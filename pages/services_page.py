# pages/services_page.py
from selenium.webdriver.common.by import By
from pages.base_page import BasePage 
import allure
import logging 
import time

class ServicesPage(BasePage):
    """Clase Page Object para el Módulo de Servicios (Selección de equipaje)."""

    # ----------------------------------------------------
    # LOCATORS DEL MÓDULO
    # ----------------------------------------------------
    _VALIDATION_ELEMENT = (By.XPATH, "//div[contains(text(), 'Servicios disponibles') or contains(text(), 'Selecciona los servicios')]")
    _BUTTON_CONTINUAR = (By.XPATH, "//button[contains(., 'Continuar')]")
    
    # Localizadores para selección de servicios (basados en el requisito del Caso 2)
    _LOCATOR_CARRY_ON = (By.XPATH, "//div[contains(., 'Equipaje de mano') or contains(., 'Carry-on')]/ancestor::div[contains(@class, 'service-card')]//button[contains(., 'Añadir') or contains(., 'Seleccionar') or contains(., 'Agregar')]")
    _LOCATOR_CHECKED_BAGGAGE = (By.XPATH, "//div[contains(., 'Equipaje facturado') or contains(., 'Checked baggage')]/ancestor::div[contains(@class, 'service-card')]//button[contains(., 'Añadir') or contains(., 'Seleccionar') or contains(., 'Agregar')]")
    _LOCATOR_SPORT_BAGGAGE = (By.XPATH, "//div[contains(., 'Equipaje deportivo') or contains(., 'Sport baggage')]/ancestor::div[contains(@class, 'service-card')]//button[contains(., 'Añadir') or contains(., 'Seleccionar') or contains(., 'Agregar')]")

    # ----------------------------------------------------
    # MÉTODOS DE FLUJO
    # ----------------------------------------------------
    @allure.step("Módulo Servicios: Seleccionar Carry-on, Checked y Equipaje Deportivo (Caso 2)")
    def select_required_baggage(self):
        """Selecciona todos los tipos de equipaje requeridos para avanzar en el flujo."""
        logging.info("Esperando la carga del Módulo de Servicios...")
        self._wait_for_element(self._VALIDATION_ELEMENT, timeout=15) 
        
        locators_to_click = [
            ("Equipaje de Mano (Carry-on)", self._LOCATOR_CARRY_ON),
            ("Equipaje Facturado (Checked)", self._LOCATOR_CHECKED_BAGGAGE),
            ("Equipaje Deportivo (Sport)", self._LOCATOR_SPORT_BAGGAGE),
        ]

        for name, locator in locators_to_click:
            with allure.step(f"Seleccionando servicio: {name}"):
                try:
                    # Busca todos los botones del servicio (uno por pasajero/segmento)
                    buttons = self.driver.find_elements(*locator)
                    if not buttons:
                        logging.warning(f"ADVERTENCIA: {name}: No se encontraron botones de 'Añadir'. Omitiendo.")
                        continue
                        
                    for button in buttons:
                        # Scroll y clic forzado
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        self.driver.execute_script("arguments[0].click();", button)
                        time.sleep(0.5) 
                        
                    logging.info(f"{name}: Seleccionados {len(buttons)} elementos.")
                except Exception as e:
                    logging.error(f"FALLO al intentar seleccionar {name}. Error: {e}")

        # 4. Clic en Continuar (Navegación forzada al siguiente módulo)
        with allure.step("Clic en Continuar desde Servicios"):
            try:
                # ScrollIntoView Directo al Botón
                button_element = self._wait_for_element(self._BUTTON_CONTINUAR, timeout=10)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", button_element)
                time.sleep(1) 
                
                # Clic final
                self._wait_and_click(self._BUTTON_CONTINUAR, "Botón Continuar (Servicios)")
                logging.info("Clic en Continuar completado. Pasando al Módulo de Asientos.")
            except Exception as e:
                logging.error(f"Error al hacer clic en Continuar en Servicios: {e}")
                raise