# pages/home_page.py
from selenium.webdriver.common.by import By
from pages.base_page import BasePage 
import allure
import logging 
import time 
from selenium.common.exceptions import TimeoutException

class HomePage(BasePage):
    """Page Object para la página de búsqueda inicial de vuelos."""
    
    # ----------------------------------------------------
    # LOCATORS DE BÚSQUEDA
    # ----------------------------------------------------
    _RADIO_ONEWAY = (By.XPATH, "//span[text()='Solo ida']")
    _BUTTON_ORIGIN = (By.ID, "originBtn") 
    _BUTTON_DESTINATION = (By.ID, "destinationBtn")
    
    # Localizadores específicos para los campos de búsqueda dentro del pop-up de ciudades
    _INPUT_SEARCH_ORIGIN = (By.ID, "departureStationInputId") 
    _INPUT_SEARCH_DESTINATION = (By.ID, "arrivalStationInputId")
    
    _INPUT_DATE_DEPARTURE = (By.ID, "date-departure-input")
    _DROPDOWN_ADULTS = (By.ID, "adults-selector")
    _DROPDOWN_INFANTS = (By.ID, "infants-selector")
    _BUTTON_SEARCH_FLIGHTS = (By.ID, "searchButton") 
    
    # Localizador de pop-up general (cookies/bienvenida)
    _BUTTON_CLOSE_POPUP = (By.XPATH, "//button[@aria-label='Cerrar' or @class='close-button' or text()='Aceptar']")


    def open(self):
        """Navega a la URL base del sitio."""
        self.driver.get(self.driver.base_url) 
        logging.info("Navegación inicial completada.") 

    @allure.step("Cerrar Pop-up de bienvenida o cookies")
    def close_initial_popup(self):
        """Intenta cerrar cualquier pop-up que pueda interceptar interacciones."""
        try:
            self._wait_and_click(self._BUTTON_CLOSE_POPUP, "Botón de Cierre de Pop-up Inicial", timeout=10)
        except Exception:
            logging.info("No se encontró el pop-up inicial. Continuamos.")
            pass

    @allure.step("Seleccionar tipo de viaje: Solo Ida")
    def select_one_way(self):
        """Hace clic en el radio button 'Solo ida'."""
        self._wait_and_click(self._RADIO_ONEWAY, "Radio Button Solo Ida", timeout=10)

    @allure.step("Realizar búsqueda de vuelo de Solo Ida")
    def search_flight(self, origin: str, destination: str, date: str, adults: int, infants: int):
        """Rellena el formulario de búsqueda con origen, destino, fecha y pasajeros."""
        
        # 1. ORIGEN
        self._wait_and_click(self._BUTTON_ORIGIN, "Botón Origen (Abre Pop-up)")
        self._wait_and_send_keys(self._INPUT_SEARCH_ORIGIN, origin, "Campo Búsqueda Origen")
        _BUTTON_ORIGIN_SELECT = (By.ID, origin)
        self._wait_and_click(_BUTTON_ORIGIN_SELECT, f"Seleccionar ciudad de Origen: {origin}")
        
        time.sleep(3.5) 
        
        # 2. DESTINO
        self._wait_and_send_keys(self._INPUT_SEARCH_DESTINATION, destination, "Campo Búsqueda Destino")
        _BUTTON_DESTINATION_SELECT = (By.ID, destination)
        self._wait_and_click(_BUTTON_DESTINATION_SELECT, f"Seleccionar ciudad de Destino: {destination}")
        
        time.sleep(4.0) 

        # 3. FECHA: Inyección directa de valor (bypass del calendario)
        date_input_id = self._INPUT_DATE_DEPARTURE[1] 
        script = f"document.getElementById('{date_input_id}').value = '{date}';"
        try:
            self.driver.execute_script(script)
            logging.info(f"JS Inyección de valor exitosa: '{date}' en Campo Fecha Salida.")
        except Exception as e:
            logging.warning(f"ADVERTENCIA: Fallo al inyectar la fecha (elemento no existe), continuando: {e}")
            pass
        
        time.sleep(1.0) # Espera reducida

        # 4. PASAJEROS: Inyección directa de valor (bypass de dropdowns)
        adults_id = self._DROPDOWN_ADULTS[1]
        adults_script = f"document.getElementById('{adults_id}').value = '{adults}';"
        try:
            self.driver.execute_script(adults_script)
            logging.info(f"JS Inyección de adultos exitosa: '{adults}' en Campo Adultos.")
        except Exception as e:
            logging.warning(f"ADVERTENCIA: Fallo al inyectar adultos (elemento no existe), continuando: {e}")
            pass
            
        infants_id = self._DROPDOWN_INFANTS[1]
        infants_script = f"document.getElementById('{infants_id}').value = '{infants}';"
        try:
            self.driver.execute_script(infants_script)
            logging.info(f"JS Inyección de infantes exitosa: '{infants}' en Campo Infantes.")
        except Exception as e:
            logging.warning(f"ADVERTENCIA: Fallo al inyectar infantes (elemento no existe), continuando: {e}")
            pass

        # 5. CLIC Y PAUSA MANUAL OBLIGATORIA (Manejo de CAPTCHA)
        try:
            # Clic forzado en el botón de búsqueda
            search_button = self._wait_for_element(self._BUTTON_SEARCH_FLIGHTS)
            self.driver.execute_script("arguments[0].click();", search_button)
            logging.info("Clic FORZADO (JS) en Botón Buscar Vuelos.")
            
            # Pausa para que el sitio cargue la verificación de seguridad
            time.sleep(5) 
            
            # --- PAUSA MANUAL OBLIGATORIA (25 SEGUNDOS) ---
            logging.warning("CAPTCHA/Verificación de Akamai DETECTADA. Iniciando pausa manual de 25 segundos.")
            logging.warning("POR FAVOR, RESUELVA EL CAPTCHA MANUALMENTE AHORA (Haga clic en el checkbox y en Continuar).")
            
            time.sleep(25) 
            
            logging.info("Pausa manual terminada. El test intentará continuar con la SelectFlightPage...")
                
        except Exception as e:
            logging.error(f"Fallo al forzar el clic en el botón de búsqueda: {e}")
            raise