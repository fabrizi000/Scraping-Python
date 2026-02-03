from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

# Configuraciones manuales
URL = "https://es.investing.com/economic-calendar/"
IMPACTO_MINIMO = 2            # 1, 2 o 3
FECHA_OBJETIVO = "2023-01-31" # YYYY-MM-DD

# Aceptar el pop up de cookies
def aceptar_cookies_si_aparece(driver):
    try:
        boton = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        boton.click()
        print("Cookies aceptadas")
        time.sleep(0.3)
    except:
        pass



# Seleccionar fecha elegida por usuario
def seleccionar_fecha_rango(driver, wait, fecha_objetivo):
    fecha = datetime.strptime(fecha_objetivo, "%Y-%m-%d")
    fecha_input = fecha.strftime("%d.%m.%Y")

    boton_calendario = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[contains(text(),'Personalizar fechas')]]")
        )
    )
    boton_calendario.click()

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-test="date-range-picker"]')
        )
    )

    inicio = wait.until(EC.presence_of_element_located((By.ID, "date-picker-start-day")))
    fin = wait.until(EC.presence_of_element_located((By.ID, "date-picker-end-day")))

    inicio.clear()
    inicio.send_keys(fecha_input)

    fin.clear()
    fin.send_keys(fecha_input)

    boton_aceptar = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[.//text()='Aceptar']")
        )
    )
    driver.execute_script("arguments[0].click();", boton_aceptar)

    time.sleep(1)

# Configuracion de selenium
service = Service("/usr/local/bin/geckodriver")
driver = webdriver.Firefox(service=service)
driver.set_window_size(1920, 1080)
wait = WebDriverWait(driver, 20)

# abrir pagina
driver.get(URL)

aceptar_cookies_si_aparece(driver)
seleccionar_fecha_rango(driver, wait, FECHA_OBJETIVO)

wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))

# check de listas
rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
print(f"\n Filas encontradas: {len(rows)}\n")

# procesar resultados
resultados = []

for row in rows:
    try:
        evento = row.find_element(By.CSS_SELECTOR, "a").text.strip()
        if not evento:
            continue

        try:
            hora = row.find_element(
                By.CSS_SELECTOR, 'td[class*="w-\\[60px\\]"] div'
            ).text.strip()
        except:
            hora = "N/A"

        try:
            divisa = row.find_element(By.CSS_SELECTOR, "span.w-\\[30px\\]").text.strip()
        except:
            divisa = ""

        # Importancia del 1 al 3
        importancia = len(
            row.find_elements(
                By.CSS_SELECTOR,
                'td[class*="min-w-[60px]"] svg.opacity-60'
            )
        )

        if importancia != IMPACTO_MINIMO:
            continue

        valores = row.find_elements(By.CSS_SELECTOR, 'td[dir="ltr"]')
        actual = valores[0].text.strip() if len(valores) > 0 else ""
        prevision = valores[1].text.strip() if len(valores) > 1 else ""
        anterior = valores[2].text.strip() if len(valores) > 2 else ""

        resultados.append({
            "hora": hora,
            "divisa": divisa,
            "evento": evento,
            "importancia": importancia,
            "actual": actual,
            "prevision": prevision,
            "anterior": anterior
        })

    except:
        continue

# Resultados
if not resultados:
    print(f"No hay noticias con impacto nivel {IMPACTO_MINIMO} para {FECHA_OBJETIVO}")
else:
    for r in resultados:
        print("Hora:", r["hora"])
        print("Divisa:", r["divisa"])
        print("Evento:", r["evento"])
        print("Importancia:", r["importancia"])
        print("Actual:", r["actual"])
        print("Previsión:", r["prevision"])
        print("Anterior:", r["anterior"])
        print("-" * 40)

driver.quit()