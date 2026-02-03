from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

# =====================================================
# PARÁMETROS DE USUARIO (luego vendrán del GUI)
# =====================================================
URL = "https://es.investing.com/economic-calendar/"
IMPACTO_MINIMO = 1              # 1, 2 o 3
FECHA_OBJETIVO = "2026-1-31"   # YYYY-MM-DD

# =====================================================
# FUNCIÓN: ACEPTAR COOKIES (SI APARECE)
# =====================================================
def aceptar_cookies_si_aparece(driver):
    try:
        boton = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        boton.click()
        print("Cookies aceptadas")
        time.sleep(0.5)
    except:
        pass

# =====================================================
# FUNCIÓN: CERRAR POPUP DE LOGIN (SI APARECE)
# =====================================================
def cerrar_popup_login_si_aparece(driver):
    try:
        overlay = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class*='auth_popup_darkBackground']")
            )
        )
        driver.execute_script("arguments[0].remove();", overlay)
        print("Popup de login eliminado")
        time.sleep(0.5)
    except:
        pass

# =====================================================
# FUNCIÓN: SELECCIONAR FECHA (RANGO = MISMO DÍA)
# =====================================================
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

    inicio = wait.until(
        EC.presence_of_element_located((By.ID, "date-picker-start-day"))
    )
    inicio.clear()
    inicio.send_keys(fecha_input)

    fin = driver.find_element(By.ID, "date-picker-end-day")
    fin.clear()
    fin.send_keys(fecha_input)

    boton_aceptar = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[.//text()='Aceptar']")
        )
    )
    driver.execute_script("arguments[0].click();", boton_aceptar)

    time.sleep(1)

# =====================================================
# CONFIGURACIÓN SELENIUM
# =====================================================
service = Service("/usr/local/bin/geckodriver")
driver = webdriver.Firefox(service=service)
driver.set_window_size(1920, 1080)
wait = WebDriverWait(driver, 20)

# =====================================================
# ABRIR PÁGINA
# =====================================================
driver.get(URL)

aceptar_cookies_si_aparece(driver)
cerrar_popup_login_si_aparece(driver)
seleccionar_fecha_rango(driver, wait, FECHA_OBJETIVO)

wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
)

# =====================================================
# OBTENER FILAS
# =====================================================
calendar_table = driver.find_element(By.CSS_SELECTOR, "table")
rows = calendar_table.find_elements(By.CSS_SELECTOR, "tbody tr")

print(f"\nFilas encontradas: {len(rows)}\n")

# =====================================================
# RECORRER FILAS
# =====================================================
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

        # IMPORTANCIA CORRECTA (1–3)
        importancia = 0
        try:
            estrellas = row.find_elements(
                By.CSS_SELECTOR,
                'td.hidden.md\\:table-cell div.flex svg'
            )
            for estrella in estrellas:
                clase = estrella.get_attribute("class")
                if clase and "opacity-60" in clase:
                    importancia += 1

            importancia = min(importancia, 3)

        except:
            importancia = 0

        if importancia < IMPACTO_MINIMO:
            continue

        valores = row.find_elements(By.CSS_SELECTOR, 'td[dir="ltr"]')
        actual = valores[0].text.strip() if len(valores) > 0 else ""
        prevision = valores[1].text.strip() if len(valores) > 1 else ""
        anterior = valores[2].text.strip() if len(valores) > 2 else ""

        print("Hora:", hora)
        print("Divisa:", divisa)
        print("Evento:", evento)
        print("Importancia:", importancia)
        print("Actual:", actual)
        print("Previsión:", prevision)
        print("Anterior:", anterior)
        print("-" * 40)

    except:
        continue

# =====================================================
# CERRAR
# =====================================================
driver.quit()