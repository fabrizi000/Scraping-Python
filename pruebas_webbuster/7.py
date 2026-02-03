import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd

# Configuracion manual para pruebas
URL = "https://es.investing.com/economic-calendar/"
IMPACTO_MINIMO = 2 # Se filtra por impacto de noticia de entre 1 al 3
FECHA_OBJETIVO = "2020-01-31" # Fecha en ese formato
GECKODRIVER_PATH = "/usr/local/bin/geckodriver"

CARPETA_SALIDA = "/home/fabri/Documents/pruebas_webbuster/datoscsv"
os.makedirs(CARPETA_SALIDA, exist_ok=True)

SELECTOR_LOGIN_POPUP = "div[class*='auth_popup']"
SELECTOR_IMPORTANCIA = 'td[class*="min-w-[60px]"] svg.opacity-60'
SELECTOR_VALORES = 'td[dir="ltr"]'

# Preparando terreno para scrapear porque si no la tabla no se ve
def click_si_existe(driver, by, selector, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        ).click()
        return True
    except:
        return False


def aceptar_cookies(driver):
    click_si_existe(driver, By.ID, "onetrust-accept-btn-handler")


def cerrar_popup_login(driver):
    try:
        popup = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_LOGIN_POPUP))
        )
        driver.execute_script("arguments[0].remove();", popup)
    except:
        pass


def seleccionar_fecha(wait, fecha_str):
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d.%m.%Y")

    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[.//span[contains(text(),'Personalizar fechas')]]")
    )).click()

    inicio = wait.until(EC.presence_of_element_located((By.ID, "date-picker-start-day")))
    fin = wait.until(EC.presence_of_element_located((By.ID, "date-picker-end-day")))

    inicio.clear()
    inicio.send_keys(fecha)

    fin.clear()
    fin.send_keys(fecha)

    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[.//text()='Aceptar']")
    )).click()


def texto_si_existe(row, by, selector):
    try:
        return row.find_element(by, selector).text.strip()
    except:
        return ""

# Pasos en la pagina con Selenium
service = Service(GECKODRIVER_PATH)
driver = webdriver.Firefox(service=service)
driver.set_window_size(1920, 1080)
wait = WebDriverWait(driver, 20)

driver.get(URL)

aceptar_cookies(driver)
cerrar_popup_login(driver)
seleccionar_fecha(wait, FECHA_OBJETIVO)

wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))

# Proceso del Scraping
rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
resultados = []

for row in rows:
    evento = texto_si_existe(row, By.CSS_SELECTOR, "a")
    if not evento:
        continue

    importancia = len(row.find_elements(By.CSS_SELECTOR, SELECTOR_IMPORTANCIA))
    if importancia != IMPACTO_MINIMO:
        continue

    hora = texto_si_existe(row, By.CSS_SELECTOR, 'td[class*="w-\\[60px\\]"] div') or "N/A"
    divisa = texto_si_existe(row, By.CSS_SELECTOR, "span.w-\\[30px\\]")
    valores = row.find_elements(By.CSS_SELECTOR, SELECTOR_VALORES)

    resultados.append({
        "fecha": FECHA_OBJETIVO,
        "hora": hora,
        "divisa": divisa,
        "evento": evento,
        "impacto": importancia,
        "actual": valores[0].text.strip() if len(valores) > 0 else "",
        "prevision": valores[1].text.strip() if len(valores) > 1 else "",
        "anterior": valores[2].text.strip() if len(valores) > 2 else ""
    })

driver.quit()

# Pandas para salidas csv la verdad que no tengo idea para que esto si al final es un csv pero bueno xddddddddd
df = pd.DataFrame(resultados)

if df.empty:
    print(f"No hay noticias de impacto {IMPACTO_MINIMO} para {FECHA_OBJETIVO}")
else:
    df = df.replace("", pd.NA)

    df.columns = [col.capitalize() for col in df.columns]

    df = df.sort_values(by="Hora")

    # Resumen de divisas, si no pongo esto sale un mensaje feo al final que cuando lo vi me dio miedo :V
    resumen_divisas = (
        df["Divisa"]
        .value_counts()
        .reset_index()
    )
    resumen_divisas.columns = ["Divisa", "Total noticias"]

    # Proceso de guardado con CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_csv = os.path.join(
        CARPETA_SALIDA,
        f"calendario_{FECHA_OBJETIVO}_impacto{IMPACTO_MINIMO}_{timestamp}.csv"
    )

    with open(nombre_csv, "w", encoding="utf-8-sig") as f:

        df.to_csv(f, index=False)

        f.write("\n\n")

        f.write("Resumen por divisa\n")

        resumen_divisas.to_csv(f, index=False)

    # Aqui esta un poco lo que me daba miedo, eso sale en la consola cuando Paco lo vea :v
    print(f"\nDatos guardados en: {nombre_csv}\n")

    print("Primeras filas del calendario:")
    print(df.head())

    print("\nResumen por divisa:")
    for _, row in resumen_divisas.iterrows():
        print(f"{row['Divisa']}: {row['Total noticias']}")