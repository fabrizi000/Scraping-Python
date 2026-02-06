import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from collections import Counter
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin

HOME = Path.home()

DOCUMENTS = HOME / "Documents"
if not DOCUMENTS.exists():
    DOCUMENTS = HOME / "Documentos"

CARPETA_SALIDA = DOCUMENTS / "WebBusterResultados" / "Expansion"
CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)

# ---------------- CONFIGURACIÓN ----------------
BASE_URL = "https://www.expansion.com"
URL = "https://www.expansion.com/economia.html"
HEADERS = {"User-Agent": "Mozilla/5.0"}
FRASES_RESUMEN = 3
SLEEP_SECONDS = 1

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
    r = requests.get(URL, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        url_completa = urljoin(BASE_URL, href)

        if (
            url_completa.startswith("https://www.expansion.com/economia/")
            and url_completa.endswith(".html")
        ):
            links.append(url_completa)

    links_unicos = list(dict.fromkeys(links))
    print(f"Enlaces detectados: {len(links_unicos)}")
    return links_unicos

# ---------------- SCRAPEAR NOTICIA ----------------
def scrapear_noticia(url):
    print("Procesando:", url)
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    titulo = soup.find("h1")

    cuerpo = soup.find("div", class_="ue-c-article__body")
    if not cuerpo:
        cuerpo = soup.find("div", {"itemprop": "articleBody"})
    if not cuerpo:
        cuerpo = soup.find("article")

    if not titulo or not cuerpo:
        print("No compatible, se descarta")
        return None

    parrafos = cuerpo.find_all("p")
    if not parrafos:
        print("Sin párrafos, se descarta")
        return None

    texto = " ".join(p.get_text(strip=True) for p in parrafos)
    resumen = resumir_texto(texto, FRASES_RESUMEN)

    return {
        "medio": "Expansión",
        "titulo": titulo.get_text(strip=True),
        "resumen": resumen,
        "url": url,
    }

# ---------------- MAIN ----------------
def main():
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

    links = obtener_links()
    noticias = []

    for i, url in enumerate(links, 1):
        try:
            print(f"[{i}/{len(links)}]")
            noticia = scrapear_noticia(url)
            if noticia:
                noticias.append(noticia)
            time.sleep(SLEEP_SECONDS)
        except Exception as e:
            print("Error al procesar:", url)
            print(e)

    print("Noticias válidas obtenidas:", len(noticias))

    if noticias:
        df = pd.DataFrame(noticias)
        archivo = CARPETA_SALIDA / f"expansion_resumen_{fecha}.csv"
        df.to_csv(archivo, index=False)
        print("Archivo de noticias guardado en:", archivo)
    else:
        print("No se han encontrado noticias válidas.")

    # CSV de links (trazabilidad)
    df_links = pd.DataFrame({"url": links})
    archivo_links = CARPETA_SALIDA / f"expansion_links_{fecha}.csv"
    df_links.to_csv(archivo_links, index=False)
    print("Archivo de enlaces guardado en:", archivo_links)

    print("Scraping terminado correctamente")

# ---------------- EJECUCIÓN ----------------
if __name__ == "__main__":
    main()