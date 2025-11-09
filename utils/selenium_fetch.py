# utils/selenium_fetch.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from PIL import Image
import io
from .webdriver_helper import get_chrome_service

def fetch_with_selenium(url, headless=True, wait_seconds=3, screenshot=False, window_size=(1200,900)):
    """
    Carga la página con Selenium y devuelve dict con 'html', 'title', 'screenshot_bytes' (opcional).
    Excepciones se lanzan hacia el caller.
    """
    chrome_options = Options()
    if headless:
        # usar el nuevo modo headless si tu chrome/chromedriver lo soporta
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
    service = get_chrome_service()

    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(wait_seconds)  # espera a que JS cargue; puedes mejorar con WebDriverWait
        html = driver.page_source
        title = driver.title
        result = {"html": html, "title": title}
        if screenshot:
            png = driver.get_screenshot_as_png()
            result["screenshot_bytes"] = png
        return result
    finally:
        try:
            driver.quit()
        except Exception:
            pass
