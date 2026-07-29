"""
Pruebas End-to-End (Selenium) — Fase 4.

IMPORTANTE: estas pruebas NO se ejecutan en el sandbox de esta
conversación (no hay navegador ni GPU/display disponibles ahí). Deben
correrse en tu máquina local, con:

  1. La aplicación corriendo (local con `python run.py` o en el
     contenedor Docker de la Fase 2, escuchando en el puerto 5000).
  2. Google Chrome instalado.
  3. `pip install -r requirements-dev.txt`

Ejecución (modo visual, como pide el PDF, es decir SIN --headless):
  python -m pytest tests_e2e/ -v -s

Cada test usa webdriver-manager, que descarga automáticamente la
versión correcta de chromedriver la primera vez que se ejecuta.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = 'http://localhost:5000'


def test_home_page_loads_with_form(browser):
    """1) La página principal carga y contiene el formulario para acortar URLs."""
    browser.get(BASE_URL)
    assert 'Py URL Shortener' in browser.title or 'URL' in browser.page_source

    input_field = browser.find_element(By.NAME, 'long_url')
    assert input_field.is_displayed()


def test_shorten_a_valid_url_end_to_end(browser):
    """2) Flujo principal: pegar una URL válida y verificar que se genera un short_url visible."""
    browser.get(BASE_URL)

    input_field = browser.find_element(By.NAME, 'long_url')
    input_field.send_keys('https://www.wikipedia.org')

    submit_button = browser.find_element(By.CSS_SELECTOR, "input[type='submit'][name='submit']")
    submit_button.click()

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, 'clipboard'))
    )
    short_url_value = browser.find_element(By.ID, 'clipboard').get_attribute('value')
    assert short_url_value.startswith(BASE_URL)


def test_shorten_an_invalid_url_shows_validation_error(browser):
    """3) Enviar un texto que no es una URL debe mostrar un mensaje de error, no un short_url."""
    browser.get(BASE_URL)

    input_field = browser.find_element(By.NAME, 'long_url')
    input_field.send_keys('esto-no-es-una-url')

    submit_button = browser.find_element(By.CSS_SELECTOR, "input[type='submit'][name='submit']")
    submit_button.click()

    WebDriverWait(browser, 10).until(
        lambda d: 'valid' in d.page_source.lower() or 'link' in d.page_source.lower()
    )
    # El short_url NO debe haberse generado ante un input invalido.
    assert len(browser.find_elements(By.ID, 'clipboard')) == 0


def test_create_and_follow_short_url_redirect(browser):
    """4) Crear un short_url y verificar que, al visitarlo, redirige a la URL original."""
    browser.get(BASE_URL)
    input_field = browser.find_element(By.NAME, 'long_url')
    input_field.send_keys('https://www.wikipedia.org')
    browser.find_element(By.CSS_SELECTOR, "input[type='submit'][name='submit']").click()

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, 'clipboard'))
    )
    short_url = browser.find_element(By.ID, 'clipboard').get_attribute('value')

    # Navega directamente a la URL corta generada y confirma que el
    # navegador terminó en la URL larga original (redirect 302 seguido).
    browser.get(short_url)
    WebDriverWait(browser, 10).until(lambda d: 'wikipedia.org' in d.current_url)
    assert 'wikipedia.org' in browser.current_url
