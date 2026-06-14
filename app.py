from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import urllib.request
import json
import ssl
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///geno_goals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS DE BASE DE DATOS ---
class Objetivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class Auditoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(10), default=lambda: datetime.utcnow().strftime('%Y-%m-%d'))
    horas_codigo = db.Column(db.Float, default=0.0)
    millas_caminadas = db.Column(db.Float, default=0.0)
    videos_publicados = db.Column(db.Integer, default=0)
    ingresos_usd = db.Column(db.Float, default=0.0)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    pitch_personalizado = db.Column(db.Text, nullable=True)

with app.app_context():
    db.create_all()

# --- RUTAS ---
@app.route('/')
def index():
    todos_los_objetivos = Objetivo.query.order_by(Objetivo.fecha.desc()).all()
    historial = Auditoria.query.order_by(Auditoria.id.desc()).all()
    todos_los_leads = Lead.query.order_by(Lead.id.desc()).all()
    
    try:
        url = "https://api.coindesk.com/v1/bpi/currentprice.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        contexto_seguro = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=contexto_seguro, timeout=5) as response:
            datos = json.loads(response.read().decode())
            btc_usd = datos['bpi']['USD']['rate']
    except Exception:
        btc_usd = "Error de enlace externo"

    return render_template('index.html', objetivos=todos_los_objetivos, auditorias=historial, btc_price=btc_usd, leads=todos_los_leads)

@app.route('/agregar', methods=['POST'])
def agregar():
    texto = request.form.get('contenido')
    if texto:
        nuevo = Objetivo(contenido=texto)
        db.session.add(nuevo)
        db.session.commit()
    return redirect('/')

@app.route('/auditar', methods=['POST'])
def auditar():
    nueva = Auditoria(
        horas_codigo=float(request.form.get('horas_codigo', 0)),
        millas_caminadas=float(request.form.get('millas_caminadas', 0)),
        videos_publicados=int(request.form.get('videos_publicados', 0)),
        ingresos_usd=float(request.form.get('ingresos_usd', 0))
    )
    db.session.add(nueva)
    db.session.commit()
    return redirect('/')

@app.route('/crear_lead', methods=['POST'])
def crear_lead():
    empresa = request.form.get('empresa')
    contacto = request.form.get('contacto')
    email = request.form.get('email')
    
    pitch = f"Hi {contacto},\n\nI noticed {empresa} could automate its data workflow. I built a custom Python integration that saves up to 10 hours a week on operations. Let me know if you have 5 minutes this week to scale your system.\n\nBest,\nEddie"
    
    nuevo_lead = Lead(empresa=empresa, contacto=contacto, email=email, pitch_personalizado=pitch)
    db.session.add(nuevo_lead)
    db.session.commit()
    return redirect('/')

@app.route('/minar', methods=['POST'])
def minar():
    target_url = request.form.get('target_url')
    if not target_url:
        return redirect('/')
    
    try:
        if not target_url.startswith('http'):
            target_url = 'https://' + target_url
            
        req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
        contexto_seguro = ssl._create_unverified_context()
        
        with urllib.request.urlopen(req, context=contexto_seguro, timeout=8) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        emails_encontrados = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
        emails_unicos = list(dict.fromkeys(emails_encontrados))
        
        # Filtro de proveedores genéricos
        lista_basura = ['gmail', 'yahoo', 'hotmail', 'outlook', 'live', 'icloud', 'msn', 'aol']
        
        for email in emails_unicos:
            if any(email.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.webp']):
                continue
                
            partes = email.split('@')
            usuario = partes[0].replace('.', ' ').replace('_', ' ').replace('-', ' ').title()
            dominio_completo = partes[1].split('.')
            nombre_dominio = dominio_completo[0].lower()
            
            if nombre_dominio in lista_basura:
                empresa_final = usuario
                contacto_final = "Owner"
            else:
                empresa_final = dominio_completo[0].title()
                contacto_final = usuario if usuario.strip() else "Team"
            
            empresa_final = re.sub(r'\d+', '', empresa_final).strip()
            contacto_final = re.sub(r'\d+', '', contacto_final).strip()
            
            existe = Lead.query.filter_by(email=email).first()
            if not existe:
                pitch = f"Hi {contacto_final},\n\nI noticed {empresa_final} could automate its data workflow. I built a custom Python integration that saves up to 10 hours a week on operations. Let me know if you have 5 minutes this week to scale your system.\n\nBest,\nEddie"
                nuevo_lead = Lead(empresa=empresa_final, contacto=contacto_final, email=email, pitch_personalizado=pitch)
                db.session.add(nuevo_lead)
                
        db.session.commit()
    except Exception:
        pass
        
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)