import pandas as pd
from datetime import datetime
import os

URL = "https://www.worldgovernmentbonds.com/"
CARPETA_SALIDA = "datoscsv"
os.makedirs(CARPETA_SALIDA, exist_ok=True)

# Leer todas las tablas de la página
tablas = pd.read_html(URL)

df = tablas[0]  # la tabla principal

# Guardar CSV
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
nombre_csv = os.path.join(
    CARPETA_SALIDA,
    f"world_government_bonds_{timestamp}.csv"
)

df.to_csv(nombre_csv, index=False, encoding="utf-8-sig")

print("Datos guardados en:", nombre_csv)