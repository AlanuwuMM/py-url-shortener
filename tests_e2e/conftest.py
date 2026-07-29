"""
Fixture del navegador para Selenium.

- En tu máquina local (demo en vivo ante el profesor): corre en modo
  VISUAL, tal como exige el PDF, porque la variable de entorno CI no
  existe.
- En GitHub Actions (Fase 5): el runner no tiene pantalla, así que se
  activa automáticamente --headless=new cuando detecta la variable de
  entorno estándar `CI=true` que GitHub Actions define por defecto.
"""
import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture()
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')

    if os.environ.get('CI'):
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.implicitly_wait(5)
    yield driver
    if not os.environ.get('CI'):
        time.sleep(1)
    driver.quit()
