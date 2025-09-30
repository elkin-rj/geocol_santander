import pandas as pd
import requests
import time
from tqdm import tqdm
import os

# === CONFIGURACIÓN ===
API_KEY = "30c9f36723754bcb9100e4f54e82f897"   # <-- Pega aquí tu API key de Geoapify
ENTRADA = "Colegios_Giron_Geolocalizacion_Plantilla.xlsx"
SALIDA  = "Colegios_Giron_Geolocalizados.xlsx"

# === CARGAR DATOS ===
df = pd.read_excel(ENTRADA)

# Si ya existe archivo de salida, reanudar desde ahí
if os.path.exists(SALIDA):
    print(f"🔄 Reanudando desde: {SALIDA}")
    df_out = pd.read_excel(SALIDA)
else:
    df_out = df.copy()
    # Crear columnas latitud/longitud si no existen
    if "latitud" not in df_out.columns:
        df_out["latitud"] = None
    if "longitud" not in df_out.columns:
        df_out["longitud"] = None

# Filas pendientes: donde latitud está vacía
pendientes = df_out[df_out["latitud"].isna()].index
print(f"Total de direcciones pendientes: {len(pendientes)}")

# === GEOLOCALIZAR ===
for i in tqdm(pendientes, desc="Geocodificando", unit="fila"):
    # Ajusta el nombre de la columna que contiene la dirección
    direccion = f"{df_out.loc[i, 'direccion']}, Girón, Santander, Colombia"

    url = (
        "https://api.geoapify.com/v1/geocode/search"
        f"?text={requests.utils.quote(direccion)}&apiKey={API_KEY}"
    )

    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()

        if data["features"]:
            coords = data["features"][0]["geometry"]["coordinates"]
            # Geoapify devuelve [long, lat]
            df_out.at[i, "longitud"] = coords[0]
            df_out.at[i, "latitud"]  = coords[1]
        else:
            print(f"⚠️  No se encontró: {direccion}")

    except Exception as e:
        print(f"⚠️  Error en {direccion}: {e}")

    # Pausa de cortesía
    time.sleep(1)

# === GUARDAR RESULTADO ===
df_out.to_excel(SALIDA, index=False)
print(f"✅ Geocodificación finalizada. Archivo generado: {SALIDA}")
