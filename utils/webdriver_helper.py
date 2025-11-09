# utils/webdriver_helper.py
import os
from selenium.webdriver.chrome.service import Service
from pathlib import Path

def get_chrome_service(chromedriver_env_var="CHROMEDRIVER_PATH"):
    """
    Devuelve un selenium.chrome.service.Service seguro.
    Prioriza CHROMEDRIVER_PATH (ruta local) y si no existe intenta
    usar webdriver_manager de forma controlada (import dinámico).
    Esto evita imports problemáticos en el arranque (p.e. dotenv issues).
    """
    # 1) ruta local desde env
    path = os.environ.get(chromedriver_env_var)
    if path:
        p = Path(path)
        if p.exists():
            return Service(str(p))

    # 2) buscar chromedriver en PATH
    # si el sistema ya tiene chromedriver en PATH, selenium lo detectará usando Service()
    # pero para ser explicito:
    for candidate in ["chromedriver", "chromedriver.exe"]:
        if shutil.which(candidate):
            return Service(candidate)

    # 3) fallback dinámico a webdriver_manager
    try:
        # import dinámico para evitar side-effects en import time
        from webdriver_manager.chrome import ChromeDriverManager
        return Service(ChromeDriverManager().install())
    except Exception as e:
        # No pudimos obtener chromedriver automáticamente
        raise RuntimeError(
            "No se pudo obtener chromedriver automáticamente. "
            "Por favor define CHROMEDRIVER_PATH en tu .env o instala chromedriver y colócalo en PATH. "
            f"Detalles: {e}"
        )
