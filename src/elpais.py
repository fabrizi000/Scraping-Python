import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from collections import Counter
from pathlib import Path
from datetime import datetime

# En donde guardar la info
OUTPUT_DIR = Path("/home/alusmr/Documentos/pruebas_webbuster/datoscsv/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# CONFIGURACIÓN
URL_PORTADA = "https://elpais.com/economia/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_NOTICIAS = 10   # limitar para no ser agresivo
FRASES_RESUMEN = 3  # nº de frases del resumen

# FUNCIÓN DE RESUMEN
def resumir_texto(texto, n_frases=3):
    frases = re.split(r'(?<=[.!?]) +', texto)

    palabras = re.findall(r'\w+', texto.lower())
    frecuencia = Counter(palabras)

    puntuacion = {}
    for frase in frases:
        for palabra in frase.lower().split():
            puntuacion[frase] = puntuacion.get(frase, 0) + frecuencia.get(palabra, 0)
# GUARDAR CSV

    frases_ordenadas = sorted(puntuacion, key=puntuacion.get, reverse=True)
    resumen = " ".join(frases_ordenadas[:n_frases])

    return resumen

# SACAR LINKS DEL DÍA
print("Obteniendo enlaces...")
response = requests.get(URL_PORTADA, headers=HEADERS)
soup = BeautifulSoup(response.text, "html.parser")

links = []
for article in soup.find_all("article"):
    a = article.find("a", href=True)# GUARDAR CSV

    if a and a["href"].startswith("https://"):
        links.append(a["href"])

# eliminar duplicados y limitar
links = list(dict.fromkeys(links))[:MAX_NOTICIAS]

# SCRAPEAR Y RESUMIR
noticias = []

for url in links:
    try:
        print("Procesando:", url)
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        titulo = soup.find("h1")
        cuerpo = soup.find("div", {"data-dtm-region": "articulo_cuerpo"})

        if not titulo or not cuerpo:
            continue

        texto_completo = " ".join(
            p.get_text(strip=True) for p in cuerpo.find_all("p")
        )

        resumen = resumir_texto(texto_completo, FRASES_RESUMEN)

        noticias.append({
            "medio": "El País",
            "titulo": titulo.get_text(strip=True),
            "resumen": resumen
        })

        time.sleep(1)

    except Exception as e:
        print("Error:", e)
        continue

# GUARDAR CSV
df = pd.DataFrame(noticias)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
nombre_archivo = f"elpais_resumen_{timestamp}.csv"

ruta_salida = OUTPUT_DIR / nombre_archivo
df.to_csv(ruta_salida, index=False)

print(f"Scraping terminado correctamente")
print(f"Archivo guardado en: {ruta_salida}")