import mysql.connector
from mysql.connector import Error
from PyQt6.QtWidgets import QMessageBox

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="BodegaAurrera",
            autocommit=False
        )
        return conexion
    except Error as e:
        QMessageBox.critical(
            None, 
            "Error de conexión", 
            f"No se pudo conectar a la base de datos:\n{str(e)}"
        )
        raise