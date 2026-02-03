import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

# Configuracion local
URL = "https://datosmacro.expansion.com/paro"
OUTPUT_DIR = Path("/home/alusmr/Documentos/pruebas_webbuster/datoscsv/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PAISES_SLUG = {
    "espana": "España",
    "alemania": "Alemania",
    "uk": "Reino Unido",
    "francia": "Francia",
    "italia": "Italia",
    "usa": "Estados Unidos",
    "japon": "Japón",
    "zona-euro": "Zona Euro"
}

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Funciones
def leer_numero(td):
    if td is None:
        return None

    if td.has_attr("data-value"):
        return float(td["data-value"])

    texto = td.get_text(strip=True)
    if not texto or texto == "—":
        return None

    texto = texto.replace("%", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None

# Tabla de paro sobre los paises mas influyentes en la economia (incluyendo a Espana y quitando China)
html = requests.get(URL, headers=HEADERS).text
soup = BeautifulSoup(html, "html.parser")

tabla = soup.find(
    "div",
    class_="tabletit",
    string="Tasa de desempleo: 2025 Países"
).find_next("table")

datos_resumen = []
urls_paises = {}

for fila in tabla.find_all("tr"):
    a = fila.find("a")
    if not a:
        continue

    href = a["href"]
    slug = href.split("/")[-1]

    if slug not in PAISES_SLUG:
        continue

    pais = PAISES_SLUG[slug]
    urls_paises[pais] = "https://datosmacro.expansion.com" + href

    numeros = fila.find_all("td", class_="numero")
    fecha = fila.find("td", class_="fecha")

    datos_resumen.append({
        "País": pais,
        "Tasa de desempleo (%)": leer_numero(numeros[0]) if len(numeros) > 0 else None,
        "Variación": leer_numero(numeros[1]) if len(numeros) > 1 else None,
        "Variación anual": leer_numero(numeros[2]) if len(numeros) > 2 else None,
        "Mes": fecha.get_text(strip=True) if fecha else None
    })

df_resumen = pd.DataFrame(datos_resumen)
df_resumen.to_csv(OUTPUT_DIR / "paro_paises_2025.csv", index=False)

print("CSV resumen generado correctamente")

# Tabla comparativa mas detallada de cada pais
for pais, url in urls_paises.items():
    html_pais = requests.get(url, headers=HEADERS).text
    soup_pais = BeautifulSoup(html_pais, "html.parser")

    titulo = soup_pais.find(
        "div",
        class_="tabletit",
        string=f"{pais}: Paro"
    )

    if not titulo:
        print(f"No se encontró tabla para {pais}")
        continue

    tabla_pais = titulo.find_next("table")

    datos = []
    for tr in tabla_pais.find_all("tr")[1:]:
        td = tr.find_all("td")
        if len(td) != 3:
            continue

        datos.append({
            "Indicador": td[0].get_text(strip=True),
            "2025": td[1].get_text(strip=True),
            "2024": td[2].get_text(strip=True)
        })

    df_pais = pd.DataFrame(datos)
    nombre = pais.lower().replace(" ", "_")
    df_pais.to_csv(
        OUTPUT_DIR / f"paro_{nombre}_2025_2024.csv",
        index=False
    )

    print(f"CSV generado para {pais}")