import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.sofascore.com/es/tennis/tournament/atp/shanghai/2519"

driver = webdriver.Chrome()   # abre una ventana de Chrome
try:
    driver.get(URL)

    # Espera a que cargue el cuerpo de la página
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(5)   # margen para que el JavaScript pinte los datos

    print("Título:", driver.title)

    # Guardamos el HTML ya renderizado para inspeccionarlo
    with open("../data/sofascore_shanghai.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    # Muestra el texto visible de la página
    texto = driver.find_element(By.TAG_NAME, "body").text
    print(texto[:3000])
finally:
    driver.quit()