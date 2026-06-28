from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import sys
import json

app = Flask(__name__)

app.secret_key = os.environ.get('GENO_SYSTEM_SECRET', 'geno_secret_key_pro_2026')

# Parche de permisos de escritura para Render
if os.environ.get('RENDER'):
    DB_PATH = '/tmp/database.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def init_geno_system(reset=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if reset:
        cursor.execute("DROP TABLE IF EXISTS notas_conexion")
        cursor.execute("DROP TABLE IF EXISTS finanzas_sistema")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas_conexion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remitente TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS finanzas_sistema (
            id INTEGER PRIMARY KEY,
            btc_balance REAL,
            usd_balance REAL
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM finanzas_sistema")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO finanzas_sistema (id, btc_balance, usd_balance) VALUES (1, 0.000000, 0.00)")
        
    conn.commit()
    conn.close()

def obtener_finanzas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT btc_balance, usd_balance FROM finanzas_sistema WHERE id = 1")
    res = cursor.fetchone()
    conn.close()
    if res:
        return {'btc': f"{res[0]:.6f}", 'usd': f"{res[1]:,.2f}"}
    return {'btc': "0.000000", 'usd': "0.00"}

# --- RUTA PRINCIPAL ---
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    try:
        crypto_data = obtener_finanzas()
        return render_template('index.html', crypto=crypto_data)
    except Exception as e:
        try:
            return render_template('login.html', crypto=crypto_data)
        except Exception as e_secundario:
            return f"<h1>Error de Diagnóstico en Geno:</h1><p>index.html falló porque: {str(e)}</p><p>login.html falló porque: {str(e_secundario)}</p>"

@app.route('/registrar_ingreso', methods=['POST'])
def registrar_ingreso():
    try:
        monto_usd = float(request.form.get('monto_usd', 0) or 0)
        monto_btc = float(request.form.get('monto_btc', 0) or 0)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE finanzas_sistema 
            SET btc_balance = btc_balance + ?, usd_balance = usd_balance + ? 
            WHERE id = 1
        """, (monto_btc, monto_usd))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al registrar ingreso manual: {e}")
        
    return redirect(url_for('dashboard'))

# --- INTERFAZ CON EL CEREBRO DE GEN3AI + PARSER AUTÓNOMO ---
@app.route('/preguntar_geno', methods=['POST'])
def preguntar_geno():
    user_message = request.form.get('mensaje')
    api_key = os.environ.get("AI_SECRET_KEY")

    if not user_message:
        return jsonify({"respuesta": "No enviaste ningún mensaje."}), 400
        
    if not api_key:
        return jsonify({"respuesta": "Error: La variable de entorno AI_SECRET_KEY no está configurada en la consola."}), 500
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Le ordenamos explícitamente responder en un formato JSON estricto
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Eres Geno, el cerebro financiero autónomo de iafuturecoded. "
                        "Analiza el mensaje del usuario y devuelve SIEMPRE un objeto JSON con esta estructura exacta:\n"
                        "{\n"
                        "  \"explicacion\": \"Tu respuesta conversacional o saludo amigable aquí\",\n"
                        "  \"monto_usd\": 0.00,  // Monto extraído si reporta ganancias/ingresos en dólares, si no 0\n"
                        "  \"monto_btc\": 0.000000 // Monto extraído si reporta transacciones en Bitcoin, si no 0\n"
                        "}"
                    )
                },
                {"role": "user", "content": user_message}
            ]
        )
        
        # --- PARSER JSON ---
        raw_content = response.choices[0].message.content
        data_json = json.loads(raw_content) # Convertimos el texto de la IA en un diccionario de Python
        
        texto_explicacion = data_json.get("explicacion", "Procesado correctamente.")
        monto_usd = float(data_json.get("monto_usd", 0 or 0))
        monto_btc = float(data_json.get("monto_btc", 0 or 0))
        
        # Si la IA detectó dinero en el comando de texto, lo inyectamos directo en la BD
        if monto_usd > 0 or monto_btc > 0:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE finanzas_sistema 
                SET btc_balance = btc_balance + ?, usd_balance = usd_balance + ? 
                WHERE id = 1
            """, (monto_btc, monto_usd))
            conn.commit()
            conn.close()
            texto_explicacion += f" 🚀 [Auto-Inyección Exitosa: +${monto_usd:,.2f} USD | +₿{monto_btc:.6f} BTC agregados a la tesorería]"

        return jsonify({"respuesta": texto_explicacion})
        
    except Exception as e:
        return jsonify({"respuesta": f"Ocurrió un error en el cerebro o base de datos: {str(e)}"}), 500

# Asegurar la creación de la BD en producción
init_geno_system(reset=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)