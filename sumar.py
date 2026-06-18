from app import app, db
from datetime import datetime

class Historial(db.Model):
    __tablename__ = 'historial'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(10), nullable=False)
    horas_codigo = db.Column(db.Float, nullable=False)
    millas = db.Column(db.Float, nullable=False)
    videos = db.Column(db.Integer, nullable=False)
    usd = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()
    
    # Capturamos la fecha de hoy de forma dinámica
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    
    # 🔍 PASO CLAVE: Validar si ya existe un registro para el día de hoy
    registro_existente = Historial.query.filter_by(fecha=fecha_hoy).first()
    
    if registro_existente:
        # Si ya existe, actualizamos los datos en vez de duplicar la fila
        registro_existente.horas_codigo = 6.5
        registro_existente.millas = 15.0
        registro_existente.videos = 1
        registro_existente.usd = 120.0
        print(f"🔄 Registro del día ({fecha_hoy}) actualizado para evitar duplicados.")
    else:
        # Si es un día nuevo, se crea limpio
        nuevo_registro = Historial(
            fecha=fecha_hoy,
            horas_codigo=6.5,
            millas=15.0,
            videos=1,
            usd=120.0
        )
        db.session.add(nuevo_registro)
        print(f"⛏️ ¡Nuevo registro creado para el día ({fecha_hoy}) con éxito!")
    
    db.session.commit()