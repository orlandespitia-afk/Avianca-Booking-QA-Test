# pages/select_flight_page.py
from selenium.webdriver.common.by import By
from pages.base_page import BasePage 
import allure
import logging 
import time
from selenium.common.exceptions import TimeoutException

class SelectFlightPage(BasePage):
    """Clase Page Object para la página de resultados de búsqueda y selección de vuelo (Módulo 2)."""

    # ----------------------------------------------------
    # LOCATORS DEL MÓDULO 2
    # ----------------------------------------------------
    # Encabezado para validar que la página de resultados cargó correctamente
    _HEADER_SEARCH_RESULTS = (By.XPATH, "//div[contains(@class, 'journey-selector_content-title') or contains(text(), 'Selecciona tu vuelo')]")
    
    # Botón para abrir el selector de tarifa del primer vuelo
    _BUTTON_FARE_SELECTOR = (By.XPATH, "(//button[contains(@class, 'journey_price_button') and .//span[contains(text(), 'Seleccionar de tarifa')]])[1]")
    
    # Botón para seleccionar la tarifa más barata (el primer botón 'Seleccionar' que aparece dentro del modal)
    _BUTTON_SELECT_FARE = (By.XPATH, "(//button[contains(@class, 'fare_button') and contains(., 'Seleccionar')])[1]")

    # ----------------------------------------------------
    # MÉTODOS DE UTILIDAD LOCAL
    # ----------------------------------------------------
    def _perform_scroll_down(self, num_scrolls: int, distance_px: int = 250):
        """Función interna para realizar el scroll vertical hacia abajo N veces."""
        for i in range(num_scrolls):
            self.driver.execute_script(f"window.scrollBy(0, {distance_px});")
            logging.info(f"Scroll N°{i+1} ejecutado con {distance_px}px.")
            time.sleep(0.5)

    # ----------------------------------------------------
    # MÉTODOS DE FLUJO DEL MÓDULO 2
    # ----------------------------------------------------
    @allure.step("Validar que la página de resultados de búsqueda ha cargado")
    def validate_search_results(self, origin: str, destination: str):
        """Espera a que los resultados de la búsqueda sean visibles y clickeables."""
        logging.info("Esperando 5 segundos para la carga estable de la página post-CAPTCHA...")
        time.sleep(5)
        
        # Un scroll inicial para asegurar que los elementos del vuelo estén en la vista
        self._perform_scroll_down(1)

        logging.info("Validando presencia del botón clave 'Seleccionar de tarifa' con un tiempo de espera de 20s...")
        try:
            self._wait_for_element(self._BUTTON_FARE_SELECTOR, timeout=20)
            logging.info("Página de resultados cargada y lista. Botón de tarifa visible y clickeable.")
        except TimeoutException:
            logging.error("Timeout: No se encontraron resultados de vuelo o el botón de selección de tarifa no cargó.")
            raise

    @allure.step("Seleccionar la tarifa más económica y avanzar a detalles de vuelo")
    def select_cheapest_flight(self):
        """Abre el selector de tarifas y hace clic en la primera opción disponible."""
        logging.info("Abre el selector de tarifas.")
        
        # 1. Clic para desplegar la selección de tarifas
        self._wait_and_click(self._BUTTON_FARE_SELECTOR, "Botón para Abrir el Selector de Tarifa")
        logging.info("Selector de tarifa abierto.")
        
        # 2. Scrolls para asegurar visibilidad de las tarifas dentro del modal
        logging.info("Ejecutando 3 scrolls para asegurar la visibilidad de las tarifas...")
        self._perform_scroll_down(3)
        
        # 3. Hacemos clic en el botón 'Seleccionar' de la primera tarifa con clic forzado.
        try:
            button = self._wait_for_element(self._BUTTON_SELECT_FARE, timeout=10)
            # Clic forzado con JS para evitar problemas de intercepción dentro del modal
            self.driver.execute_script("arguments[0].click();", button) 
            logging.info("Clic forzado en Botón 'Seleccionar' tarifa. Avanzando al siguiente Módulo.")
        except TimeoutException as e:
            logging.error("Fallo crítico: El botón 'Seleccionar' de la tarifa no se encontró a tiempo.")
            raise e