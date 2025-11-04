# utils/database_manager.py
import sqlite3
import logging
# 'os' no es estrictamente necesario para esta lógica, pero se mantiene si se usa en otro contexto.
# import os 

class DatabaseManager:
    """
    Clase para manejar la conexión y operaciones con la base de datos SQLite.
    Se utiliza para persistir los resultados de las pruebas de automatización.
    """

    def __init__(self, db_name="test_results.db"):
        self.db_name = db_name
        self._initialize_db()

    def _initialize_db(self):
        """Crea la base de datos SQLite y la tabla 'test_results' si no existen."""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Definición del esquema de la tabla de resultados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT NOT NULL,
                    result TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration REAL,
                    origin TEXT
                )
            """)
            conn.commit()
            conn.close()
            logging.info(f"Base de datos '{self.db_name}' inicializada.")
        except Exception as e:
            logging.error(f"Error durante la inicialización de la BD: {e}")

    def insert_result(self, test_name: str, result: str, duration: float, origin: str):
        """Inserta el resultado de una prueba en la tabla 'test_results'."""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO test_results (test_name, result, duration, origin)
                VALUES (?, ?, ?, ?)
            """, (test_name, result, duration, origin))
            
            conn.commit()
            conn.close()
            logging.info(f"Resultado de prueba insertado: {test_name} - {result}")
        except Exception as e:
            logging.error(f"Error al insertar resultado en la BD: {e}")

    def get_all_results(self):
        """Recupera todos los resultados almacenados de la base de datos."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_results")
        results = cursor.fetchall()
        conn.close()
        return results