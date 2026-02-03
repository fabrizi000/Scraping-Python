import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://elpais.com/economia/"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

noticias = []

for articulo in soup.find_all("article"):
    titulo = articulo.find("h2")
    enlace = articulo.find("a")

    if titulo and enlace:
        noticias.append({
            "medio": "El País",
            "titulo": titulo.get_text(strip=True),
            "url": enlace["href"]
        })

df = pd.DataFrame(noticias)
df.to_csv("elpais_economia.csv", index=False)