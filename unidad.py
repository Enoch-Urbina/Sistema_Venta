from conexion import obtener_conexion
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator

class VentanaUnidad(QWidget):
    def __init__(self, conexion):
        super().__init__()
        self.conexion = conexion
        
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        self.setWindowTitle("Gestión de Unidades")
        
        # Widgets
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID Unidad")
        self.id_input.setValidator(QIntValidator(1, 9999))
        
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre de la unidad")
        
        # Botones
        self.boton_agregar = QPushButton("➕ Agregar")
        self.boton_agregar.setStyleSheet("background-color: #4CAF50; color: white;")
        
        self.boton_actualizar = QPushButton("🔄 Actualizar")
        self.boton_actualizar.setStyleSheet("background-color: #2196F3; color: white;")
        
        self.boton_eliminar = QPushButton("🗑️ Eliminar")
        self.boton_eliminar.setStyleSheet("background-color: #f44336; color: white;")
        
        self.boton_limpiar = QPushButton("🧹 Limpiar")
        self.boton_limpiar.setStyleSheet("background-color: #FFC107; color: black;")
        
        # Tabla
        self.tabla = QTableWidget()
        self.configurar_tabla()
        
        # Layouts
        form_layout = QFormLayout()
        form_layout.addRow("ID:", self.id_input)
        form_layout.addRow("Nombre:", self.nombre_input)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.boton_agregar)
        button_layout.addWidget(self.boton_actualizar)
        button_layout.addWidget(self.boton_eliminar)
        button_layout.addWidget(self.boton_limpiar)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tabla)
        
        self.setLayout(main_layout)
        
        # Conexiones
        self.boton_agregar.clicked.connect(self.agregar)
        self.boton_actualizar.clicked.connect(self.actualizar)
        self.boton_eliminar.clicked.connect(self.eliminar)
        self.boton_limpiar.clicked.connect(self.limpiar_campos)
        self.tabla.itemDoubleClicked.connect(self.cargar_datos_desde_tabla)

    def configurar_tabla(self):
        self.tabla.setColumnCount(2)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def agregar(self):
        conexion = None
        cursor = None
        try:
            id_uni = self.id_input.text()
            nombre = self.nombre_input.text()
            
            if not id_uni or not nombre:
                QMessageBox.warning(self, "Campos vacíos", "Todos los campos son obligatorios")
                return
                
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO unidad (id_unidad, nombre) VALUES (%s, %s)",
                (int(id_uni), nombre))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Unidad agregada correctamente")
            self.cargar_datos()
            self.limpiar_campos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo agregar la unidad:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def actualizar(self):
        conexion = None
        cursor = None
        try:
            id_uni = self.id_input.text()
            nombre = self.nombre_input.text()
            
            if not id_uni or not nombre:
                QMessageBox.warning(self, "Campos vacíos", "Todos los campos son obligatorios")
                return
                
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE unidad SET nombre = %s WHERE id_unidad = %s",
                (nombre, int(id_uni)))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Unidad actualizada correctamente")
            self.cargar_datos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar la unidad:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def eliminar(self):
        conexion = None
        cursor = None
        try:
            id_uni = self.id_input.text()
            
            if not id_uni:
                QMessageBox.warning(self, "ID requerido", "Ingresa el ID de la unidad a eliminar")
                return
                
            respuesta = QMessageBox.question(
                self, "Confirmar eliminación",
                f"¿Estás seguro de eliminar la unidad con ID {id_uni}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if respuesta == QMessageBox.StandardButton.No:
                return
                
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "DELETE FROM unidad WHERE id_unidad = %s",
                (int(id_uni),))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Unidad eliminada correctamente")
            self.cargar_datos()
            self.limpiar_campos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo eliminar la unidad:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def cargar_datos(self):
        conexion = None
        cursor = None
        try:
            self.tabla.setRowCount(0)
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_unidad, nombre FROM unidad ORDER BY id_unidad")
            
            for row_idx, (id_uni, nombre) in enumerate(cursor.fetchall()):
                self.tabla.insertRow(row_idx)
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(id_uni)))
                self.tabla.setItem(row_idx, 1, QTableWidgetItem(nombre))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def cargar_datos_desde_tabla(self, item):
        row = item.row()
        self.id_input.setText(self.tabla.item(row, 0).text())
        self.nombre_input.setText(self.tabla.item(row, 1).text())

    def limpiar_campos(self):
        self.id_input.clear()
        self.nombre_input.clear()
        self.id_input.setFocus()