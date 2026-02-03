import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from collections import Counter
from pathlib import Path
from datetime import datetime

# ---------------- CONFIGURACIÓN ----------------
URL = "https://www.expansion.com/economia.html"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_NOTICIAS = 15
FRASES_RESUMEN = 3

OUTPUT_DIR = Path("/home/fabri/Documents/pruebas_webbuster/datoscsv")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- RESUMEN ----------------
def resumir_texto(texto, n_frases):
    frases = re.split(r'(?<=[.!?]) +', texto)

    palabras = re.findall(r'\w+', texto.lower())
    frecuencia = Counter(palabras)

    puntuacion = {}
    for frase in frases:
        puntuacion[frase] = sum(
            frecuencia.get(p.lower(), 0) for p in frase.split()
        )

    frases_ordenadas = sorted(puntuacion, key=puntuacion.get, reverse=True)
    return " ".join(frases_ordenadas[:n_frases])

# ---------------- OBTENER ENLACES ----------------
def obtener_links():
    print("Obteniendo enlaces de Expansión...")
    r = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("https://www.expansion.com/economia/") and href.endswith(".html"):
            links.append(href)

    # quitar duplicados, NO limitar aquí
    return list(dict.fromkeys(links))

# ---------------- SCRAPEAR NOTICIA ----------------
def scrapear_noticia(url):
    print("Procesando:", url)
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    titulo = soup.find("h1")
    cuerpo = soup.find("div", class_="ue-c-article__body")

    if not titulo or not cuerpo:
        return None

    texto = " ".join(p.get_text(strip=True) for p in cuerpo.find_all("p"))
    resumen = resumir_texto(texto, FRASES_RESUMEN)

    return {
        "medio": "Expansión",
        "titulo": titulo.get_text(strip=True),
        "resumen": resumen
    }

# ---------------- MAIN ----------------
def main():
    links = obtener_links()
    noticias = []

    for url in links:
        if len(noticias) >= MAX_NOTICIAS:
            break

        try:
            noticia = scrapear_noticia(url)
            if noticia:
                noticias.append(noticia)
            time.sleep(1)
        except Exception as e:
            print("Error:", e)

    print("Noticias válidas obtenidas:", len(noticias))

    # NO crear CSV vacío
    if not noticias:
        print("No se han encontrado noticias válidas. No se crea el CSV.")
        return

    df = pd.DataFrame(noticias)
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = OUTPUT_DIR / f"expansion_resumen_{fecha}.csv"
    df.to_csv(archivo, index=False)

    print("Scraping terminado correctamente")
    print("Archivo guardado en:", archivo)

# ---------------- EJECUCIÓN ----------------
if __name__ == "__main__":
    main()