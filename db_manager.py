import sqlite3
import logging
import time

class DBManager:
    """Clase para gestionar la conexión y operaciones con la base de datos SQLite para persistencia de resultados."""

    def __init__(self, db_name='test_results.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._setup_db()
        logging.info(f"Base de datos '{self.db_name}' lista y configurada.")

    def _setup_db(self):
        """Inicializa la base de datos y crea la tabla 'results' si no existe."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            
            # Creación de la tabla con todos los campos requeridos
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    test_name TEXT,
                    result TEXT,
                    duration REAL,
                    origin TEXT 
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error al configurar la base de datos: {e}")

    def insert_result(self, test_name: str, result: str, duration: float, origin: str):
        """Inserta el resultado de un test en la tabla 'results'."""
        if self.conn:
            try:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                self.cursor.execute(
                    "INSERT INTO results (timestamp, test_name, result, duration, origin) VALUES (?, ?, ?, ?, ?)",
                    (timestamp, test_name, result, duration, origin)
                )
                self.conn.commit()
                logging.info(f"Resultado de '{test_name}' insertado en la BD: {result}")
            except sqlite3.Error as e:
                logging.error(f"Error al insertar resultado en la base de datos: {e}")
            except Exception as e:
                logging.error(f"Error desconocido al insertar resultado: {e}")

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            logging.info(f"Conexión con '{self.db_name}' cerrada.")