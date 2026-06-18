from flask import Flask, request, flash, redirect, url_for, render_template
import os
import requests

app = Flask(__name__)
app.secret_key = "geno_secreto_temporal"

# Configuración del búnker financiero de geno.iafuturecoded
DIRECCION_BITCOIN = "3CSf4...yvsRW"

@app.route('/')
def dashboard():
    # Simulamos datos de rendimiento de la tesorería del sistema
    ingresos_usd_estimados = 1250.00
    porcentaje_acumulacion = 1.00  # 100% destinado a la billetera de respaldo
    
    contexto = {
        "direccion_btc": DIRECCION_BITCOIN,
        "usd_totales": ingresos_usd_estimados,
        "btc_simulados": ingresos_usd_estimados / 64101.81  # Cálculo basado en el valor actual
    }
    return render_template('index.html', **contexto)

@app.route('/minar', methods=['POST'])
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
        
    print(f"[+] Minador activado en zona: {zona_objetivo}. Procesando {len(leads_filtrados)} objetivos...")
    
    for lead in leads_filtrados:
        pitch_ingles = (
            f"Hi, this is De Jesus with Geno Services. We specialize in commercial-grade "
            f"landscaping and site cleanups for high-end projects in {zona_objetivo}. "
            f"Fully equipped and available for immediate dispatch. Direct line: {TELEFONO_HERMANO}."
        )
        print(f"[📡 SMS OUT] -> Empresa: {lead['empresa']} | Destino: {lead['telefono']}")
        print(f"    Mensaje: \"{pitch_ingles}\"")
        
    flash(f"Minería completada en {zona_objetivo}. {len(leads_filtrados)} propuestas procesadas.")
    return redirect(url_for('dashboard'))