import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

URL = "https://elpais.com/economia/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

noticias = []

# 1️⃣ Sacar links del día
r = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(r.text, "html.parser")

links = set()
for article in soup.find_all("article"):
    a = article.find("a", href=True)
    if a and a["href"].startswith("https://"):
        links.add(a["href"])

# 2️⃣ Entrar a cada noticia
for url in links:
    try:
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        titulo = soup.find("h1")
        cuerpo = soup.find("div", {"data-dtm-region": "articulo_cuerpo"})

        if not titulo or not cuerpo:
            continue

        texto = " ".join(p.get_text(strip=True) for p in cuerpo.find_all("p"))

        noticias.append({
            "titulo": titulo.get_text(strip=True),
            "url": url,
            "contenido": texto
        })

        time.sleep(1)

    except:
        continue

df = pd.DataFrame(noticias)
df.to_csv("elpais_noticias_hoy.csv", index=False)

print("El País → OK")