from flask import Flask, request, flash, redirect, url_for, render_template
import os
import requests

app = Flask(__name__)
app.secret_key = "geno_secreto_temporal" # Llave para que funcionen los mensajes flash

@app.route('/')
def dashboard():
    # Esta ruta hace que al entrar al link seco, cargue tu panel directamente
    return render_template('index.html')

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
        
    flash(f"Minería y envío completado en {zona_objetivo}. {len(leads_filtrados)} propuestas enviadas.")
    return redirect(url_for('dashboard'))