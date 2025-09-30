import pandas as pd
import requests
import time
from tqdm import tqdm

# ======= CONFIGURACIÓN =======
API_KEY = "cbbb35226537438f921fc0081fac011e"   # <-- tu clave Geoapify
INPUT_FILE = "Colegios_Floridablanca_Geolocalizacion_Plantilla.xlsx"  # Archivo con columnas: nombre, direccion, latitud, longitud
OUTPUT_FILE = "Colegios_Floridablanca_Geolocalizados.xlsx"

print(f"Usando API_KEY: {API_KEY}")

# ======= CARGAR DATOS =======
df = pd.read_excel(INPUT_FILE)

# Si no existen, crea las columnas de latitud/longitud
for col in ["latitud", "longitud"]:
    if col not in df.columns:
        df[col] = None

# ======= SELECCIONAR REGISTROS PENDIENTES =======
pendientes = df[df["latitud"].isna() | df["longitud"].isna()].index
print(f"Total de direcciones pendientes: {len(pendientes)}")

# ======= GEOCODIFICACIÓN =======
for i in tqdm(pendientes, desc="Geocodificando"):
    direccion = f"{df.loc[i,'direccion']}, Piedecuesta, Santander, Colombia"
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {"text": direccion, "apiKey": API_KEY}

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Verifica que exista la clave 'features' y que no esté vacía
            if "features" in data and data["features"]:
                coords = data["features"][0]["geometry"]["coordinates"]
                df.loc[i, "longitud"] = coords[0]
                df.loc[i, "latitud"] = coords[1]
            else:
                print(f"⚠️  Sin resultados para: {direccion}")
                print("Respuesta completa:", data)  # Para diagnosticar
        else:
            print(f"❌ Error {r.status_code} en {direccion}")
            print("URL:", r.url)
            print("Respuesta completa:", r.text)
    except requests.exceptions.RequestException as e:
        print(f"🚨 Error de red en {direccion}: {e}")

    # Pausa de cortesía para no exceder límites de la API
    time.sleep(1)

# ======= GUARDAR RESULTADOS =======
df.to_excel(OUTPUT_FILE, index=False)
print(f"✅ Geocodificación finalizada. Archivo guardado como: {OUTPUT_FILE}")
