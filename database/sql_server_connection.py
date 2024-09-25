import pyodbc
import os
import logging
from dotenv import load_dotenv

class SQLServerDatabase:
    def __init__(self, server, database, username, password):
        # Cargar las variables de entorno desde el archivo .env
        load_dotenv()

        self.server = os.getenv(server)  # Obtiene la variable desde el .env
        self.database = os.getenv(database)
        self.username = os.getenv(username)
        self.password = os.getenv(password)
        self.connection = None

    def connect(self):
        try:
            if self.connection is None:
                connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}"
                self.connection = pyodbc.connect(connection_string)
                print("Connected to SQL Server.")
            else:
                print("Already connected to SQL Server.")
        except pyodbc.Error as e:
            print(f"Error connecting to SQL Server: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from SQL Server.")
            self.connection = None
        else:
            print("No active connection to disconnect from.")

    def is_connected(self):
        return self.connection is not None

    def execute_query(self, query, return_results=True):
        try:
            if not self.is_connected():
                print("No active connection to execute the query.")
                return None

            with self.connection.cursor() as cursor:
                cursor.execute(query)

                if return_results:
                    results = cursor.fetchall()
                    return results
                else:
                    print(f"Número de filas afectadas: {cursor.rowcount}")
                    return None

        except pyodbc.Error as ex:
            print('Error executing query:', ex)
            return None

    def execute_query_with_params(self, query, params=None, return_results=True):
        try:
            if not self.is_connected():
                logging.error("No active connection to execute the query.")
                return None

            with self.connection.cursor() as cursor:
                cursor.execute(query, params)

                if return_results:
                    results = cursor.fetchall()
                    return results
                else:
                    logging.info(f"Número de filas afectadas: {cursor.rowcount}")
                    return None

        except Exception as e:
            logging.error(f"Error al ejecutar la consulta: {e}")
            return None

    # Nueva función para registrar errores
    def log_error(self, process_name, error_message, additional_info=None, path=None):
        try:
            if not self.is_connected():
                print("No active connection to log the error.")
                return

            query = "{CALL InsertErrorLog (?, ?, ?, ?)}"
            params = (process_name, error_message, additional_info, path)

            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                print("Error logged successfully.")

        except pyodbc.Error as ex:
            print(f"Error logging the error: {ex}")
