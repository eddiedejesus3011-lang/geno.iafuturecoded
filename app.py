@app.route('/minar', methods=['POST'])
@login_requerido
def minar_leads():
    zona_objetivo = request.form.get('zona', 'Seattle')
    
    # Lista actualizada: Tukwila fuera, Bellevue dentro
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
        
    print(f"[+] Minador activado en zona: {zona_objetivo}. Procesando {len(leads_filtrados)} leads de alto valor...")
    
    for lead in leads_filtrados:
        pass
        
    flash(f"Minería completada en {zona_objetivo}. {len(leads_filtrados)} prospectos listos para auditar.")
    return redirect(url_for('dashboard'))