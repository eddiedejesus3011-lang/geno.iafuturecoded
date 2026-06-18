@echo off
cd /d C:\Users\eddie\flask_project
call venv\Scripts\activate.bat
set FLASK_APP=app.py
set FLASK_DEBUG=1
python -c "import sqlite3; conn=sqlite3.connect('base_datos'); cursor=conn.cursor(); cursor.execute('CREATE TABLE IF NOT EXISTS credenciales_bancarias (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, plataforma TEXT NOT NULL, llave_api TEXT, estado TEXT DEFAULT \'activo\')'); conn.commit(); conn.close(); print('[LOG INTERNO] Tabla credenciales_bancarias verificada y reparada.')"
python -m flask run --host=127.0.0.1 --port=5000
pause