from conexion import obtener_conexion
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator

class VentanaProveedores(QWidget):
    def __init__(self, conexion):
        super().__init__()
        self.conexion = conexion
        
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        self.setWindowTitle("Gestión de Proveedores")
        
        # Widgets
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID Proveedor")
        self.id_input.setValidator(QIntValidator(1, 9999))
        
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del proveedor")
        
        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Teléfono")
        self.telefono_input.setValidator(QIntValidator())
        
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
        form_layout.addRow("Teléfono:", self.telefono_input)
        
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
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def agregar(self):
        conexion = None
        cursor = None
        try:
            id_prov = self.id_input.text()
            nombre = self.nombre_input.text()
            telefono = self.telefono_input.text()
            
            if not id_prov or not nombre or not telefono:
                QMessageBox.warning(self, "Campos vacíos", "Todos los campos son obligatorios")
                return
                
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO proveedores (id_proveedor, nombre, telefono) VALUES (%s, %s, %s)",
                (int(id_prov), nombre, telefono))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Proveedor agregado correctamente")
            self.cargar_datos()
            self.limpiar_campos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo agregar el proveedor:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def actualizar(self):
        conexion = None
        cursor = None
        try:
            id_prov = self.id_input.text()
            nombre = self.nombre_input.text()
            telefono = self.telefono_input.text()
            
            if not id_prov or not nombre or not telefono:
                QMessageBox.warning(self, "Campos vacíos", "Todos los campos son obligatorios")
                return
                
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE proveedores SET nombre = %s, telefono = %s WHERE id_proveedor = %s",
                (nombre, telefono, int(id_prov)))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Proveedor actualizado correctamente")
            self.cargar_datos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el proveedor:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def eliminar(self):
        conexion = None
        cursor = None
        try:
            id_prov = self.id_input.text()
            
            if not id_prov:
                QMessageBox.warning(self, "ID requerido", "Ingresa el ID del proveedor a eliminar")
                return
                
            respuesta = QMessageBox.question(
                self, "Confirmar eliminación",
                f"¿Estás seguro de eliminar al proveedor con ID {id_prov}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if respuesta == QMessageBox.StandardButton.No:
                return
                
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "DELETE FROM proveedores WHERE id_proveedor = %s",
                (int(id_prov),))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Proveedor eliminado correctamente")
            self.cargar_datos()
            self.limpiar_campos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el proveedor:\n{e}")
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
            cursor.execute("SELECT id_proveedor, nombre, telefono FROM proveedores ORDER BY id_proveedor")
            
            for row_idx, (id_prov, nombre, telefono) in enumerate(cursor.fetchall()):
                self.tabla.insertRow(row_idx)
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(id_prov)))
                self.tabla.setItem(row_idx, 1, QTableWidgetItem(nombre))
                self.tabla.setItem(row_idx, 2, QTableWidgetItem(telefono))
                
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
        self.telefono_input.setText(self.tabla.item(row, 2).text())

    def limpiar_campos(self):
        self.id_input.clear()
        self.nombre_input.clear()
        self.telefono_input.clear()
        self.id_input.setFocus()