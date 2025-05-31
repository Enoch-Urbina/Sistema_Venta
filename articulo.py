from conexion import obtener_conexion
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QIntValidator

class VentanaArticulos(QWidget):
    def __init__(self, conexion):
        super().__init__()
        self.conexion = conexion
        
        self.init_ui()
        self.cargar_combos()
        self.cargar_datos()

    def init_ui(self):
        self.setWindowTitle("Gestión de Artículos")
        
        # Widgets
        self.codigo_input = QLineEdit()
        self.codigo_input.setMaxLength(13)
        self.codigo_input.setPlaceholderText("Código de barras")
        
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del producto")
        
        self.precio_input = QLineEdit()
        self.precio_input.setPlaceholderText("Precio de venta")
        self.precio_input.setValidator(QDoubleValidator(0, 9999, 2))
        
        self.costo_input = QLineEdit()
        self.costo_input.setPlaceholderText("Costo")
        self.costo_input.setValidator(QDoubleValidator(0, 9999, 2))
        
        self.existencias_input = QLineEdit()
        self.existencias_input.setPlaceholderText("Existencias")
        self.existencias_input.setValidator(QIntValidator(0, 9999))
        
        self.reorden_input = QLineEdit()
        self.reorden_input.setPlaceholderText("Punto de reorden")
        
        self.categoria_combo = QComboBox()
        self.categoria_combo.setPlaceholderText("Seleccione categoría")
        
        self.unidad_combo = QComboBox()
        self.unidad_combo.setPlaceholderText("Seleccione unidad")
        
        self.proveedor_combo = QComboBox()
        self.proveedor_combo.setPlaceholderText("Seleccione proveedor")
        
        # Botones
        self.boton_agregar = QPushButton("➕ Agregar")
        self.boton_agregar.setStyleSheet("background-color: #4CAF50; color: white;")
        
        self.boton_actualizar = QPushButton("🔄 Actualizar")
        self.boton_actualizar.setStyleSheet("background-color: #2196F3; color: white;")
        
        self.boton_limpiar = QPushButton("🧹 Limpiar")
        self.boton_limpiar.setStyleSheet("background-color: #f44336; color: white;")
        
        # Tabla
        self.tabla = QTableWidget()
        self.configurar_tabla()
        
        # Layouts
        form_layout = QFormLayout()
        form_layout.addRow("Código:", self.codigo_input)
        form_layout.addRow("Nombre:", self.nombre_input)
        form_layout.addRow("Precio:", self.precio_input)
        form_layout.addRow("Costo:", self.costo_input)
        form_layout.addRow("Existencias:", self.existencias_input)
        form_layout.addRow("Reorden:", self.reorden_input)
        form_layout.addRow("Categoría:", self.categoria_combo)
        form_layout.addRow("Proveedor:", self.proveedor_combo)
        form_layout.addRow("Unidad:", self.unidad_combo)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.boton_agregar)
        button_layout.addWidget(self.boton_actualizar)
        button_layout.addWidget(self.boton_limpiar)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tabla)
        
        self.setLayout(main_layout)
        
        # Conexiones
        self.boton_agregar.clicked.connect(self.agregar)
        self.boton_actualizar.clicked.connect(self.cargar_datos)
        self.boton_limpiar.clicked.connect(self.limpiar_campos)
        self.tabla.itemDoubleClicked.connect(self.cargar_datos_desde_tabla)

    def configurar_tabla(self):
        self.tabla.setColumnCount(9)
        self.tabla.setHorizontalHeaderLabels([
            "Código", "Nombre", "Precio", "Costo", "Existencias",
            "Reorden", "Categoría", "Proveedor", "Unidad"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def cargar_combos(self):
        conexion = None
        cursor = None
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Agregar item vacío al inicio de cada combo
            self.categoria_combo.addItem("", None)
            cursor.execute("SELECT id_categorias, nombre FROM categorias")
            for id_cat, nombre in cursor.fetchall():
                self.categoria_combo.addItem(nombre, id_cat)

            self.proveedor_combo.addItem("", None)
            cursor.execute("SELECT id_proveedor, nombre FROM proveedores")
            for id_prov, nombre in cursor.fetchall():
                self.proveedor_combo.addItem(nombre, id_prov)

            self.unidad_combo.addItem("", None)
            cursor.execute("SELECT id_unidad, nombre FROM unidad")
            for id_uni, nombre in cursor.fetchall():
                self.unidad_combo.addItem(nombre, id_uni)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar combos:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def agregar(self):
        conexion = None
        cursor = None
        try:
            # Validación de campos
            campos = {
                "código": self.codigo_input.text(),
                "nombre": self.nombre_input.text(),
                "precio": self.precio_input.text(),
                "costo": self.costo_input.text(),
                "existencias": self.existencias_input.text(),
                "reorden": self.reorden_input.text(),
                "categoría": self.categoria_combo.currentData(),
                "proveedor": self.proveedor_combo.currentData(),
                "unidad": self.unidad_combo.currentData()
            }
            
            for campo, valor in campos.items():
                if not valor and campo not in ["reorden"]:  # Reorden es opcional
                    QMessageBox.warning(self, "Campo vacío", f"El campo {campo} es obligatorio")
                    return
            
            # Obtener valores
            codigo = campos["código"]
            nombre = campos["nombre"]
            precio = float(campos["precio"])
            costo = float(campos["costo"])
            existencias = int(campos["existencias"])
            reorden = campos["reorden"] if campos["reorden"] else "0"  # Valor por defecto si está vacío
            id_categoria = campos["categoría"]
            id_proveedor = campos["proveedor"]
            id_unidad = campos["unidad"]

            # Insertar en la base de datos
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            query = """
                INSERT INTO articulos 
                (codigo, nombre, precio, costo, existencias, reorden, id_categorias, id_proveedor, id_unidad)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (codigo, nombre, precio, costo, existencias, reorden, id_categoria, id_proveedor, id_unidad)
            cursor.execute(query, valores)
            conexion.commit()
            
            QMessageBox.information(self, "Éxito", "Artículo agregado correctamente")
            self.cargar_datos()
            self.limpiar_campos()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo agregar el artículo:\n{e}")
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
            cursor.execute("""
                SELECT a.codigo, a.nombre, a.precio, a.costo, a.existencias, a.reorden,
                       c.nombre, p.nombre, u.nombre
                FROM articulos a
                JOIN categorias c ON a.id_categorias = c.id_categorias
                JOIN proveedores p ON a.id_proveedor = p.id_proveedor
                JOIN unidad u ON a.id_unidad = u.id_unidad
                ORDER BY a.nombre
            """)
            
            for row_idx, row in enumerate(cursor.fetchall()):
                self.tabla.insertRow(row_idx)
                for col_idx, dato in enumerate(row):
                    item = QTableWidgetItem(str(dato))
                    if col_idx in (2, 3):  # Columnas de precio y costo
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                        if col_idx == 2:  # Precio
                            item.setText(f"${float(dato):.2f}")
                        elif col_idx == 3:  # Costo
                            item.setText(f"${float(dato):.2f}")
                    self.tabla.setItem(row_idx, col_idx, item)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def cargar_datos_desde_tabla(self, item):
        row = item.row()
        self.codigo_input.setText(self.tabla.item(row, 0).text())
        self.nombre_input.setText(self.tabla.item(row, 1).text())
        self.precio_input.setText(self.tabla.item(row, 2).text().replace('$', ''))
        self.costo_input.setText(self.tabla.item(row, 3).text().replace('$', ''))
        self.existencias_input.setText(self.tabla.item(row, 4).text())
        self.reorden_input.setText(self.tabla.item(row, 5).text())
        
        # Establecer los combos según los valores
        categoria = self.tabla.item(row, 6).text()
        proveedor = self.tabla.item(row, 7).text()
        unidad = self.tabla.item(row, 8).text()
        
        index = self.categoria_combo.findText(categoria)
        if index >= 0:
            self.categoria_combo.setCurrentIndex(index)
            
        index = self.proveedor_combo.findText(proveedor)
        if index >= 0:
            self.proveedor_combo.setCurrentIndex(index)
            
        index = self.unidad_combo.findText(unidad)
        if index >= 0:
            self.unidad_combo.setCurrentIndex(index)

    def limpiar_campos(self):
        self.codigo_input.clear()
        self.nombre_input.clear()
        self.precio_input.clear()
        self.costo_input.clear()
        self.existencias_input.clear()
        self.reorden_input.clear()
        self.categoria_combo.setCurrentIndex(0)  # Selecciona el item vacío
        self.proveedor_combo.setCurrentIndex(0)  # Selecciona el item vacío
        self.unidad_combo.setCurrentIndex(0)  # Selecciona el item vacío
        self.codigo_input.setFocus()