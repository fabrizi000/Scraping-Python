import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

# Configuracion para cualquier equipo
HOME = Path.home()

DOCUMENTS = HOME / "Documents"
if not DOCUMENTS.exists():
    DOCUMENTS = HOME / "Documentos"

CARPETA_SALIDA = DOCUMENTS / "WebBusterResultados" / "DatosMacro"
CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
URL = "https://datosmacro.expansion.com/paro"

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
        try:
            return float(td["data-value"])
        except ValueError:
            return None

    texto = td.get_text(strip=True)
    if not texto or texto == "—":
        return None

    texto = texto.replace("%", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None

# Tabla de paro principal
html = requests.get(URL, headers=HEADERS).text
soup = BeautifulSoup(html, "html.parser")

titulo = None
for div in soup.find_all("div", class_="tabletit"):
    if "Tasa de desempleo" in div.get_text():
        titulo = div
        break

if not titulo:
    raise Exception("No se encontró la tabla principal de tasa de desempleo")

tabla = titulo.find_next("table")

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
        "pais": pais,
        "tasa de desempleo (%)": leer_numero(numeros[0]) if len(numeros) > 0 else None,
        "variación": leer_numero(numeros[1]) if len(numeros) > 1 else None,
        "variación anual": leer_numero(numeros[2]) if len(numeros) > 2 else None,
        "mes": fecha.get_text(strip=True) if fecha else None
    })

df_resumen = pd.DataFrame(datos_resumen)
df_resumen.to_csv(CARPETA_SALIDA / "paro_paises_resumen.csv", index=False)

print("CSV resumen generado correctamente")

# Tablas detalladas por país
for pais, url in urls_paises.items():
    html_pais = requests.get(url, headers=HEADERS).text
    soup_pais = BeautifulSoup(html_pais, "html.parser")

    titulo_pais = None
    for div in soup_pais.find_all("div", class_="tabletit"):
        texto = div.get_text()
        if pais in texto and "Paro" in texto:
            titulo_pais = div
            break

    if not titulo_pais:
        print(f"No se encontró tabla para {pais}")
        continue

    tabla_pais = titulo_pais.find_next("table")

    datos = []
    filas = tabla_pais.find_all("tr")

    # Cabeceras dinámicas (años reales)
    headers = [th.get_text(strip=True) for th in filas[0].find_all("th")]

    for tr in filas[1:]:
        td = tr.find_all("td")
        if len(td) != len(headers):
            continue

        fila_dict = {"indicador": td[0].get_text(strip=True)}
        for i in range(1, len(headers)):
            fila_dict[headers[i]] = td[i].get_text(strip=True)

        datos.append(fila_dict)

    df_pais = pd.DataFrame(datos)
    nombre = pais.lower().replace(" ", "_")
    df_pais.to_csv(
        CARPETA_SALIDA / f"paro_{nombre}.csv",
        index=False
    )

    print(f"CSV generado para {pais}")
