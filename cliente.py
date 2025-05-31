from conexion import obtener_conexion
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator

class VentanaClientes(QWidget):
    def __init__(self, conexion):
        super().__init__()
        self.conexion = conexion
        
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        self.setWindowTitle("Gestión de Clientes")
        
        # Widgets
        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Teléfono")
        self.telefono_input.setValidator(QIntValidator())
        self.telefono_input.setMaxLength(10)
        
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre completo")
        
        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Dirección")
        
        self.rfc_input = QLineEdit()
        self.rfc_input.setPlaceholderText("RFC (opcional)")
        self.rfc_input.setMaxLength(13)
        
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
        form_layout.addRow("Teléfono:", self.telefono_input)
        form_layout.addRow("Nombre:", self.nombre_input)
        form_layout.addRow("Dirección:", self.direccion_input)
        form_layout.addRow("RFC:", self.rfc_input)
        
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
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Teléfono", "Nombre", "Dirección", "RFC"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def agregar(self):
        conexion = None
        cursor = None
        try:
            telefono = self.telefono_input.text()
            nombre = self.nombre_input.text()
            direccion = self.direccion_input.text()
            rfc = self.rfc_input.text() or None
            
            if not telefono or not nombre or not direccion:
                QMessageBox.warning(self, "Campos vacíos", "Teléfono, nombre y dirección son obligatorios")
                return
                
            if len(telefono) != 10:
                QMessageBox.warning(self, "Teléfono inválido", "El teléfono debe tener 10 dígitos")
                return
                
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO clientes (telefono, nombre, direccion, rfc) VALUES (%s, %s, %s, %s)",
                (telefono, nombre, direccion, rfc))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Cliente agregado correctamente")
            self.cargar_datos()
            self.limpiar_campos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo agregar el cliente:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def actualizar(self):
        conexion = None
        cursor = None
        try:
            telefono = self.telefono_input.text()
            nombre = self.nombre_input.text()
            direccion = self.direccion_input.text()
            rfc = self.rfc_input.text() or None
            
            if not telefono or not nombre or not direccion:
                QMessageBox.warning(self, "Campos vacíos", "Teléfono, nombre y dirección son obligatorios")
                return
                
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE clientes SET nombre = %s, direccion = %s, rfc = %s WHERE telefono = %s",
                (nombre, direccion, rfc, telefono))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")
            self.cargar_datos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el cliente:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def eliminar(self):
        conexion = None
        cursor = None
        try:
            telefono = self.telefono_input.text()
            
            if not telefono:
                QMessageBox.warning(self, "Teléfono requerido", "Ingresa el teléfono del cliente a eliminar")
                return
                
            respuesta = QMessageBox.question(
                self, "Confirmar eliminación",
                f"¿Estás seguro de eliminar al cliente con teléfono {telefono}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if respuesta == QMessageBox.StandardButton.No:
                return
                
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "DELETE FROM clientes WHERE telefono = %s",
                (telefono,))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
            self.cargar_datos()
            self.limpiar_campos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el cliente:\n{e}")
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
            cursor.execute("SELECT telefono, nombre, direccion, rfc FROM clientes ORDER BY nombre")
            
            for row_idx, (telefono, nombre, direccion, rfc) in enumerate(cursor.fetchall()):
                self.tabla.insertRow(row_idx)
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(telefono))
                self.tabla.setItem(row_idx, 1, QTableWidgetItem(nombre))
                self.tabla.setItem(row_idx, 2, QTableWidgetItem(direccion))
                self.tabla.setItem(row_idx, 3, QTableWidgetItem(rfc if rfc else ""))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def cargar_datos_desde_tabla(self, item):
        row = item.row()
        self.telefono_input.setText(self.tabla.item(row, 0).text())
        self.nombre_input.setText(self.tabla.item(row, 1).text())
        self.direccion_input.setText(self.tabla.item(row, 2).text())
        self.rfc_input.setText(self.tabla.item(row, 3).text())

    def limpiar_campos(self):
        self.telefono_input.clear()
        self.nombre_input.clear()
        self.direccion_input.clear()
        self.rfc_input.clear()
        self.telefono_input.setFocus()