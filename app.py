from flask import Flask, request, flash, redirect, url_for, render_template, session
from functools import wraps
import os

app = Flask(__name__)
# Usamos una clave fuerte para encriptar las sesiones del búnker
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "bunker_seguro_geno_2026")

# Definimos tu contraseña de acceso táctico
ACCESO_MASTERMIND = "GenoCoded2026!"
DIRECCION_BITCOIN = "3CSf4...yvsRW"

# Decorador de seguridad estricto
def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if not session.get('autenticado'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorada

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password_ingresada = request.form.get('password')
        if password_ingresada == ACCESO_MASTERMIND:
            session['autenticado'] = True
            return redirect(url_for('dashboard'))
        else:
            flash("Acceso denegado. Credencial incorrecta.")
    return '''
        <div style="background:#111; color:#fff; height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center; font-family:sans-serif;">
            <form method="POST" style="background:#222; padding:30px; border-radius:8px; box-shadow:0 4px 15px rgba(0,0,0,0.5);">
                <h3 style="margin-top:0; color:#ff9900;">geno.iafuturecoded</h3>
                <p style="color:#aaa; font-size:14px;">Introduce la clave de acceso al sistema:</p>
                <input type="password" name="password" placeholder="Contraseña" style="padding:10px; width:100%; margin-bottom:15px; border:1px solid #444; background:#333; color:#fff; border-radius:4px;"><br>
                <button type="submit" style="padding:10px; width:100%; background:#ff9900; color:#000; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Entrar al Sistema</button>
            </form>
        </div>
    '''

@app.route('/logout')
def logout():
    session.pop('autenticado', None)
    return redirect(url_for('login'))

@app.route('/')
@login_requerido
def dashboard():
    ingresos_usd_estimados = 1250.00
    contexto = {
        "direccion_btc": DIRECCION_BITCOIN,
        "usd_totales": ingresos_usd_estimados,
        "btc_simulados": ingresos_usd_estimados / 64101.81
    }
    return render_template('index.html', **contexto)

@app.route('/minar', methods=['POST'])
@login_requerido
def minar_leads():
    zona_objetivo = request.form.get('zona', 'Seattle')
    TELEFONO_HERMANO = "+14258302521"
    
    prospectos_encontrados = [
        {"empresa": "WA Premium Builders", "telefono": "206-555-0142", "direccion": "Bellevue, WA"},
        {"empresa": "Cascade Property Management", "telefono": "253-555-0199", "direccion": "Tacoma, WA"},
        {"empresa": "Bellevue Corporate Gardens", "telefono": "425-555-0855", "direccion": "Bellevue, WA"},
        {"empresa": "Redmond Tech Estates", "telefono": "425-555-0322", "direccion": "Redmond, WA"},
        {"empresa": "Kirkland Waterfront Condos", "telefono": "425-555-0481", "direccion": "Kirkland, WA"}
    ]
    
    leads_filtrados = [l for l in prospectos_encontrados if zona_objetivo.lower() in l['direccion'].lower()]
    if not leads_filtrados:
        leads_filtrados = prospectos_encontrados
        
    for lead in leads_filtrados:
        pitch_ingles = (
            f"Hi, this is De Jesus with Geno Services. We specialize in commercial-grade "
            f"landscaping and site cleanups for high-end projects in {zona_objetivo}. "
            f"Fully equipped and available for immediate dispatch. Direct line: {TELEFONO_HERMANO}."
        )
        print(f"[📡 SMS OUT] -> {lead['empresa']}")
        
    flash(f"Minería completada en {zona_objetivo}.")
    return redirect(url_for('dashboard'))