# pages/base_page.py
import os
import logging
from typing import Tuple, Union, Any, TypeVar

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import allure

# Definición de tipo de variable genérica
T = TypeVar("T")

class BasePage:
    """Clase base para Page Objects, maneja las interacciones comunes con Selenium."""
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        # Tiempo de espera por defecto para la mayoría de las operaciones.
        self.wait = WebDriverWait(self.driver, 25) 
        
        # Inicializa la URL base del driver, esencial para navegaciones.
        self.driver.base_url = getattr(self.driver, 'base_url', '') or ''


    def _wait_for_element(self, locator: Tuple[str, str], timeout: Union[int, float] = 25) -> Any:
        """
        Espera a que un elemento sea visible en el DOM.
        Lanza TimeoutException si el elemento no aparece.
        """
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            return element
        except TimeoutException:
            logging.error(f"Timeout esperando el elemento con locator {locator}")
            raise

    def _wait_and_click(self, locator: Tuple[str, str], element_name: str, timeout: Union[int, float] = 25):
        """
        Espera a que un elemento sea visible y hace clic.
        Si el clic es interceptado, intenta forzar el clic con JavaScript.
        """
        try:
            element = self._wait_for_element(locator, timeout)
            element.click()
            logging.info(f"Clic: {element_name} {locator}")
        except ElementClickInterceptedException:
            logging.warning(f"Advertencia: El clic en {element_name} fue interceptado. Intentando con JS.")
            element = self.driver.find_element(*locator)
            self.driver.execute_script("arguments[0].click();", element)
            logging.info(f"Clic forzado por JS: {element_name} {locator}")
        except Exception as e:
            logging.error(f"Fallo al hacer clic en {element_name} {locator}: {e}")
            raise

    def _wait_and_send_keys(self, locator: Tuple[str, str], value: str, element_name: str, timeout: Union[int, float] = 25):
        """Espera a que un elemento sea visible, lo limpia y envía texto."""
        try:
            element = self._wait_for_element(locator, timeout)
            element.clear()
            element.send_keys(value)
            logging.info(f"Input '{value}' en: {element_name} {locator}")
        except Exception as e:
            logging.error(f"Fallo al enviar keys a {element_name} {locator}: {e}")
            raise
    
    def _is_element_visible(self, locator: Tuple[str, str], timeout: Union[int, float] = 1) -> bool:
        """Verifica si un elemento es visible dentro de un corto timeout para validaciones rápidas."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
            
    def _wait_and_click_js(self, locator: Tuple[str, str], element_name: str, timeout: Union[int, float] = 25):
        """Espera a que un elemento sea visible y hace clic forzado con JavaScript."""
        try:
            element = self._wait_for_element(locator, timeout)
            self.driver.execute_script("arguments[0].click();", element)
            logging.info(f"Clic forzado por JS: {element_name} {locator}")
        except Exception as e:
            logging.error(f"Fallo al hacer clic con JS en {element_name} {locator}: {e}")
            raise
            
    @allure.step("Tomar Captura de Pantalla: {name}")
    def _take_screenshot(self, name: str):
        """Toma una captura de pantalla y la adjunta al reporte Allure."""
        try:
            allure.attach(
                self.driver.get_screenshot_as_png(), 
                name=name, 
                attachment_type=allure.attachment_type.PNG
            )
        except Exception as e:
            logging.error(f"Fallo al tomar captura de pantalla '{name}': {e}")
            pass
            
    def open(self, path: str = ''):
        """Navega a la URL base o a una ruta específica."""
        url = self.driver.base_url + path
        self.driver.get(url)
        logging.info(f"Navegación inicial completada a: {url}")