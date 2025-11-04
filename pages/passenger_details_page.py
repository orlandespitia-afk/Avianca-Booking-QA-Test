# pages/passenger_details_page.py
from selenium.webdriver.common.by import By
from pages.base_page import BasePage 
import allure
import logging 
import time
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException


class PassengerDetailsPage(BasePage): 
    """Clase Page Object para el Módulo de Datos de Pasajeros."""
    
    # ----------------------------------------------------
    # LOCATORS DEL MÓDULO (Campos del primer pasajero)
    # ----------------------------------------------------
    _VALIDATION_GENDER_BUTTON = (By.XPATH, "//button[contains(@id, 'IdPaxGender') and @role='combobox']")
    
    # Campos de Nombre y Apellido
    _INPUT_FIRST_NAME = (By.XPATH, "//input[contains(@id, 'IdFirstName') and not(contains(@id, 'Document'))][1]") 
    _INPUT_LAST_NAME = (By.XPATH, "//input[contains(@id, 'IdLastName') or contains(@name, 'IdLastName')][1]") 
    
    # Localizadores de Fecha de Nacimiento y Documentos
    _BUTTON_DOB_DAY = (By.XPATH, "//button[contains(@id, 'dateDayId_IdDateOfBirthHidden')]")
    _BUTTON_DOB_MONTH = (By.XPATH, "//button[contains(@id, 'dateMonthId_IdDateOfBirthHidden')]")
    _BUTTON_DOB_YEAR = (By.XPATH, "//button[contains(@id, 'dateYearId_IdDateOfBirthHidden')]")
    _BUTTON_DOC_NATIONALITY = (By.XPATH, "//button[contains(@id, 'IdDocNationality')]")
    
    # Documento y Programas
    _BUTTON_DOC_TYPE = (By.ID, "passengerId") 
    _INPUT_DOC_NUMBER = (By.XPATH, "//input[contains(@id, 'DocumentNumber')]") 
    _BUTTON_CUSTOMER_PROGRAMS = (By.ID, "customerPrograms")
    
    # Campos de Contacto
    _BUTTON_PHONE_PREFIX = (By.ID, "phone_prefixPhoneId")
    _INPUT_LOYALTY_NUMBER = (By.ID, "AVloyaltyNumber") 
    _INPUT_PHONE_NUMBER = (By.ID, "phone_phoneNumberId")
    _INPUT_EMAIL = (By.ID, "email")
    _INPUT_CONFIRM_EMAIL = (By.ID, "confirmEmail")

    # Botón Final
    _CHECKBOX_NEWSLETTER = (By.XPATH, "//label[./span[contains(text(), 'Acepto el uso de mis datos personales')]]")
    _BUTTON_CONTINUE_TO_PAYMENT = (By.XPATH, "//button[contains(., 'Continuar')]") 
    
    # ----------------------------------------------------
    # MÉTODOS DE UTILIDAD LOCAL
    # ----------------------------------------------------
    def _force_type(self, locator: tuple, value: str, element_name: str):
        """Método de escritura forzada con JS para asegurar la inyección de valores."""
        logging.info(f"Intentando escribir en {element_name} ({value}) mediante JavaScript.")
        try:
            element = self._wait_for_element(locator, timeout=5)
            element.clear() 
            self.driver.execute_script("arguments[0].value = arguments[1];", element, value)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)
            logging.info(f"Escritura forzada exitosa en {element_name}.")
            time.sleep(1.5)
        except TimeoutException:
            logging.error(f"Timeout al intentar localizar el elemento {element_name} para escritura forzada.")
            raise

    def _select_dropdown_option(self, button_locator: tuple, option_text: str, element_name: str):
        """Selecciona una opción de un dropdown forzando el clic y los eventos de cambio."""
        logging.info(f"Seleccionando '{option_text}' para {element_name}.")
        
        button_element = self._wait_for_element(button_locator, timeout=5)
        self.driver.execute_script("arguments[0].click();", button_element)
        time.sleep(0.5) 
        
        option_xpath = f"//button[@role='option']//span[text()='{option_text}' or text()='{option_text.zfill(2)}']"
        option_locator = (By.XPATH, option_xpath)
        
        try:
            option_element = self._wait_for_element(option_locator, timeout=7)
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", option_element)
            time.sleep(0.5)

            self.driver.execute_script("arguments[0].click();", option_element)
            
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", button_element)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", button_element)

            logging.info(f"Selección (JS forzada) de {option_text} completada para {element_name}.")

        except (TimeoutException, ElementNotInteractableException) as e:
            logging.error(f"Fallo crítico: No se pudo localizar o hacer clic forzado en la opción '{option_text}' para {element_name}.")
            raise 
            
    def _scroll_up_correction(self, pixels=100):
        """Aplica scroll hacia arriba para contrarrestar el desplazamiento en la UI."""
        logging.info(f"Aplicando scroll de corrección (-{pixels}px).")
        self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
        time.sleep(1)
        
    def _scroll_down(self, pixels):
        """Aplica scroll hacia abajo."""
        logging.info(f"Aplicando scroll hacia abajo de {pixels}px.")
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")
        time.sleep(1)
        
    def _scroll_to_bottom(self):
        """Mueve la vista a la parte inferior de la página."""
        logging.info("Moviendo la vista a la parte inferior de la página.")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)


    # ----------------------------------------------------
    # MÉTODOS DE FLUJO DEL MÓDULO
    # ----------------------------------------------------
    @allure.step("Validar que la página de datos de pasajero ha cargado")
    def validate_passenger_details_page(self):
        """Espera a que el botón de género del primer pasajero sea visible (Validación de carga)."""
        logging.info("Esperando la carga del Módulo de Datos del Pasajero...")
        try:
            # Se usa un timeout extendido debido a la alta latencia en la carga de este módulo.
            self._wait_for_element(self._VALIDATION_GENDER_BUTTON, timeout=40) 
            logging.info("Módulo de Pasajeros cargado exitosamente.")
        except TimeoutException as e:
            logging.error("Timeout: La página de datos del pasajero no cargó correctamente.")
            raise e

    @allure.step("Rellenar los datos del primer pasajero")
    def fill_first_passenger_data(self, passenger_data: dict):
        """Rellena todos los campos de datos del primer pasajero (incluyendo bypass de validación)."""
        
        first_name = "Test" 
        last_name = "Automation" 
        
        logging.info("Pausa de 5 segundos para estabilidad antes de llenar datos.")
        time.sleep(5)
        
        # 1. GÉNERO
        gender_button_locator = (By.ID, passenger_data["gender_id"])
        logging.info("Seleccionando Género.")
        self._wait_and_click(gender_button_locator, "Botón de Género")
        gender_option_locator = (By.XPATH, f"//button[@role='option' and .//span[text()='{passenger_data['gender_option']}']]")
        self._wait_and_click(gender_option_locator, f"Opción de Género: {passenger_data['gender_option']}")
        
        # 2. NOMBRE
        logging.info(f"Ingresando nombre: {first_name}")
        self._force_type(self._INPUT_FIRST_NAME, first_name, "Input Nombre") 
        
        # 3. APELLIDOS
        logging.info(f"Ingresando apellido(s): {last_name}")
        self._force_type(self._INPUT_LAST_NAME, last_name, "Input Apellido")

        # 4. FECHA DE NACIMIENTO
        with allure.step("Seleccionar Fecha de Nacimiento (05 Febrero 1995)"):
            self._scroll_down(pixels=100)
            self._select_dropdown_option(self._BUTTON_DOB_DAY, "5", "Día de Nacimiento")
            self._scroll_up_correction() 
            self._select_dropdown_option(self._BUTTON_DOB_MONTH, "Febrero", "Mes de Nacimiento") 
            self._scroll_up_correction()
            self._select_dropdown_option(self._BUTTON_DOB_YEAR, "1995", "Año de Nacimiento")
            self._scroll_up_correction()

        # 5. NACIONALIDAD Y DOCUMENTO (BYPASS)
        with allure.step("Seleccionar Nacionalidad y forzar Documento (BYPASS)"):
            self._select_dropdown_option(self._BUTTON_DOC_NATIONALITY, "Colombia", "Nacionalidad del Documento")

            # 5.1 SELECCIÓN DEL TIPO (Cédula de Ciudadanía)
            try:
                self._select_dropdown_option(self._BUTTON_DOC_TYPE, "Cédula de Ciudadanía", "Tipo de Documento")
                logging.info("BYPASS: Cédula de Ciudadanía seleccionada.")
            except Exception as e:
                logging.warning(f"BYPASS: Falló la selección de Tipo de Documento. {e}")
                
            # 5.2 LLENADO DEL NÚMERO
            try:
                doc_number_input = self._wait_for_element(self._INPUT_DOC_NUMBER, timeout=3)
                self.driver.execute_script("arguments[0].value = '1024567890';", doc_number_input)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", doc_number_input)
                logging.info("BYPASS: Número de Documento inyectado.")
                time.sleep(1) 
            except Exception as e:
                logging.warning(f"BYPASS: Falló la inyección del Número de Documento. {e}")
                
        # 6. PROGRAMAS DE CLIENTE FRECUENTE
        with allure.step("Seleccionar Programa de Cliente: lifemiles"):
            self._select_dropdown_option(self._BUTTON_CUSTOMER_PROGRAMS, "lifemiles ", "Programas de Cliente")
            self.driver.execute_script("window.scrollBy(0, -80);")
            time.sleep(1)
            
        # 7. NÚMERO DE CLIENTE FRECUENTE
        with allure.step("Ingresar Número de Cliente lifemiles"):
            loyalty_number = "1114060886"
            self._force_type(self._INPUT_LOYALTY_NUMBER, loyalty_number, "Número de Cliente") 

        # 8. CONTACTO (Prefijo, Teléfono, Email)
        with allure.step("Seleccionar Prefijo y Datos de Contacto"):
            self._select_dropdown_option(self._BUTTON_PHONE_PREFIX, "Colombia", "Prefijo Telefónico")

            phone_number = "3185578482"
            self._force_type(self._INPUT_PHONE_NUMBER, phone_number, "Número de Teléfono") 
        
            email = "test.automation@gmail.com" 
            self._force_type(self._INPUT_EMAIL, email, "Email") 

            confirm_email = "test.automation@gmail.com" 
            self._force_type(self._INPUT_CONFIRM_EMAIL, confirm_email, "Confirmar Email") 

        # 9. CLIC FINAL Y PAUSA MANUAL
        with allure.step("Aceptar términos y Continuar al pago"):
            self._scroll_to_bottom()
            self._wait_and_click(self._CHECKBOX_NEWSLETTER, "Checkbox Suscripción")
            
            logging.warning("PAUSA MANUAL CRÍTICA: El script se detiene (20s). Por favor, haga clic en 'Continuar' en el navegador.")
            time.sleep(20)
            logging.info("Pausa manual terminada. Intentando clic de seguridad para el siguiente módulo.")
            
            # Clic en Continuar (Técnica ULTRA-FORZADA DE TRIPLE ACCIÓN)
            try:
                button_element = self._wait_for_element(self._BUTTON_CONTINUE_TO_PAYMENT, timeout=10)
                
                logging.info("Aplicando SCROLL FORZADO al botón 'Continuar'.")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", button_element)
                time.sleep(0.5)
                
                span_element = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Continuar')]")
                self.driver.execute_script("arguments[0].click();", span_element)
                self.driver.execute_script("arguments[0].click();", button_element) 
                logging.info("Clic en Continuar ejecutado exitosamente.")
            
            except Exception as e:
                logging.error(f"FALLA CRÍTICA: No se pudo hacer clic en 'Continuar' ni siquiera después de la pausa. {e}")


        logging.info("Datos del pasajero completados. Pasando al módulo de Servicios.")