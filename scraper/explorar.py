import io
import pandas as pd
import requests

URL = "https://www.sofascore.com/es/tennis/tournament/atp/shanghai/2519#id:82375"
HEADERS = {
    "User-Agent": "FantasyTenisUPV/1.0 (proyecto universitario ATD-UPV; damofer1@upv.edu.es) python-requests"
}

r = requests.get(URL, headers=HEADERS, timeout=15)
print("Código HTTP:", r.status_code)
r.raise_for_status()   # si falla, para aquí con un error claro

tablas = pd.read_html(io.StringIO(r.text))

print(f"Tablas encontradas: {len(tablas)}")
for i, t in enumerate(tablas):
    print(f"\n--- Tabla {i} --- {t.shape}")
    print(t.head(3))