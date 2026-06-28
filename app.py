from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)

app.secret_key = os.environ.get('GENO_SYSTEM_SECRET', 'geno_secret_key_pro_2026')
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

CONTRASEÑA_REAL = os.environ.get('GENO_MASTER_PASSWORD', '1234')
CONTRASEÑA_MAESTRA_HASH = generate_password_hash(CONTRASEÑA_REAL)

def init_geno_system(reset=False):
    """Limpia los datos de prueba y arranca la base de datos vacía"""
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

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    crypto_data = obtener_finanzas()
    return render_template('index.html', crypto=crypto_data)

@app.route('/registrar_ingreso', methods=['POST'])
def registrar_ingreso():
    concepto = request.form.get('concepto')
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

if __name__ == '__main__':
    # reset=True borra los datos viejos una sola vez al arrancar
    init_geno_system(reset=True)
    # Mantiene la misma IP y puerto activos para tus teléfonos
    app.run(host='0.0.0.0', port=5000, debug=True)