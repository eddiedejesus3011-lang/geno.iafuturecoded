import os
import requests
import imaplib
import threading
import time
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# CONFIGURACIÓN CENTRALIZADA - GENO.IAFUTURECODED
EMAIL_USER = "eddiedejesus3011@gmail.com"
EMAIL_PASS = "vdpkaklsshscgcxk"

# Configuración de base de datos persistente (Render o SQLite local de respaldo)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sistema.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELOS DE BASE DE DATOS (Se crean automáticamente)
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

# LOGICA DE AUTOMATIZACIÓN (Gmail & BTC)
def obtener_precio_btc():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return f"${response.json()['bitcoin']['usd']:,.2f} USD"
        return "Línea ocupada"
    except Exception:
        return "Desconectado"

def ejecutar_purga_silenciosa():
    try:
        print("[+] [geno.iafuturecoded] Iniciando ciclo de limpieza automática...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        
        # Jalar lista negra desde la Base de Datos
        with app.app_context():
            correos_lista_negra = [c.correo_remitente for c in ListaNegra.query.all()]
        
        for correo in correos_lista_negra:
            status, mensajes = mail.search(None, f'FROM "{correo}"')
            if status == "OK" and mensajes[0]:
                id_lista = mensajes[0].split()
                if id_lista:
                    print(f"[+] [geno.iafuturecoded] Eliminando {len(id_lista)} correos de: {correo}")
                    for num in id_lista:
                        mail.store(num, '+FLAGS', '\\Deleted')
                    mail.expunge()
        mail.logout()
        print("[+] [geno.iafuturecoded] Purga silenciosa completada con éxito.")
    except Exception as e:
        print(f"[-] Error en purga: {str(e)}")

# RUTAS DEL DASHBOARD INTERACTIVO
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Accion 1: Registrar Auditoría
        if action == 'registrar_auditoria':
            nueva_auditoria = Auditoria(
                fecha=request.form.get('fecha'),
                horas_codigo=float(request.form.get('horas_codigo', 0)),
                millas=float(request.form.get('millas', 0)),
                videos=int(request.form.get('videos', 0)),
                usd=float(request.form.get('usd', 0)),
                objetivos=request.form.get('objetivos')
            )
            db.session.add(nueva_auditoria)
            db.session.commit()
            
        # Accion 2: Bloquear Correo en Lista Negra
        elif action == 'agregar_lista_negra':
            correo = request.form.get('correo_bloquear')
            if correo:
                # Evitar duplicados
                existente = ListaNegra.query.filter_by(correo_remitente=correo).first()
                if not existente:
                    nuevo_bloqueo = ListaNegra(correo_remitente=correo)
                    db.session.add(nuevo_bloqueo)
                    db.session.commit()
                    
        return redirect(url_for('dashboard'))
    
    registros = Auditoria.query.order_by(Auditoria.id.desc()).all()
    lista_negra = ListaNegra.query.all()
    btc_status = obtener_precio_btc()
    return render_template('index.html', registros=registros, lista_negra=lista_negra, btc_status=btc_status)

@app.route('/ejecutar_purga')
def purga_manual():
    # Permite disparar la limpieza de Gmail con un toque desde tu iPhone
    hilo = threading.Thread(target=ejecutar_purga_silenciosa)
    hilo.start()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)