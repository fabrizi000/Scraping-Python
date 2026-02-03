from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------- CONFIGURACIÓN ----------
URL = "https://es.investing.com/economic-calendar/"

service = Service("/usr/local/bin/geckodriver")
driver = webdriver.Firefox(service=service)

# 👉 AQUÍ MISMO
driver.set_window_size(1920, 1080)

wait = WebDriverWait(driver, 20)

# ---------- ABRIR PÁGINA ----------
driver.get(URL)

# ---------- ESPERAR A QUE CARGUE LA TABLA ----------
wait.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "table")
    )
)

# ---------- OBTENER FILAS ----------
calendar_table = driver.find_element(By.CSS_SELECTOR, "table")
rows = calendar_table.find_elements(By.CSS_SELECTOR, "tbody tr")

print(f"Filas encontradas: {len(rows)}\n")

# ---------- RECORRER FILAS ----------
for row in rows:
    try:
        # Evento (filtro clave)
        evento = row.find_element(By.CSS_SELECTOR, "a").text.strip()
        if not evento:
            continue

        # Hora (selector correcto para columna hora)
        try:
            hora = row.find_element(
                By.CSS_SELECTOR,
                'td[class*="w-\\[60px\\]"] div'
            ).text.strip()
        except:
            hora = "N/A"

        # Divisa
        try:
            divisa = row.find_element(By.CSS_SELECTOR, "span.w-\\[30px\\]").text.strip()
        except:
            divisa = ""

        # Importancia (solo estrellas activas)
        importancia = 0
        try:
            star_div = row.find_element(By.CSS_SELECTOR, "td div.flex")
            stars = star_div.find_elements(By.TAG_NAME, "svg")
            for star in stars:
                if "opacity-60" in star.get_attribute("class"):
                    importancia += 1
        except:
            importancia = 0

        # Valores numéricos
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

# ---------- CERRAR ----------
driver.quit()
