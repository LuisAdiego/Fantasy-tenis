# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 11:05:01 2026

@author: rotci
"""

import time
import re
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By

URL = "https://www.sofascore.com/es/tennis/tournament/atp/shanghai/2519"

# Carpeta data/ al lado de scraper/, funcione desde donde lo ejecutes
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Categorías que quieres recoger del desplegable de "Estadísticas"
CATEGORIAS = [
    "Aces por partido",
    "Dobles faltas por partido",
    "Puntos de quiebre salvados",
    "Puntos de quiebre convertidos",
    "Tie breaks ganados",
]

# Todas las opciones que vi en tu captura (sirven para localizar el desplegable
# cuando está cerrado, porque el botón muestra la opción seleccionada).
# Si la que aparece por defecto no está aquí, añádela.
TODAS_LAS_OPCIONES = CATEGORIAS + [
    "1.er servicio",
    "Puntos ganados con 1.er servicio",
    "2.o servicio",
    "Puntos ganados con 2.o servicio",
]
# Si prefieres localizar el desplegable por CSS, pon aquí su selector
SELECTOR_DESPLEGABLE = None

PAUSA = 2


def nombre_seguro(texto):
    s = "".join(c if c.isalnum() else "_" for c in texto.lower())
    return s.strip("_")


def guardar(driver, nombre):
    texto = driver.find_element(By.TAG_NAME, "body").text
    (DATA_DIR / f"{nombre}.txt").write_text(texto, encoding="utf-8")
    (DATA_DIR / f"{nombre}.html").write_text(driver.page_source, encoding="utf-8")
    print(f"[OK] {nombre}: {len(texto)} caracteres")


def scroll_hasta_el_final(driver, pausa=2, max_intentos=30):
    ultima = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_intentos):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pausa)
        nueva = driver.execute_script("return document.body.scrollHeight")
        if nueva == ultima:
            break
        ultima = nueva
    driver.execute_script("window.scrollTo(0, 0);")


def elementos_con_texto(driver, texto):
    exacto = driver.find_elements(
        By.XPATH, f'//*[not(*)][normalize-space(.)="{texto}"]'
    )
    visibles = [e for e in exacto if e.is_displayed()]
    if visibles:
        return visibles
    parcial = driver.find_elements(
        By.XPATH, f'//*[not(*)][contains(normalize-space(.), "{texto}")]'
    )
    return [e for e in parcial if e.is_displayed()]


def clic(driver, elem):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
    time.sleep(0.5)
    try:
        elem.click()
    except Exception:
        driver.execute_script("arguments[0].click();", elem)


def clic_texto(driver, texto, ultimo=False, espera=10):
    fin = time.time() + espera
    while time.time() < fin:
        elems = elementos_con_texto(driver, texto)
        if elems:
            clic(driver, elems[-1] if ultimo else elems[0])
            return True
        time.sleep(0.5)
    print(f"[AVISO] No encuentro '{texto}'")
    return False


def abrir_desplegable(driver):
    if SELECTOR_DESPLEGABLE:
        driver.find_element(By.CSS_SELECTOR, SELECTOR_DESPLEGABLE).click()
        return True
    for opcion in TODAS_LAS_OPCIONES:
        elems = elementos_con_texto(driver, opcion)
        if elems:
            clic(driver, elems[0])
            return True
    return False


def aceptar_cookies(driver):
    for t in ["Consentir", "Aceptar todo", "Aceptar", "Acepto"]:
        elems = elementos_con_texto(driver, t)
        if elems:
            clic(driver, elems[0])
            print(f"[OK] Cookies: '{t}'")
            time.sleep(1)
            return


def main():
    driver = webdriver.Chrome()
    driver.maximize_window()
    try:
        driver.get(URL)
        time.sleep(5)
        aceptar_cookies(driver)

        scroll_hasta_el_final(driver)
        guardar(driver, "sofascore_inicio")

        # Pestaña Cuadro
        if clic_texto(driver, "Cuadro"):
            time.sleep(PAUSA)
            scroll_hasta_el_final(driver)
            guardar(driver, "sofascore_cuadro")

        # Pestaña Estadísticas
        if clic_texto(driver, "Estadísticas"):
            time.sleep(PAUSA) 
            guardar_paginas(driver, "sofascore_stats_defecto")

            for cat in CATEGORIAS:
                if not abrir_desplegable(driver):
                    print("[AVISO] No he podido abrir el desplegable")
                    driver.save_screenshot(str(DATA_DIR / "error_desplegable.png"))
                    break
                time.sleep(1)
                # ultimo=True: si la opción coincide con la que muestra el botón,
                # coge la de la lista y no el botón
                time.sleep(1) 
                if cat == "Tie breaks ganados": 
                    scroll_lista_desplegable(driver, "Puntos de quiebre convertidos") 
                    time.sleep(1) 
                    if clic_texto(driver, cat, ultimo=True): 
                        if clic_texto(driver, cat, ultimo=True):  
                            time.sleep(PAUSA)  
                            guardar_paginas(driver, f"sofascore_stats_{nombre_seguro(cat)}")
    finally:
        driver.quit()
        
def leer_etiqueta_paginacion(driver):
    xp = ('//*[not(*)][contains(normalize-space(.)," de ") '
          'and contains(normalize-space(.),"-") '
          'and string-length(normalize-space(.))<15]')
    for e in driver.find_elements(By.XPATH, xp):
        if e.is_displayed():
            m = re.match(r"(\d+)-(\d+) de (\d+)", e.text.strip())
            if m:
                return e, int(m.group(2)), int(m.group(3))
    return None, None, None


def guardar_paginas(driver, nombre, max_paginas=10):
    for n in range(1, max_paginas + 1):
        guardar(driver, f"{nombre}_p{n}")
        etiqueta, fin, total = leer_etiqueta_paginacion(driver)
        if etiqueta is None or fin >= total:
            break  # última página (o no hay paginación)
        siguiente = etiqueta.find_elements(By.XPATH, "following::button[1]")
        if not siguiente:
            break
        clic(driver, siguiente[0])
        time.sleep(PAUSA)

def scroll_lista_desplegable(driver, texto_referencia):
    """Baja hasta el final el contenedor con scroll que contiene una opción visible."""
    elems = elementos_con_texto(driver, texto_referencia)
    if not elems:
        return False
    js = """
    let el = arguments[0];
    while (el && el !== document.body) {
      if (el.scrollHeight > el.clientHeight + 5) {
        el.scrollTop = el.scrollHeight; return true;
      }
      el = el.parentElement;
    }
    return false;
    """
    return driver.execute_script(js, elems[0])


if __name__ == "__main__":
    main()