from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import sys
import json
import pg8000  # Conector nativo para PostgreSQL

app = Flask(__name__)

app.secret_key = os.environ.get('GENO_SYSTEM_SECRET', 'geno_secret_key_pro_2026')

# --- CONEXIÓN OPTIMIZADA CON PG8000 ---
def obtener_conexion():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        try:
            url = DATABASE_URL.replace("postgres://", "").replace("postgresql://", "")
            user_pass, host_db = url.split("@")
            user, password = user_pass.split(":")
            host_port, database = host_db.split("/")
            host = host_port.split(":")[0]
            port = int(host_port.split(":")[1]) if ":" in host_port else 5432
            
            return pg8000.connect(user=user, password=password, host=host, port=port, database=database)
        except Exception as e:
            raise Exception(f"Error al procesar la DATABASE_URL: {e}")
    else:
        raise Exception("Falta configurar la URL de la base de datos PostgreSQL.")

def init_geno_system():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas_conexion (
            id SERIAL PRIMARY KEY,
            remitente TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS finanzas_sistema (
            id INTEGER PRIMARY KEY,
            btc_balance REAL DEFAULT 0.000000,
            usd_balance REAL DEFAULT 0.00
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM finanzas_sistema")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO finanzas_sistema (id, btc_balance, usd_balance) VALUES (1, 0.000000, 0.00)")
        
    conn.commit()
    conn.close()

def obtener_finanzas():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT btc_balance, usd_balance FROM finanzas_sistema WHERE id = 1")
        res = cursor.fetchone()
        conn.close()
        if res:
            return {'btc': f"{res[0]:.6f}", 'usd': f"{res[1]:,.2f}"}
    except Exception as e:
        print(f"Error al traer finanzas: {e}")
    return {'btc': "0.000000", 'usd': "0.00"}

# --- RUTAS DE LA INTERFAZ ---
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    crypto_data = obtener_finanzas()
    return render_template('index.html', crypto=crypto_data)

@app.route('/registrar_ingreso', methods=['POST'])
def registrar_ingreso():
    try:
        monto_usd = float(request.form.get('monto_usd', 0) or 0)
        monto_btc = float(request.form.get('monto_btc', 0) or 0)
        
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE finanzas_sistema 
            SET btc_balance = btc_balance + %s, usd_balance = usd_balance + %s 
            WHERE id = 1
        """, (monto_btc, monto_usd))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error manual: {e}")
    return redirect(url_for('dashboard'))

@app.route('/preguntar_geno', methods=['POST'])
def preguntar_geno():
    user_message = request.form.get('mensaje')
    api_key = os.environ.get("AI_SECRET_KEY")

    if not user_message:
        return jsonify({"respuesta": "No enviaste ningún mensaje."}), 400
    if not api_key:
        return jsonify({"respuesta": "Error: Falta AI_SECRET_KEY"}), 500
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Eres Geno, el cerebro financiero autónomo. Devuelve SIEMPRE JSON:\n"
                        "{\n"
                        "  \"explicacion\": \"Tu respuesta amigable aquí\",\n"
                        "  \"monto_usd\": 0.00,\n"
                        "  \"monto_btc\": 0.000000\n"
                        "}"
                    )
                },
                {"role": "user", "content": user_message}
            ]
        )
        
        data_json = json.loads(response.choices[0].message.content)
        texto_explicacion = data_json.get("explicacion", "Procesado.")
        monto_usd = float(data_json.get("monto_usd", 0))
        monto_btc = float(data_json.get("monto_btc", 0))
        
        if monto_usd > 0 or monto_btc > 0:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE finanzas_sistema 
                SET btc_balance = btc_balance + %s, usd_balance = usd_balance + %s 
                WHERE id = 1
            """, (monto_btc, monto_usd))
            conn.commit()
            conn.close()
            texto_explicacion += f" 🚀 [Guardado Permanente: +${monto_usd:,.2f} USD]"

        return jsonify({"respuesta": texto_explicacion})
    except Exception as e:
        return jsonify({"respuesta": f"Error: {str(e)}"}), 500

try:
    init_geno_system()
except Exception as e:
    print(f"Aviso de inicio de BD: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)