import pytest
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from browsermobproxy import Server
# Se asume que esta clase existe en utils/database_manager.py
from utils.database_manager import DatabaseManager 
import allure 

# ----------------------------------------------------
# CONFIGURACIÓN INICIAL DEL FRAMEWORK
# ----------------------------------------------------

# 1. Configuración del Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    handlers=[
                        logging.FileHandler("test_execution.log"),
                        logging.StreamHandler()
                    ])

# 2. RUTA DEL PROXY (Asegurando el path al ejecutable)
PROXY_SERVER_PATH = os.path.join(os.getcwd(), 'resources', 'browsermob-proxy-2.1.4', 'bin', 'browsermob-proxy')


# ----------------------------------------------------
# FIXTURES DE CONFIGURACIÓN DE PYTEST
# ----------------------------------------------------

def pytest_addoption(parser):
    """Define las opciones que se pueden pasar por línea de comandos (e.g., --browser, --baseurl)."""
    parser.addoption("--browser", action="store", default="chrome", help="Tipo de navegador a usar (chrome o firefox)")
    parser.addoption("--baseurl", action="store", default="https://nuxqa4.avtest.ink/", help="URL base del entorno a probar")

@pytest.fixture(scope="session") 
def db_manager():
    """Inicializa la conexión a SQLite para la sesión de pruebas."""
    db = DatabaseManager()
    yield db 
    # Teardown de la conexión
    logging.info("Conexión con la base de datos cerrada.")
    # No llamamos a db.close() porque la conexión se maneja dentro de DatabaseManager.

@pytest.fixture(scope="session")
def proxy_server():
    """Inicializa y gestiona el servidor BrowserMob Proxy para sniffing."""
    server = None
    proxy = None
    try:
        # Inicializa el servidor en un puerto específico
        server = Server(PROXY_SERVER_PATH, options={'port': 8090}) 
        server.start()
        
        # Crea una instancia de proxy sin opciones complejas
        proxy = server.create_proxy() 
        
        logging.info("BrowserMob Proxy iniciado con éxito.")
        
        yield proxy
        
    except Exception as e:
        logging.error(f"Fallo al iniciar BrowserMob Proxy: {e}")
        yield None
        
    finally:
        # Bloque de cierre seguro
        if server and server.process.poll() is None: # Verifica si el servidor aún está corriendo
            server.stop() 
            logging.info("BrowserMob Proxy detenido.")


@pytest.fixture(scope="function")
def driver(request, proxy_server, db_manager): 
    """Inicializa el WebDriver para cada función de prueba."""
    
    browser_name = request.config.getoption("--browser")
    base_url = request.config.getoption("--baseurl")
    
    options = ChromeOptions()
    options.add_argument("--disable-infobars")
    
    # Podrías añadir la configuración del proxy aquí si fuera necesario
    # if proxy_server:
    #     options.add_argument(f'--proxy-server={proxy_server.proxy}')
    
    # Inicialización del driver
    driver = webdriver.Chrome(options=options) 

    # Adjuntando metadata al driver para ser accesible en los Page Objects
    driver.base_url = base_url
    driver.db_manager = db_manager 
    driver.proxy_server = proxy_server 
    
    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(45) # Espera implícita larga para la carga de SPA
    
    logging.info(f"WebDriver inicializado para {browser_name} en {base_url}.")
    
    yield driver
    
    # Teardown del driver
    logging.info("Cerrando WebDriver.")
    driver.quit()