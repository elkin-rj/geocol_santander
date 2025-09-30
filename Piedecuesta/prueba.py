import requests
API_KEY="TU_CLAVE_NUEVA"
r = requests.get("https://api.geoapify.com/v1/geocode/search",
                 params={"text": "Piedecuesta, Santander, Colombia", "format": "json", "apiKey": API_KEY})
print(r.status_code, r.text[:200])