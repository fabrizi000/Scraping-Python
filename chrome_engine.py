from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys, time, os, subprocess  # <--- agregar os y subprocess

url = sys.argv[1]

service = Service("/usr/local/bin/chromedriver")
options = Options()
# options.add_argument('--headless')  # Descomenta si no quieres que se abra Chrome

driver = webdriver.Chrome(service=service, options=options)

# Crear carpeta resultados
carpeta_resultados = "/home/fabri/Documents/scrap/resultados"
os.makedirs(carpeta_resultados, exist_ok=True)
output_file = os.path.join(carpeta_resultados, "datos_scrapeadosChrome.txt")

try:
    print("Abriendo Investing.com con Chrome...")
    driver.get(url)

    wait = WebDriverWait(driver, 20)
    table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.genTbl")))
    rows = driver.find_elements(By.CSS_SELECTOR, "table.genTbl tr")

    economic_data = []
    for i, row in enumerate(rows[1:15], 1):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 4:
            row_data = {
                'Hora': cells[0].text.strip(),
                'Evento': cells[1].text.strip(),
                'Impacto': cells[2].text.strip(),
                'Actual': cells[3].text.strip()
            }
            economic_data.append(row_data)
            print(f"Fila {i}: {row_data}")

    # Guardar en .txt
    with open(output_file, "w", encoding="utf-8") as f:
        for evento in economic_data:
            f.write(f"{evento['Hora']} | {evento['Evento']} | {evento['Impacto']} | {evento['Actual']}\n")

    print(f"\nDatos guardados en {output_file}")
    subprocess.run(["xdg-open", output_file])

except Exception as e:
    print(f"Error: {e}")
finally:
    time.sleep(3)
    driver.quit()
