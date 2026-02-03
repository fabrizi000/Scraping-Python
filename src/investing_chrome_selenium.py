import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd

# Configuracion manual para pruebas
URL = "https://es.investing.com/economic-calendar/"
IMPACTO_MINIMO = 3 # Solo selecionar los siguientes impactos como filtro: 1 = bajo, 2 = medio, 3 = alto
FECHA_OBJETIVO = "2022-05-05" # YYYY-MM-DD fecha solo en ese formato, se recomienda fechas superiores a las del 2018
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"

CARPETA_SALIDA = "/home/alusmr/Documentos/pruebas_webbuster/datoscsv/" # Esta es mi carpeta local, para hacer el GUI se modificara a un general
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

    boton = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[.//span[contains(text(),'Personalizar fechas')]]")
    ))

    # En Chrome a veces hay elementos flotantes que molestan, asi que centramos el boton
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)

    try:
        boton.click()
    except:
        # Si Chrome se pone tonto, click por JS
        driver.execute_script("arguments[0].click();", boton)

    for campo in ("date-picker-start-day", "date-picker-end-day"):
        input_fecha = wait.until(EC.presence_of_element_located((By.ID, campo)))
        input_fecha.clear()
        input_fecha.send_keys(fecha)

    aceptar = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[.//text()='Aceptar']")
    ))
    driver.execute_script("arguments[0].click();", aceptar)


def texto_si_existe(elemento, by, selector):
    try:
        return elemento.find_element(by, selector).text.strip()
    except:
        return ""

# Pasos en la pagina con Selenium
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-infobars")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 20)

try:
    driver.get(URL)

    aceptar_cookies(driver)
    cerrar_popup_login(driver)
    seleccionar_fecha(wait, FECHA_OBJETIVO)

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))

    # Proceso del Scraping
    resultados = []

    for row in driver.find_elements(By.CSS_SELECTOR, "table tbody tr"):
        evento = texto_si_existe(row, By.CSS_SELECTOR, "a")
        if not evento:
            continue

        importancia = len(row.find_elements(By.CSS_SELECTOR, SELECTOR_IMPORTANCIA))
        if importancia != IMPACTO_MINIMO:
            continue

        valores = row.find_elements(By.CSS_SELECTOR, SELECTOR_VALORES)

        resultados.append({
            "fecha": FECHA_OBJETIVO,
            "hora": texto_si_existe(row, By.CSS_SELECTOR, 'td[class*="w-\\[60px\\]"] div') or "N/A",
            "divisa": texto_si_existe(row, By.CSS_SELECTOR, "span.w-\\[30px\\]"),
            "evento": evento,
            "impacto": importancia,
            "actual": valores[0].text.strip() if len(valores) > 0 else "",
            "prevision": valores[1].text.strip() if len(valores) > 1 else "",
            "anterior": valores[2].text.strip() if len(valores) > 2 else ""
        })

finally:
    # Esto asegura que el navegador se cierre aunque algo pete por el camino
    driver.quit()

# Pandas para salidas csv, ahora si se que hace. Si no sale nada se imprimira un mensaje y no creara nada
df = pd.DataFrame(resultados)

if df.empty:
    print(f"No hay noticias de impacto {IMPACTO_MINIMO} para {FECHA_OBJETIVO}")
else:
    df = df.replace("", pd.NA)
    df = df.sort_values(by="hora")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    nombre_csv = os.path.join(
        CARPETA_SALIDA,
        f"calendario_{FECHA_OBJETIVO}_impacto{IMPACTO_MINIMO}_{timestamp}.csv"
    )
    df.to_csv(nombre_csv, index=False, encoding="utf-8-sig")

    df_resumen = df["divisa"].value_counts().reset_index()
    df_resumen.columns = ["divisa", "total noticias"]

    nombre_csv_resumen = os.path.join(
        CARPETA_SALIDA,
        f"calendario_{FECHA_OBJETIVO}_impacto{IMPACTO_MINIMO}_{timestamp}_resumen_divisas.csv"
    )
    df_resumen.to_csv(nombre_csv_resumen, index=False, encoding="utf-8-sig")

    # Esto es lo que sale en consola, una mini tabla y el resumen de divisas
    print(f"\nDatos guardados en:\n- {nombre_csv}")
    print(f"- {nombre_csv_resumen}\n")

    print("Primeras filas del calendario:")
    print(df.head())

    print("\nResumen por divisa:")
    for _, row in df_resumen.iterrows():
        print(f"{row['divisa']}: {row['total noticias']}")