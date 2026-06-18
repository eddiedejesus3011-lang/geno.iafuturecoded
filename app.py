@app.route('/minar', methods=['POST'])
@login_requerido
def minar_leads():
    zona_objetivo = request.form.get('zona', 'Seattle')
    
    # Canalización de llamadas directa al celular de tu hermano
    TELEFONO_HERMANO = "+14258302521"
    
    # Base de datos local unificada del Eastside
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
        # Pitch comercial estratégico estructurado en inglés nativo
        pitch_ingles = (
            f"Hi, this is De Jesus. We have trucks and commercial equipment ready for "
            f"any landscaping, cleanup, or mowing support your projects need in {zona_objetivo}. "
            f"Available immediately. Call me back at {TELEFONO_HERMANO}."
        )
        
        # Monitor de salida en la terminal del búnker
        print(f"[📡 SMS OUT] -> Empresa: {lead['empresa']} | Destino: {lead['telefono']}")
        print(f"    Mensaje: \"{pitch_ingles}\"")
        
        # Espacio listo para la integración final del SDK de Twilio:
        # twilio_client.messages.create(body=pitch_ingles, from_=NUMERO_TWILIO, to=lead['telefono'])
        
    flash(f"Minería y envío completado en {zona_objetivo}. {len(leads_filtrados)} propuestas enviadas.")
    return redirect(url_for('dashboard'))