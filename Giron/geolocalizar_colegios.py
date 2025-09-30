import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
import os

# ---------- CONFIGURACIÓN ----------
INPUT_FILE  = "Colegios_Giron_Geolocalizacion_Plantilla.xlsx"
OUTPUT_FILE = "Colegios_Giron_Geolocalizados.xlsx"
chunk_size  = 20        # Número de filas a procesar por lote
timeout_s   = 20        # Tiempo máximo de espera por solicitud (segundos)
delay_s     = 1         # Pausa entre solicitudes para no saturar Nominatim
# -----------------------------------

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"No se encuentra el archivo: {INPUT_FILE}")

# Carga del archivo original
df = pd.read_excel(INPUT_FILE)

# Si ya existe un archivo parcial, reanudar desde allí
if os.path.exists(OUTPUT_FILE):
    print(f"🔄 Reanudando desde archivo existente: {OUTPUT_FILE}")
    df_out = pd.read_excel(OUTPUT_FILE)
else:
    df_out = df.copy()
    df_out["latitude"] = None
    df_out["longitude"] = None

# Configurar geolocalizador
geolocator = Nominatim(user_agent="colegios_giron")
geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=delay_s,
    max_retries=3,
    error_wait_seconds=5,
    swallow_exceptions=False
)

# Identificar filas pendientes (sin coordenadas)
pending_idx = df_out[df_out["latitude"].isna()].index

print(f"Total de direcciones pendientes: {len(pending_idx)}")

# Procesar en lotes
for start in range(0, len(pending_idx), chunk_size):
    end = start + chunk_size
    batch = pending_idx[start:end]
    print(f"\nProcesando filas {start + 1} a {min(end, len(pending_idx))}…")

    for i in batch:
        direccion = f"{df_out.loc[i, 'direccion']}, Girón, Santander, Colombia"
        try:
            location = geocode(direccion, timeout=timeout_s)
            if location:
                df_out.at[i, "latitude"] = location.latitude
                df_out.at[i, "longitude"] = location.longitude
                print(f"✓ {direccion} → {location.latitude}, {location.longitude}")
            else:
                print(f"⚠️  No se encontró: {direccion}")
        except Exception as e:
            print(f"❌ Error en '{direccion}': {e}")

        # Pausa ligera por cortesía (RateLimiter ya incluye min_delay_seconds)
        time.sleep(0.5)

    # Guardar progreso después de cada lote
    df_out.to_excel(OUTPUT_FILE, index=False)
    print(f"💾 Progreso guardado: {OUTPUT_FILE}")

print("\n✅ Geocodificación finalizada.")
print(f"Archivo final: {OUTPUT_FILE}")
