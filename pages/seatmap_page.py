# pages/seatmap_page.py
from selenium.webdriver.common.by import By
from pages.base_page import BasePage 
import allure
import logging 
import time
from selenium.common.exceptions import TimeoutException

class SeatmapPage(BasePage):
    """
    Page Object para la página de Selección de Asientos (Seatmap).
    Implementa la lógica de selección solo para pasajeros impares.
    """

    # ----------------------------------------------------
    # LOCATORS DEL MÓDULO
    # ----------------------------------------------------
    _VALIDATION_ELEMENT = (By.XPATH, "//div[contains(text(), 'Selección de asientos')]")
    # Pestañas de Pasajero (usado para iterar sobre todos los pasajeros)
    _PASSENGER_TABS = (By.XPATH, "//div[@role='tablist']//button[contains(., 'Pasajero')]") 
    # Selector del primer asiento disponible (robustez)
    _FIRST_AVAILABLE_SEAT = (By.XPATH, "(//div[contains(@class, 'seat-available') or contains(@class, 'seat-standard') and not(contains(@class, 'seat-occupied'))][1] | //button[contains(@class, 'seat-button') and not(@disabled)])[1]")
    _BUTTON_CONTINUAR = (By.XPATH, "//button[contains(., 'Continuar')]")

    # ----------------------------------------------------
    # MÉTODOS DE FLUJO
    # ----------------------------------------------------
    @allure.step("Módulo Asientos: Seleccionar asientos para Pasajeros Impares (Caso 2)")
    def select_seats_for_odd_passengers(self):
        logging.info("Esperando la carga del Módulo de Asientos (Seatmap)...")
        try:
            self._wait_for_element(self._VALIDATION_ELEMENT, timeout=20) 
            logging.info("Módulo de Asientos cargado.")
        except TimeoutException:
            logging.warning("Módulo de Asientos no cargó a tiempo. Intentando continuar...")
            pass
            
        passenger_tabs = self.driver.find_elements(*self._PASSENGER_TABS)
        
        # Itera sobre las pestañas de pasajeros. El índice (index) empieza en 1.
        for index, tab in enumerate(passenger_tabs, 1):
            if index % 2 != 0: # La condición clave: si el índice es IMPAR
                with allure.step(f"Seleccionando asiento para Pasajero {index} (IMPAR)"):
                    try:
                        # 1. Clic en la pestaña del pasajero impar (activar el mapa de asientos)
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", tab)
                        self.driver.execute_script("arguments[0].click();", tab)
                        time.sleep(1) 
                        
                        # 2. Seleccionar el primer asiento disponible con clic forzado
                        self._wait_and_click_js(self._FIRST_AVAILABLE_SEAT, f"Asiento para P{index}")
                        logging.info(f"Asiento seleccionado para Pasajero {index}.")
                        time.sleep(2) 
                    except Exception as e:
                        logging.warning(f"Falló la selección de asiento para P{index}. Error: {e}")
            else:
                logging.info(f"Pasajero {index} (PAR) omitido según requisito del Caso 2.")
                
        # 3. Clic en Continuar (Navegación forzada al siguiente módulo)
        with allure.step("Clic en Continuar desde Seatmap"):
            try:
                # Scroll y clic forzado para evitar problemas de intercepción
                button_element = self._wait_for_element(self._BUTTON_CONTINUAR, timeout=10)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", button_element)
                time.sleep(1) 
                
                self._wait_and_click(self._BUTTON_CONTINUAR, "Botón Continuar (Asientos)")
                logging.info("Clic en Continuar completado. Pasando al Módulo de Pago.")
            except TimeoutException:
                logging.error("Timeout: No se pudo encontrar el botón Continuar en Asientos.")
                raise