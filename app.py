from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import sys

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

# --- RUTA PRINCIPAL CON RASTREO DE ERRORES INTELIGENTE ---
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    try:
        crypto_data = obtener_finanzas()
        # Intentamos cargar index.html primero
        return render_template('index.html', crypto=crypto_data)
    except Exception as e:
        # Si falla, intentamos con login.html por si acaso
        try:
            return render_template('login.html', crypto=crypto_data)
        except Exception as e_secundario:
            # Si ambos fallan, te escupimos el error real en la cara para saber qué pasa
            return f"<h1>Error de Diagnóstico en Geno:</h1><p>index.html falló porque: {str(e)}</p><p>login.html falló porque: {str(e_secundario)}</p>"

@app.route('/registrar_ingreso', methods=['POST'])
def registrar_ingreso():
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
    return redirect(url_for('dashboard'))

# Asegurar la creación de la BD en producción
init_geno_system(reset=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)