from conexion import obtener_conexion
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator

class VentanaEmpleados(QWidget):
    def __init__(self, conexion):
        super().__init__()
        self.conexion = conexion
        
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        self.setWindowTitle("Gestión de Empleados")
        
        # Widgets
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID Empleado")
        self.id_input.setValidator(QIntValidator(1, 9999))
        
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre completo")
        
        self.genero_combo = QComboBox()
        self.genero_combo.addItems(["Masculino", "Femenino"])
        
        self.puesto_combo = QComboBox()
        self.puesto_combo.addItems(["Administrador", "Encargado", "Cajero"])
        
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
        form_layout.addRow("Género:", self.genero_combo)
        form_layout.addRow("Puesto:", self.puesto_combo)
        
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
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Género", "Puesto"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def agregar(self):
        conexion = None
        cursor = None
        try:
            id_emp = self.id_input.text()
            nombre = self.nombre_input.text()
            
            if not id_emp or not nombre:
                QMessageBox.warning(self, "Campos vacíos", "ID y nombre son obligatorios")
                return
                
            genero = self.genero_combo.currentText()[0]  # 'M' o 'F'
            puesto = self.puesto_combo.currentText().lower()
            
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO empleado (id_empleado, nombre, genero, puesto) VALUES (%s, %s, %s, %s)",
                (int(id_emp), nombre, genero, puesto))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Empleado agregado correctamente")
            self.cargar_datos()
            self.limpiar_campos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo agregar el empleado:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def actualizar(self):
        conexion = None
        cursor = None
        try:
            id_emp = self.id_input.text()
            nombre = self.nombre_input.text()
            
            if not id_emp or not nombre:
                QMessageBox.warning(self, "Campos vacíos", "ID y nombre son obligatorios")
                return
                
            genero = self.genero_combo.currentText()[0]  # 'M' o 'F'
            puesto = self.puesto_combo.currentText().lower()
            
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE empleado SET nombre = %s, genero = %s, puesto = %s WHERE id_empleado = %s",
                (nombre, genero, puesto, int(id_emp)))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Empleado actualizado correctamente")
            self.cargar_datos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el empleado:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def eliminar(self):
        conexion = None
        cursor = None
        try:
            id_emp = self.id_input.text()
            
            if not id_emp:
                QMessageBox.warning(self, "ID requerido", "Ingresa el ID del empleado a eliminar")
                return
                
            respuesta = QMessageBox.question(
                self, "Confirmar eliminación",
                f"¿Estás seguro de eliminar al empleado con ID {id_emp}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if respuesta == QMessageBox.StandardButton.No:
                return
                
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "DELETE FROM empleado WHERE id_empleado = %s",
                (int(id_emp),))
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Empleado eliminado correctamente")
            self.cargar_datos()
            self.limpiar_campos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el empleado:\n{e}")
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
            cursor.execute("SELECT id_empleado, nombre, genero, puesto FROM empleado ORDER BY id_empleado")
            
            for row_idx, (id_emp, nombre, genero, puesto) in enumerate(cursor.fetchall()):
                self.tabla.insertRow(row_idx)
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(id_emp)))
                self.tabla.setItem(row_idx, 1, QTableWidgetItem(nombre))
                self.tabla.setItem(row_idx, 2, QTableWidgetItem("Masculino" if genero == "M" else "Femenino"))
                self.tabla.setItem(row_idx, 3, QTableWidgetItem(puesto.capitalize()))
                
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
        
        genero = self.tabla.item(row, 2).text()
        index = self.genero_combo.findText(genero)
        if index >= 0:
            self.genero_combo.setCurrentIndex(index)
            
        puesto = self.tabla.item(row, 3).text()
        index = self.puesto_combo.findText(puesto)
        if index >= 0:
            self.puesto_combo.setCurrentIndex(index)

    def limpiar_campos(self):
        self.id_input.clear()
        self.nombre_input.clear()
        self.genero_combo.setCurrentIndex(0)
        self.puesto_combo.setCurrentIndex(0)
        self.id_input.setFocus()