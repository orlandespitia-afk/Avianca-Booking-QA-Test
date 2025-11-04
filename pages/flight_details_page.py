# pages/flight_details_page.py
from selenium.webdriver.common.by import By
from pages.base_page import BasePage 
import allure
import logging 
import time
from selenium.common.exceptions import TimeoutException

class FlightDetailsPage(BasePage):
    """Page Object para la página de detalles de vuelo, que a veces actúa como un resumen antes de pasajeros."""
    
    # ----------------------------------------------------
    # LOCATORS DEL MÓDULO (Resumen/Detalles antes de Pasajeros)
    # ----------------------------------------------------
    # Elemento estable para validar la carga de la página (El encabezado con la fecha/ruta)
    _HEADER_FLIGHT_DETAILS = (By.XPATH, "//div[contains(@class, 'journey-selector_selected-date')]") 
    
    # Selector de fecha/ruta que a veces requiere clic para revelar el contenido
    _DIV_DATE_SELECTOR = (By.XPATH, "//div[contains(@class, 'journey-selector_selected-date') and .//span[contains(text(), 'noviembre') or contains(text(), 'diciembre')]]")
    
    # Botón principal para avanzar a la siguiente etapa (Datos del Pasajero)
    _BUTTON_CONTINUE = (By.XPATH, "//button[contains(., 'Continuar')]")

    # ----------------------------------------------------
    # MÉTODOS DE FLUJO
    # ----------------------------------------------------
    @allure.step("Validar que la página de detalles de vuelo ha cargado")
    def validate_flight_details_page(self):
        """Espera a que el encabezado de detalles de vuelo sea visible."""
        logging.info("Esperando la carga del Módulo 3: Detalles de Vuelo...")
        
        try:
            self._wait_for_element(self._HEADER_FLIGHT_DETAILS, timeout=15)
            logging.info("Módulo 3 estabilizado (Validación de carga exitosa).")
        except TimeoutException as e:
            logging.error("Timeout: Falló la validación inicial del Módulo 3. La página no cargó correctamente.")
            raise e

    @allure.step("Avanzar a la página de datos de pasajero")
    def continue_to_passenger_details(self):
        """Ejecuta la secuencia para pasar del resumen a la página de Pasajeros."""
        
        # En algunas versiones del sitio, es necesario hacer clic en el selector de ruta para forzar la carga de la siguiente etapa.
        logging.info("Haciendo clic en el selector de fecha/ruta para avanzar.")
        self._wait_and_click(self._DIV_DATE_SELECTOR, "Elemento Selector de Fecha/Ruta")
        time.sleep(1.0) 
        
        # Uso de scrollIntoView para asegurar que el botón 'Continuar' sea clicable (solución a interceptaciones)
        button = self._wait_for_element(self._BUTTON_CONTINUE, timeout=10) 
        
        logging.info("Aplicando scroll forzado al botón 'Continuar'.")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(1.0) 
            
        logging.info("Haciendo clic en el botón 'Continuar'.")
        self._wait_and_click(self._BUTTON_CONTINUE, "Botón Continuar")
        logging.info("Clic en Continuar completado. Pasando al Módulo de Pasajeros.")