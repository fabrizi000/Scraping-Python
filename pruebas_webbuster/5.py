from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# Configuracion manual
URL = "https://es.investing.com/economic-calendar/"
IMPACTO_MINIMO = 3            # 1 = bajo, 2 = medio, 3 = alto
FECHA_OBJETIVO = "2020-01-31" # YYYY-MM-DD
GECKODRIVER_PATH = "/usr/local/bin/geckodriver"

# Selectores reutilizables
SELECTOR_LOGIN_POPUP = "div[class*='auth_popup']"
SELECTOR_IMPORTANCIA = 'td[class*="min-w-[60px]"] svg.opacity-60'
SELECTOR_VALORES = 'td[dir="ltr"]'


# FUNCIONES AUXILIARES
def click_si_existe(wait, by, selector, timeout=5):
    """Hace click en un elemento si aparece"""
    try:
        wait.until(EC.element_to_be_clickable((by, selector))).click()
        return True
    except:
        return False


def aceptar_cookies(wait):
    click_si_existe(wait, By.ID, "onetrust-accept-btn-handler")


def cerrar_popup_login(driver):
    """Elimina el popup de login si aparece"""
    try:
        popup = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_LOGIN_POPUP))
        )
        driver.execute_script("arguments[0].remove();", popup)
    except:
        pass


def seleccionar_fecha(wait, fecha_str):
    """Selecciona la misma fecha como inicio y fin"""
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
    """Devuelve el texto del elemento o una cadena vacia"""
    try:
        return row.find_element(by, selector).text.strip()
    except:
        return ""


# INICIAR SELENIUM
service = Service(GECKODRIVER_PATH)
driver = webdriver.Firefox(service=service)
driver.set_window_size(1920, 1080)
wait = WebDriverWait(driver, 20)

# CARGAR PAGINA
driver.get(URL)

aceptar_cookies(wait)
cerrar_popup_login(driver)
seleccionar_fecha(wait, FECHA_OBJETIVO)

wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))

# LEER TABLA
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
        "hora": hora,
        "divisa": divisa,
        "evento": evento,
        "importancia": importancia,
        "actual": valores[0].text.strip() if len(valores) > 0 else "",
        "prevision": valores[1].text.strip() if len(valores) > 1 else "",
        "anterior": valores[2].text.strip() if len(valores) > 2 else ""
    })

# MOSTRAR RESULTADOS
if not resultados:
    print(f"No hay noticias con impacto {IMPACTO_MINIMO} para {FECHA_OBJETIVO}")
else:
    for r in resultados:
        print(f"""
Hora: {r['hora']}
Divisa: {r['divisa']}
Evento: {r['evento']}
Importancia: {r['importancia']}
Actual: {r['actual']}
Previsión: {r['prevision']}
Anterior: {r['anterior']}
----------------------------------------
""")

driver.quit()