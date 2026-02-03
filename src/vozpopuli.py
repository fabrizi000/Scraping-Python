import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from collections import Counter
from pathlib import Path
from datetime import datetime

# ---------------- CONFIGURACIÓN ----------------
URL = "https://www.vozpopuli.com/economia/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_NOTICIAS = 15
FRASES_RESUMEN = 3
PAUSA = 1

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
    print("Obteniendo enlaces de Vozpópuli...")
    r = requests.get(URL, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]

        # enlaces relativos reales de Vozpópuli (economía)
        if href.startswith("/economia/") and href.endswith(".html"):
            enlace_completo = "https://www.vozpopuli.com" + href
            links.append(enlace_completo)

    links = list(dict.fromkeys(links))
    print("Enlaces encontrados:", len(links))
    return links

# ---------------- SCRAPEAR NOTICIA ----------------
def scrapear_noticia(url):
    print("Procesando:", url)
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    titulo = soup.find("h1")

    # selector REAL del cuerpo en Vozpópuli
    cuerpo = (
        soup.find("div", class_="vp-article-content")
        or soup.find("div", class_="article-content")
        or soup.find("article")
    )

    if not titulo or not cuerpo:
        return None

    texto = " ".join(p.get_text(strip=True) for p in cuerpo.find_all("p"))

    if not texto.strip():
        return None

    resumen = resumir_texto(texto, FRASES_RESUMEN)

    return {
        "medio": "Vozpópuli",
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
            time.sleep(PAUSA)
        except Exception as e:
            print("Error:", e)

    print("Noticias válidas obtenidas:", len(noticias))

    # NO crear CSV vacío
    if not noticias:
        print("No se han encontrado noticias válidas. No se crea el CSV.")
        return

    df = pd.DataFrame(noticias)
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = OUTPUT_DIR / f"vozpopuli_resumen_{fecha}.csv"
    df.to_csv(archivo, index=False)

    print("Scraping terminado correctamente")
    print("Archivo guardado en:", archivo)

# ---------------- EJECUCIÓN ----------------
if __name__ == "__main__":
    main()