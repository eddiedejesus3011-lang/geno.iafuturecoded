import os
import requests
import imaplib
import threading
import time
from functools import wraps  # <-- SOLUCIÓN AL FALLO CRÍTICO DE IMPORTACIÓN
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# LLAVE SECRETA PARA MANEJAR SESIONES SEGURAS
app.secret_key = os.environ.get('SECRET_KEY', 'geno_secret_key_restringida_2026')

# CONFIGURACIÓN CENTRALIZADA - GENO.IAFUTURECODED
EMAIL_USER = os.environ.get('EMAIL_USER', 'eddiedejesus3011@gmail.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', 'vdpkaklsshscgcxk')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///geno_control.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELOS DE BASE DE DATOS
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Auditoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(10), nullable=False)
    horas_codigo = db.Column(db.Float, default=0.0)
    millas = db.Column(db.Float, default=0.0)
    videos = db.Column(db.Integer, default=0)
    usd = db.Column(db.Float, default=0.0)
    objetivos = db.Column(db.Text, nullable=True)

class ListaNegra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    correo_remitente = db.Column(db.String(255), unique=True, nullable=False)

class BalanceBTC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cantidad_btc = db.Column(db.Float, default=0.0)  
    usd_invertido = db.Column(db.Float, default=0.0) 
    fecha = db.Column(db.String(10), nullable=False)

# CREACIÓN CONTROLADA DE TABLAS
with app.app_context():
    db.create_all()
    if not Usuario.query.filter_by(username='eddie').first():
        hashed_password = generate_password_hash('Geno2029!', method='pbkdf2:sha256')
        usuario_maestro = Usuario(username='eddie', password_hash=hashed_password)
        db.session.add(usuario_maestro)
        db.session.commit()

# LÓGICA DE AUTOMATIZACIÓN (Gmail & BTC)
def obtener_precio_btc_float():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return float(response.json()['bitcoin']['usd'])
        return 0.0
    except Exception:
        return 0.0

def ejecutar_purga_silenciosa():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        with app.app_context():
            correos_lista_negra = [c.correo_remitente for c in ListaNegra.query.all()]
        for correo in correos_lista_negra:
            status, mensajes = mail.search(None, f'FROM "{correo}"')
            if status == "OK" and mensajes[0]:
                id_lista = mensajes[0].split()
                if id_lista:
                    for num in id_lista:
                        mail.store(num, '+FLAGS', '\\Deleted')
                    mail.expunge()
        mail.logout()
    except Exception as e:
        print(f"[-] Error en purga: {str(e)}")

# DECORADOR INTEGRADO Y SEGURO
def login_requerido(f):
    @wraps(f)
    def funcion_decorada(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return funcion_decorada

# RUTAS DE ACCESO RESTRINGIDO
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['usuario'] = user.username
            session.permanent = True
            return redirect(url_for('dashboard'))
        else:
            return "<h3>Acceso denegado: Credenciales Erróneas.</h3>", 401
            
    # Formulario de emergencia directo si no encuentra la plantilla independiente
    return '''
        <body style="background:#07080b; color:white; font-family:sans-serif; display:flex; align-items:center; justify-content:center; height:100vh; margin:0;">
            <form method="POST" style="background:#10121a; color:white; padding:30px; max-width:320px; width:100%; border-radius:12px; border:1px solid #1b1f2d;">
                <h4 style="text-align:center; color:#64748b; margin-top:0;">🔐 GENO_CONTROL PANEL</h4>
                <label style="font-size:10px; color:#64748b; display:block; margin-bottom:4px;">USUARIO</label>
                <input type="text" name="username" placeholder="eddie" required style="width:100%; padding:10px; background:#030406; border:1px solid #1b1f2d; color:white; margin-bottom:15px; border-radius:6px;">
                <label style="font-size:10px; color:#64748b; display:block; margin-bottom:4px;">CONTRASEÑA</label>
                <input type="password" name="password" placeholder="••••••••" required style="width:100%; padding:10px; background:#030406; border:1px solid #1b1f2d; color:white; margin-bottom:20px; border-radius:6px;">
                <button type="submit" style="width:100%; background:#6366f1; color:white; border:none; padding:12px; font-weight:bold; border-radius:6px; cursor:pointer;">CONECTAR SISTEMA</button>
            </form>
        </body>
    '''

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# DASHBOARD CENTRAL PROTEGIDO
@app.route('/', methods=['GET', 'POST'])
@login_requerido
def dashboard():
    registros = Auditoria.query.order_by(Auditoria.id.desc()).all()
    lista_negra = ListaNegra.query.all()
    
    precio_actual = obtener_precio_btc_float()
    transacciones_btc = BalanceBTC.query.all()
    
    total_btc_poseido = sum(t.cantidad_btc for t in transacciones_btc)
    total_usd_invertido = sum(t.usd_invertido for t in transacciones_btc)
    valor_actual_usd = total_btc_poseido * precio_actual
    
    btc_status = f"${precio_actual:,.2f} USD" if precio_actual > 0 else "Desconectado"
    balance_crypto = {
        'total_btc': f"{total_btc_poseido:.8f} BTC",
        'invertido': f"${total_usd_invertido:,.2f} USD",
        'valor_actual': f"${valor_actual_usd:,.2f} USD",
        'rendimiento': f"{((valor_actual_usd - total_usd_invertido) / total_usd_invertido * 100):+.2f}%" if total_usd_invertido > 0 else "0.00%"
    }
    
    return render_template(
        'index.html', 
        registros=registros, 
        historial=registros, 
        lista_negra=lista_negra, 
        btc_price=btc_status,
        btc_status=btc_status,
        balance_crypto=balance_crypto,
        objetivos=[] 
    )

@app.route('/registrar_compra_btc', methods=['POST'])
@login_requerido
def registrar_compra_btc():
    usd_gastados = float(request.form.get('usd_invertido', 0) or 0)
    cantidad_btc_real = float(request.form.get('cantidad_btc', 0) or 0)
    
    if usd_gastados > 0 and cantidad_btc_real > 0:
        nueva_compra = BalanceBTC(
            cantidad_btc=cantidad_btc_real,
            usd_invertido=usd_gastados,
            fecha=time.strftime("%Y-%m-%d")
        )
        db.session.add(nueva_compra)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/auditar', methods=['POST'])
@login_requerido
def auditar():
    nueva_auditoria = Auditoria(
        fecha=request.form.get('fecha'),
        horas_codigo=float(request.form.get('horas_codigo', 0) or 0),
        millas=float(request.form.get('millas', 0) or 0),
        videos=int(request.form.get('videos', 0) or 0),
        usd=float(request.form.get('usd', 0) or 0),
        objetivos=request.form.get('objetivos', '')
    )
    db.session.add(nueva_auditoria)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/ejecutar_purga')
@login_requerido
def purga_manual():
    hilo = threading.Thread(target=ejecutar_purga_silenciosa)
    hilo.start()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)