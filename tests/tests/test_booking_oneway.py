# tests/tests/test_booking_oneway.py
import pytest
import time
import allure
import logging

# IMPORTACIONES REQUERIDAS
from pages.home_page import HomePage
from pages.select_flight_page import SelectFlightPage
from pages.flight_details_page import FlightDetailsPage 
from pages.passenger_details_page import PassengerDetailsPage 
from pages.services_page import ServicesPage      
from pages.seatmap_page import SeatmapPage        
# from pages.payment_page import PaymentPage      # Clase de pago pendiente de implementacion
from utils.database_manager import DatabaseManager # Requisito de BD Local
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# --- CONFIGURACIÓN DE DATOS ---
PASSENGER_DATA = {
    "gender_id": "IdPaxGender_0", 
    "gender_option": "Masculino",
}


@allure.epic("Caso 1 & 2: Flujo de Reserva Completa")
@allure.feature("Solo Ida (One-Way) con requisitos complejos")
# Parámetros para ejecutar la prueba en diferentes escenarios (Caso 1 y Caso 2 - 3 pasajeros)
@pytest.mark.parametrize("origin, destination, adults, infants", [
    ("BOG", "CTG", 1, 0),  
    ("MDE", "SCL", 3, 0)   
])
class TestBooking(object):
    
    # Fixture que inyecta el driver y el manejador de BD a la clase de prueba
    @pytest.fixture(scope="function", autouse=True)
    def setup_method(self, request, driver, db_manager: DatabaseManager):
        """Inicializa el driver de Selenium y el manejador de la base de datos para la prueba."""
        self.driver = driver
        self.db_manager = db_manager

    @allure.title("Prueba de flujo completo de reserva One-Way (Servicios, Asientos y Pago)")
    def test_oneway_booking_flow(self, origin, destination, adults, infants): 
        
        start_time = time.time()
        test_passed = False
        
        # 1. Inicialización de Page Objects
        home_page = HomePage(self.driver)
        select_flight_page = SelectFlightPage(self.driver)
        passenger_details_page = PassengerDetailsPage(self.driver)
        services_page = ServicesPage(self.driver)      
        seatmap_page = SeatmapPage(self.driver)        
        
        passenger_data = PASSENGER_DATA.copy()
        
        try:
            # 2. MÓDULO HOME (Búsqueda)
            with allure.step("Módulo HOME: Configuración de la búsqueda"):
                home_page.open()
                home_page.close_initial_popup()
                logging.info("Esperando 5 segundos para la estabilización inicial de la página.")
                time.sleep(5) 
                home_page.select_one_way()
                home_page.search_flight(origin, destination, "2026-12-01", adults, infants) 
            
            # 3. MÓDULO SELECT FLIGHT (Selección de Tarifa)
            with allure.step("Módulo SELECT FLIGHT: Seleccionar vuelo económico"):
                select_flight_page.validate_search_results(origin, destination) 
                select_flight_page.select_cheapest_flight()
                logging.info("Esperando 8 segundos para la carga completa del Módulo 3.")
                time.sleep(8)
                
            # 4. MÓDULO PASSENGER DETAILS (Llenado de Datos)
            with allure.step("Módulo PASSENGER DETAILS: Ingreso de datos del pasajero"):
                passenger_details_page.validate_passenger_details_page() 
                # La función fill_first_passenger_data contiene la pausa manual de 20s.
                passenger_details_page.fill_first_passenger_data(passenger_data) 
                
            # ------------------------------------------------
            # 5. MÓDULO SERVICIOS (REQUISITO: Equipajes) 
            # ------------------------------------------------
            with allure.step("Módulo SERVICIOS: Seleccionar Equipajes Normal y Deportivo"):
                services_page.select_required_baggage() 

            # ------------------------------------------------
            # 6. MÓDULO SEATMAP (REQUISITO: Asientos Impares) 
            # ------------------------------------------------
            with allure.step("Módulo SEATMAP: Seleccionar asientos para Pasajeros Impares"):
                seatmap_page.select_seats_for_odd_passengers()

            # ------------------------------------------------
            # 7. MÓDULO PAYMENTS (Finalización y Captura del cURL)
            # ------------------------------------------------
            with allure.step("Módulo PAYMENTS: Pausa para Captura Manual de API"):
                logging.critical("EL SCRIPT HA LLEGADO AL MÓDULO DE PAGOS. Por favor, proceda a CAPTURAR el cURL de Checkout/Payment.")
                time.sleep(30) 
            
            test_passed = True

        except Exception as e:
            allure.attach(self.driver.get_screenshot_as_png(), name="Fallo_Funcional", attachment_type=allure.attachment_type.PNG)
            logging.error(f"Fallo funcional en el flujo de reserva: {e}")
            raise 

        finally:
            end_time = time.time()
            duration = end_time - start_time
            # Almacenamiento del resultado en la Base de Datos (Requisito de la prueba técnica)
            self.db_manager.insert_result(
                test_name=f"test_oneway_booking_flow_{origin}-{destination}",
                result="PASS" if test_passed else "FAIL",
                duration=duration,
                origin=origin 
            )