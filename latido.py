import os
import sqlite3
import requests

# Nos aseguramos de leer exactamente la misma base de datos que tu Flask
if os.environ.get('RENDER'):
    DB_PATH = '/tmp/database.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def latido_del_sistema():
    print("🔋 Geno se está despertando para revisar el entorno...")
    
    # Verificar si la base de datos existe antes de operar
    if not os.path.exists(DB_PATH):
        print("⚠️ La base de datos aún no ha sido inicializada por el servidor Flask.")
        return

    try:
        # 1. Conecta con una API externa para ver el precio de Bitcoin en tiempo real
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        data = response.json()
        precio_btc_actual = float(data['bitcoin']['usd'])
        print(f"📈 Precio actual de BTC obtenido: ${precio_btc_actual:,.2f} USD")
        
        # 2. Conectar a la base de datos SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 3. Leer los balances actuales de tu tesorería
        cursor.execute("SELECT btc_balance, usd_balance FROM finanzas_sistema WHERE id = 1")
        res = cursor.fetchone()
        
        if res:
            btc_balance_actual = res[0]
            usd_balance_actual = res[1]
            
            # 4. Calcular el valor real de tu Bitcoin sumado a tus dólares estáticos
            # Fórmula: Valor Total = (Tus BTC * Precio de Mercado) + Tus USD guardados
            valor_total_crypto_en_usd = btc_balance_actual * precio_btc_actual
            tesoreria_total_actualizada = valor_total_crypto_en_usd + usd_balance_actual
            
            print(f"💰 Balance en cuenta: {btc_balance_actual:.6f} BTC (${valor_total_crypto_en_usd:,.2f} USD) + ${usd_balance_actual:,.2f} USD")
            print(f"⚡ Valor de Tesorería Total Calculado: ${tesoreria_total_actualizada:,.2f} USD")
            
            # NOTA: Aquí puedes decidir si quieres guardar este histórico del 'valor total' 
            # en una nueva tabla o simplemente dejar que tu frontend lo calcule multiplicando al vuelo.
            
        else:
            print("❌ No se encontraron registros financieros con ID = 1.")
            
        conn.close()
        print("⚡ Latido completado con éxito. Geno vuelve a segundo plano.")
        
    except Exception as e:
        print(f"❌ Falló el latido debido al siguiente error: {str(e)}")

if __name__ == "__main__":
    latido_del_sistema()