from conexion import obtener_conexion
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QSpinBox, QLabel, QGroupBox,
    QDialog, QListWidget, QAbstractItemView, QRadioButton,
    QButtonGroup, QDialogButtonBox, QComboBox,QCheckBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QEvent
from PyQt6.QtGui import QDoubleValidator, QIntValidator, QKeyEvent
from datetime import datetime
import json

class SeleccionProductosDialog(QDialog):
    producto_seleccionado = pyqtSignal(str)

    def __init__(self, conexion):
        super().__init__()
        self.conexion = conexion
        self.setWindowTitle("Seleccionar Producto")
        self.resize(500, 400)
        
        self.lista_productos = QListWidget()
        self.lista_productos.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.lista_productos.doubleClicked.connect(self.seleccionar_producto)
        
        self.boton_aceptar = QPushButton("Aceptar")
        self.boton_aceptar.clicked.connect(self.seleccionar_producto)
        
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_cancelar.clicked.connect(self.reject)
        
        layout = QVBoxLayout()
        layout.addWidget(self.lista_productos)
        
        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.boton_aceptar)
        botones_layout.addWidget(self.boton_cancelar)
        
        layout.addLayout(botones_layout)
        self.setLayout(layout)
        
        self.cargar_productos()

    def cargar_productos(self):
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            cursor.execute("""
                SELECT a.codigo, a.nombre, a.precio, a.existencias 
                FROM articulos a 
                ORDER BY a.nombre
            """)
            
            for codigo, nombre, precio, existencias in cursor.fetchall():
                item_text = f"{codigo} - {nombre} - ${precio:.2f} - Stock: {existencias}"
                item = QTableWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, codigo)
                self.lista_productos.addItem(item_text)
                self.lista_productos.item(self.lista_productos.count()-1).setData(Qt.ItemDataRole.UserRole, codigo)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar productos:\n{e}")
        finally:
            cursor.close()
            conexion.close()

    def seleccionar_producto(self):
        selected = self.lista_productos.currentRow()
        if selected >= 0:
            codigo = self.lista_productos.item(selected).data(Qt.ItemDataRole.UserRole)
            self.producto_seleccionado.emit(codigo)
            self.accept()

class FacturacionDialog(QDialog):
    def __init__(self, cliente_actual, es_cliente_general=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Datos de Facturación")
        self.resize(500, 400)
        self.es_cliente_general = es_cliente_general
        
        # Widgets
        self.rfc_input = QLineEdit()
        self.rfc_input.setPlaceholderText("RFC del cliente")
        self.rfc_input.setMaxLength(13)
        
        self.razon_social_input = QLineEdit()
        self.razon_social_input.setPlaceholderText("Razón social (obligatorio)")
        
        self.direccion_fiscal_input = QLineEdit()
        self.direccion_fiscal_input.setPlaceholderText("Dirección fiscal (obligatorio)")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email para factura (obligatorio)")
        
        # Si es cliente registrado, autocompletar datos
        if cliente_actual and not es_cliente_general:
            if 'rfc' in cliente_actual and cliente_actual['rfc']:
                self.rfc_input.setText(cliente_actual['rfc'])
            if 'nombre' in cliente_actual and cliente_actual['nombre']:
                self.razon_social_input.setText(cliente_actual['nombre'])
            if 'direccion' in cliente_actual and cliente_actual['direccion']:
                self.direccion_fiscal_input.setText(cliente_actual['direccion'])
            if 'email' in cliente_actual and cliente_actual['email']:
                self.email_input.setText(cliente_actual['email'])
        
        # Botones
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.validar_datos)
        self.button_box.rejected.connect(self.reject)
        
        # Layout
        layout = QFormLayout()
        layout.addRow("RFC (obligatorio):", self.rfc_input)
        layout.addRow("Razón Social (obligatorio):", self.razon_social_input)
        layout.addRow("Dirección Fiscal (obligatorio):", self.direccion_fiscal_input)
        layout.addRow("Email (obligatorio):", self.email_input)
        
        if self.es_cliente_general:
            self.registrar_cliente_check = QCheckBox("Registrar como nuevo cliente")
            layout.addRow(self.registrar_cliente_check)
            
            self.telefono_cliente_input = QLineEdit()
            self.telefono_cliente_input.setPlaceholderText("Teléfono del nuevo cliente")
            self.telefono_cliente_input.setValidator(QIntValidator())
            self.telefono_cliente_input.setMaxLength(10)
            layout.addRow("Teléfono:", self.telefono_cliente_input)
            
            self.registrar_cliente_check.toggled.connect(self.toggle_registro_cliente)
            self.telefono_cliente_input.setEnabled(False)
        
        layout.addRow(self.button_box)
        self.setLayout(layout)
    
    def toggle_registro_cliente(self, checked):
        self.telefono_cliente_input.setEnabled(checked)
        if not checked:
            self.telefono_cliente_input.clear()
    
    def validar_datos(self):
        # Validar que todos los campos obligatorios estén completos
        if (not self.rfc_input.text() or len(self.rfc_input.text()) < 12 or
            not self.razon_social_input.text() or
            not self.direccion_fiscal_input.text() or
            not self.email_input.text()):
            QMessageBox.warning(self, "Datos incompletos", 
                              "Todos los campos de facturación son obligatorios")
            return
        
        # Validar formato de email
        if "@" not in self.email_input.text() or "." not in self.email_input.text():
            QMessageBox.warning(self, "Email inválido", 
                              "Ingrese un email válido para la factura")
            return
        
        # Si es cliente general y quiere registrar, validar teléfono
        if self.es_cliente_general and self.registrar_cliente_check.isChecked():
            if len(self.telefono_cliente_input.text()) != 10:
                QMessageBox.warning(self, "Teléfono inválido", 
                                  "El teléfono debe tener 10 dígitos")
                return
        
        self.accept()
    
    def get_datos_factura(self):
        datos = {
            'rfc': self.rfc_input.text(),
            'razon_social': self.razon_social_input.text(),
            'direccion_fiscal': self.direccion_fiscal_input.text(),
            'email': self.email_input.text()
        }
        
        if self.es_cliente_general and self.registrar_cliente_check.isChecked():
            datos['registrar_cliente'] = True
            datos['telefono'] = self.telefono_cliente_input.text()
        else:
            datos['registrar_cliente'] = False
        
        return datos

class VentanaVenta(QWidget):
    def __init__(self, conexion):
        super().__init__()
        self.conexion = conexion
        self.productos_agregados = []
        self.cliente_actual = None
        self.venta_pausada = None
        
        self.init_ui()
        self.installEventFilter(self)

    def init_ui(self):
        self.setWindowTitle("Registro de Ventas")
        
        # Widgets para cliente
        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Teléfono del cliente (opcional)")
        self.telefono_input.setValidator(QIntValidator())
        self.telefono_input.setMaxLength(10)
        
        self.boton_buscar_cliente = QPushButton("🔍 Buscar")
        self.boton_buscar_cliente.setStyleSheet("background-color: #9E9E9E; color: white;")
        
        self.cliente_info = QLabel("Cliente: General")
        self.cliente_info.setStyleSheet("font-weight: bold;")
        
        # Widgets para productos
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código del producto (escáner)")
        self.codigo_input.setMaxLength(13)
        
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setRange(1, 999)
        self.cantidad_spin.setValue(1)
        
        # Widget para ID de empleado
        self.id_empleado_input = QLineEdit()
        self.id_empleado_input.setPlaceholderText("ID del empleado")
        self.id_empleado_input.setValidator(QIntValidator(1, 9999))
        
        # Label para mostrar nombre del empleado
        self.empleado_nombre_label = QLabel("Empleado: No asignado")
        self.empleado_nombre_label.setStyleSheet("font-weight: bold;")
        
         # Método de pago
        self.metodo_pago_group = QButtonGroup()
        self.radio_efectivo = QRadioButton("Efectivo")
        self.radio_tarjeta = QRadioButton("Tarjeta")
        # Eliminamos la línea que establecía efectivo como checked por defecto
        self.metodo_pago_group.addButton(self.radio_efectivo)
        self.metodo_pago_group.addButton(self.radio_tarjeta)
        
        self.monto_efectivo = QLineEdit()
        self.monto_efectivo.setPlaceholderText("Monto recibido")
        self.monto_efectivo.setValidator(QDoubleValidator(0, 99999, 2))
        self.monto_efectivo.setEnabled(False)  # Deshabilitado inicialmente
        self.monto_efectivo.hide()
        
        self.label_cambio = QLabel("Cambio: $0.00")
        self.label_cambio.setStyleSheet("font-weight: bold; color: #2E7D32;")
        self.label_cambio.hide()
        
        # Botones
        self.boton_agregar = QPushButton("➕ Agregar producto")
        self.boton_agregar.setStyleSheet("background-color: #4CAF50; color: white;")
        
        self.boton_quitar = QPushButton("➖ Quitar producto")
        self.boton_quitar.setStyleSheet("background-color: #f44336; color: white;")
        
        self.boton_seleccionar_producto = QPushButton("📋 Seleccionar producto")
        self.boton_seleccionar_producto.setStyleSheet("background-color: #673AB7; color: white;")
        
        self.boton_pausar = QPushButton("⏸ Pausar venta")
        self.boton_pausar.setStyleSheet("background-color: #FF9800; color: white;")
        
        self.boton_continuar = QPushButton("▶ Continuar venta")
        self.boton_continuar.setStyleSheet("background-color: #FF9800; color: white;")
        self.boton_continuar.hide()
        
        self.boton_pagar = QPushButton("💳 Pagar")
        self.boton_pagar.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        
        self.boton_limpiar = QPushButton("🧹 Nueva venta")
        self.boton_limpiar.setStyleSheet("background-color: #FFC107; color: black;")
        
        # Tabla de productos
        self.tabla_productos = QTableWidget()
        self.configurar_tabla()
        
        # Información de la venta
        self.label_total = QLabel("Total: $0.00")
        self.label_total.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E7D32;")
        
        # Layouts
        cliente_layout = QHBoxLayout()
        cliente_layout.addWidget(QLabel("Teléfono cliente:"))
        cliente_layout.addWidget(self.telefono_input)
        cliente_layout.addWidget(self.boton_buscar_cliente)
        
        cliente_group = QGroupBox("Datos del Cliente")
        cliente_group.setLayout(QVBoxLayout())
        cliente_group.layout().addLayout(cliente_layout)
        cliente_group.layout().addWidget(self.cliente_info)
        
        producto_layout = QHBoxLayout()
        producto_layout.addWidget(QLabel("Código producto:"))
        producto_layout.addWidget(self.codigo_input)
        producto_layout.addWidget(QLabel("Cantidad:"))
        producto_layout.addWidget(self.cantidad_spin)
        producto_layout.addWidget(self.boton_agregar)
        producto_layout.addWidget(self.boton_quitar)
        producto_layout.addWidget(self.boton_seleccionar_producto)
        
        producto_group = QGroupBox("Agregar Productos")
        producto_group.setLayout(producto_layout)
        
        empleado_layout = QHBoxLayout()
        empleado_layout.addWidget(QLabel("ID Empleado:"))
        empleado_layout.addWidget(self.id_empleado_input)
        empleado_layout.addWidget(self.empleado_nombre_label)
        empleado_layout.addStretch()
        
        empleado_group = QGroupBox("Datos del Empleado")
        empleado_group.setLayout(empleado_layout)
        
        pago_layout = QHBoxLayout()
        pago_layout.addWidget(QLabel("Método de pago:"))
        pago_layout.addWidget(self.radio_efectivo)
        pago_layout.addWidget(self.radio_tarjeta)
        pago_layout.addWidget(self.monto_efectivo)
        pago_layout.addWidget(self.label_cambio)
        pago_layout.addStretch()
        
        pago_group = QGroupBox("Información de Pago")
        pago_group.setLayout(pago_layout)
        
        acciones_layout = QHBoxLayout()
        acciones_layout.addWidget(self.boton_pausar)
        acciones_layout.addWidget(self.boton_continuar)
        acciones_layout.addWidget(self.boton_pagar)
        acciones_layout.addWidget(self.boton_limpiar)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(cliente_group)
        main_layout.addWidget(empleado_group)
        main_layout.addWidget(producto_group)
        main_layout.addWidget(self.tabla_productos)
        main_layout.addWidget(pago_group)
        main_layout.addWidget(self.label_total)
        main_layout.addLayout(acciones_layout)
        
        self.setLayout(main_layout)
        
        # Variables para el escaneo de códigos de barras
        self.codigo_escaneo = ""
        self.temporizador_escaneo = None
        
        # Conexiones
        self.boton_buscar_cliente.clicked.connect(self.buscar_cliente)
        self.telefono_input.returnPressed.connect(self.buscar_cliente)
        self.boton_agregar.clicked.connect(self.agregar_producto)
        self.boton_quitar.clicked.connect(self.quitar_producto)
        self.boton_pagar.clicked.connect(self.procesar_pago)
        self.boton_limpiar.clicked.connect(self.limpiar_venta)
        self.codigo_input.returnPressed.connect(self.agregar_producto)
        self.boton_seleccionar_producto.clicked.connect(self.mostrar_seleccion_productos)
        self.boton_pausar.clicked.connect(self.pausar_venta)
        self.boton_continuar.clicked.connect(self.continuar_venta)
        self.radio_efectivo.toggled.connect(self.actualizar_metodo_pago)
        self.monto_efectivo.textChanged.connect(self.calcular_cambio)
        self.id_empleado_input.textChanged.connect(self.actualizar_nombre_empleado)

    def actualizar_nombre_empleado(self):
        id_empleado = self.id_empleado_input.text()
        if not id_empleado:
            self.empleado_nombre_label.setText("Empleado: No asignado")
            return
            
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre FROM empleado WHERE id_empleado = %s", (int(id_empleado),))
            empleado = cursor.fetchone()
            
            if empleado:
                self.empleado_nombre_label.setText(f"Empleado: {empleado[0]}")
            else:
                self.empleado_nombre_label.setText("Empleado: No encontrado")
        except Exception as e:
            self.empleado_nombre_label.setText("Empleado: Error al buscar")
        finally:
            cursor.close()
            conexion.close()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() in range(Qt.Key.Key_0, Qt.Key.Key_9 + 1) or event.key() == Qt.Key.Key_Enter:
                if event.key() == Qt.Key.Key_Enter:
                    if len(self.codigo_escaneo) > 0:
                        self.codigo_input.setText(self.codigo_escaneo)
                        self.agregar_producto()
                        self.codigo_escaneo = ""
                    return True
                else:
                    self.codigo_escaneo += event.text()
                    if self.temporizador_escaneo:
                        self.killTimer(self.temporizador_escaneo)
                    self.temporizador_escaneo = self.startTimer(300)
                    return True
        return super().eventFilter(obj, event)

    def timerEvent(self, event):
        if event.timerId() == self.temporizador_escaneo:
            self.killTimer(self.temporizador_escaneo)
            self.temporizador_escaneo = None
            self.codigo_escaneo = ""
        super().timerEvent(event)

    def configurar_tabla(self):
        self.tabla_productos.setColumnCount(6)
        self.tabla_productos.setHorizontalHeaderLabels([
            "Código", "Nombre", "Precio", "Cantidad", "Subtotal", "Acciones"
        ])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_productos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        self.tabla_productos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_productos.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

    def actualizar_metodo_pago(self):
        # Modificamos este método para manejar cuando no hay selección
        if not self.radio_efectivo.isChecked() and not self.radio_tarjeta.isChecked():
            self.monto_efectivo.hide()
            self.label_cambio.hide()
            self.monto_efectivo.setEnabled(False)
        elif self.radio_efectivo.isChecked():
            self.monto_efectivo.show()
            self.label_cambio.show()
            self.monto_efectivo.setEnabled(True)
            self.calcular_cambio()
        else:  # Tarjeta
            self.monto_efectivo.hide()
            self.label_cambio.hide()

    def calcular_cambio(self):
        if not self.radio_efectivo.isChecked():
            return
            
        total = sum(cant * precio for _, _, cant, precio in self.productos_agregados)
        monto_recibido = float(self.monto_efectivo.text() or 0)
        
        if monto_recibido >= total:
            cambio = monto_recibido - total
            self.label_cambio.setText(f"Cambio: ${cambio:.2f}")
            self.label_cambio.setStyleSheet("font-weight: bold; color: #2E7D32;")
        else:
            faltante = total - monto_recibido
            self.label_cambio.setText(f"Faltante: ${faltante:.2f}")
            self.label_cambio.setStyleSheet("font-weight: bold; color: #f44336;")

    def mostrar_seleccion_productos(self):
        dialog = SeleccionProductosDialog(self.conexion)
        dialog.producto_seleccionado.connect(self.producto_seleccionado_handler)
        dialog.exec()

    def producto_seleccionado_handler(self, codigo):
        self.codigo_input.setText(codigo)
        self.codigo_input.setFocus()

    def buscar_cliente(self):
        telefono = self.telefono_input.text()
        
        if not telefono:
            self.cliente_actual = None
            self.cliente_info.setText("Cliente: General (0000000000)")
            return
            
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            cursor.execute("""
                SELECT nombre, direccion, rfc 
                FROM clientes 
                WHERE telefono = %s
            """, (telefono,))
            
            cliente = cursor.fetchone()
            
            if cliente:
                nombre, direccion, rfc = cliente
                self.cliente_actual = {
                    'telefono': telefono,
                    'nombre': nombre,
                    'direccion': direccion,
                    'rfc': rfc
                }
                info = f"Cliente: {nombre}"
                if rfc:
                    info += f" (RFC: {rfc})"
                self.cliente_info.setText(info)
            else:
                self.cliente_actual = None
                self.cliente_info.setText("Cliente: General (0000000000)")
                QMessageBox.information(self, "Cliente no encontrado", 
                                    "Se usará cliente general para esta venta")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar cliente:\n{e}")
        finally:
            cursor.close()
            conexion.close()

    def agregar_producto(self):
        codigo = self.codigo_input.text()
        cantidad = self.cantidad_spin.value()
        
        if not codigo:
            QMessageBox.warning(self, "Código vacío", "Ingresa un código de producto")
            return
            
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            # Verificar si el producto ya está en el carrito
            producto_existente = None
            for idx, (cod, nombre, cant, precio) in enumerate(self.productos_agregados):
                if cod == codigo:
                    producto_existente = (idx, nombre, precio)
                    break
            
            # Si el producto ya existe, actualizamos la cantidad
            if producto_existente:
                idx, nombre, precio = producto_existente
                nueva_cantidad = self.productos_agregados[idx][2] + cantidad
                
                # Verificar stock
                cursor.execute("SELECT existencias FROM articulos WHERE codigo = %s", (codigo,))
                existencias = cursor.fetchone()[0]
                
                if existencias < nueva_cantidad:
                    QMessageBox.warning(
                        self, 
                        "Stock insuficiente", 
                        f"Stock actual: {existencias}. No hay suficientes existencias para {nueva_cantidad} unidades."
                    )
                    return
                
                self.productos_agregados[idx] = (codigo, nombre, nueva_cantidad, precio)
                self.actualizar_tabla()
                self.codigo_input.clear()
                self.codigo_input.setFocus()
                return
            
            # Si es un producto nuevo, lo agregamos
            cursor.execute("""
                SELECT a.codigo, a.nombre, a.precio, a.existencias 
                FROM articulos a 
                WHERE a.codigo = %s
            """, (codigo,))
            
            producto = cursor.fetchone()
            
            if not producto:
                QMessageBox.warning(self, "No encontrado", "Producto no encontrado")
                return
                
            codigo, nombre, precio, existencias = producto
            
            if existencias < cantidad:
                QMessageBox.warning(
                    self, 
                    "Stock insuficiente", 
                    f"Stock actual: {existencias}. No hay suficientes existencias."
                )
                return
                
            self.productos_agregados.append((codigo, nombre, cantidad, precio))
            self.actualizar_tabla()
            
            self.codigo_input.clear()
            self.codigo_input.setFocus()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar producto:\n{e}")
        finally:
            cursor.close()
            conexion.close()

    def quitar_producto(self):
        if not self.productos_agregados:
            return
            
        selected = self.tabla_productos.currentRow()
        
        if selected >= 0:
            self.productos_agregados.pop(selected)
            self.actualizar_tabla()

    def actualizar_tabla(self):
        self.tabla_productos.setRowCount(0)
        total = 0.0
        
        for idx, (codigo, nombre, cantidad, precio) in enumerate(self.productos_agregados):
            subtotal = cantidad * precio
            total += subtotal
            
            self.tabla_productos.insertRow(idx)
            
            # Código
            self.tabla_productos.setItem(idx, 0, QTableWidgetItem(codigo))
            
            # Nombre
            self.tabla_productos.setItem(idx, 1, QTableWidgetItem(nombre))
            
            # Precio
            item_precio = QTableWidgetItem(f"${precio:.2f}")
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_productos.setItem(idx, 2, item_precio)
            
            # Cantidad (editable)
            spin_cantidad = QSpinBox()
            spin_cantidad.setRange(1, 999)
            spin_cantidad.setValue(cantidad)
            spin_cantidad.valueChanged.connect(lambda value, row=idx: self.actualizar_cantidad(row, value))
            self.tabla_productos.setCellWidget(idx, 3, spin_cantidad)
            
            # Subtotal
            item_subtotal = QTableWidgetItem(f"${subtotal:.2f}")
            item_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_productos.setItem(idx, 4, item_subtotal)
            
            # Botones de acción
            btn_quitar = QPushButton("❌")
            btn_quitar.setStyleSheet("background-color: #f44336; color: white;")
            btn_quitar.clicked.connect(lambda _, row=idx: self.quitar_producto_por_indice(row))
            
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(btn_quitar)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            widget = QWidget()
            widget.setLayout(btn_layout)
            self.tabla_productos.setCellWidget(idx, 5, widget)
        
        self.label_total.setText(f"Total: ${total:.2f}")
        self.calcular_cambio()

    def actualizar_cantidad(self, row, nueva_cantidad):
        try:
            codigo = self.productos_agregados[row][0]
            
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            cursor.execute("SELECT existencias FROM articulos WHERE codigo = %s", (codigo,))
            existencias = cursor.fetchone()[0]
            
            if existencias < nueva_cantidad:
                QMessageBox.warning(
                    self, 
                    "Stock insuficiente", 
                    f"Stock actual: {existencias}. No hay suficientes existencias."
                )
                # Restaurar cantidad anterior
                spin = self.tabla_productos.cellWidget(row, 3)
                spin.setValue(self.productos_agregados[row][2])
                return
            
            # Actualizar cantidad en la lista
            producto = list(self.productos_agregados[row])
            producto[2] = nueva_cantidad
            self.productos_agregados[row] = tuple(producto)
            
            # Actualizar subtotal
            subtotal = nueva_cantidad * self.productos_agregados[row][3]
            item_subtotal = QTableWidgetItem(f"${subtotal:.2f}")
            item_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_productos.setItem(row, 4, item_subtotal)
            
            # Recalcular total
            total = sum(cant * precio for _, _, cant, precio in self.productos_agregados)
            self.label_total.setText(f"Total: ${total:.2f}")
            self.calcular_cambio()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar cantidad:\n{e}")
        finally:
            cursor.close()
            conexion.close()

    def quitar_producto_por_indice(self, idx):
        if 0 <= idx < len(self.productos_agregados):
            self.productos_agregados.pop(idx)
            self.actualizar_tabla()

    def pausar_venta(self):
        if not self.productos_agregados:
            QMessageBox.warning(self, "Venta vacía", "No hay productos para pausar")
            return
            
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ventas_pausadas (
                    id_pausa INT AUTO_INCREMENT PRIMARY KEY,
                    telefono_cliente VARCHAR(10),
                    cliente_info TEXT,
                    productos TEXT,
                    id_empleado INT,
                    fecha_pausa DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            productos_json = json.dumps(self.productos_agregados)
            
            telefono = self.cliente_actual['telefono'] if self.cliente_actual else None
            cliente_info = json.dumps(self.cliente_actual) if self.cliente_actual else None
            id_empleado = int(self.id_empleado_input.text()) if self.id_empleado_input.text() else None
            
            cursor.execute(
                "INSERT INTO ventas_pausadas (telefono_cliente, cliente_info, productos, id_empleado) VALUES (%s, %s, %s, %s)",
                (telefono, cliente_info, productos_json, id_empleado)
            )
            
            conexion.commit()
            
            self.venta_pausada = {
                'telefono': telefono,
                'cliente_info': self.cliente_actual.copy() if self.cliente_actual else None,
                'productos': self.productos_agregados.copy(),
                'id_empleado': id_empleado
            }
            
            QMessageBox.information(self, "Venta pausada", "La venta ha sido pausada correctamente")
            self.limpiar_venta()
            self.boton_continuar.show()
            self.boton_pausar.hide()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo pausar la venta:\n{e}")
        finally:
            cursor.close()
            conexion.close()

    def continuar_venta(self):
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            cursor.execute("""
                SELECT id_pausa, telefono_cliente, cliente_info, productos, id_empleado
                FROM ventas_pausadas 
                ORDER BY fecha_pausa DESC 
                LIMIT 1
            """)
            
            venta_pausada = cursor.fetchone()
            
            if venta_pausada:
                id_pausa, telefono, cliente_info_json, productos_json, id_empleado = venta_pausada
                
                # Cargar datos del cliente
                if cliente_info_json:
                    self.cliente_actual = json.loads(cliente_info_json)
                    self.telefono_input.setText(self.cliente_actual['telefono'])
                    info = f"Cliente: {self.cliente_actual['nombre']}"
                    if 'rfc' in self.cliente_actual and self.cliente_actual['rfc']:
                        info += f" (RFC: {self.cliente_actual['rfc']})"
                    self.cliente_info.setText(info)
                else:
                    self.cliente_actual = None
                    self.cliente_info.setText("Cliente: General")
                
                # Cargar productos
                productos = json.loads(productos_json)
                self.productos_agregados = productos
                self.actualizar_tabla()
                
                # Cargar ID de empleado
                if id_empleado:
                    self.id_empleado_input.setText(str(id_empleado))
                    self.actualizar_nombre_empleado()
                
                # Eliminar la venta pausada
                cursor.execute("DELETE FROM ventas_pausadas WHERE id_pausa = %s", (id_pausa,))
                conexion.commit()
                
                self.boton_continuar.hide()
                self.boton_pausar.show()
                
                QMessageBox.information(self, "Venta reanudada", "Se ha reanudado la venta pausada con todos los datos")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo continuar la venta:\n{e}")
        finally:
            cursor.close()
            conexion.close()

    def procesar_pago(self):
        if not self.productos_agregados:
            QMessageBox.warning(self, "Venta vacía", "No hay productos en la venta")
            return
            
        if not self.id_empleado_input.text():
            QMessageBox.warning(self, "ID Empleado requerido", "Ingrese el ID del empleado")
            return
            
        # Validar que se haya seleccionado un método de pago
        if not self.radio_efectivo.isChecked() and not self.radio_tarjeta.isChecked():
            QMessageBox.warning(self, "Método de pago requerido", "Seleccione un método de pago")
            return
            
        try:
            id_empleado = int(self.id_empleado_input.text())
            
            # Verificar si el empleado existe
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre FROM empleado WHERE id_empleado = %s", (id_empleado,))
            empleado = cursor.fetchone()
            
            if not empleado:
                QMessageBox.warning(self, "Empleado no encontrado", "El ID de empleado no existe")
                return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al validar empleado:\n{e}")
            return
        finally:
            cursor.close()
            conexion.close()
            
        if self.radio_efectivo.isChecked():
            total = sum(cant * precio for _, _, cant, precio in self.productos_agregados)
            monto_recibido = float(self.monto_efectivo.text() or 0)
            
            if monto_recibido < total:
                QMessageBox.warning(self, "Pago insuficiente", "El monto recibido es menor al total")
                return
        
        respuesta = QMessageBox.question(
            self,
            "Facturación",
            "¿Desea facturar esta venta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        datos_factura = None
        if respuesta == QMessageBox.StandardButton.Yes:
            es_cliente_general = self.cliente_actual is None
            dialog = FacturacionDialog(self.cliente_actual, es_cliente_general, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                datos_factura = dialog.get_datos_factura()
                
                # Registrar nuevo cliente si es necesario
                if datos_factura.get('registrar_cliente', False):
                    try:
                        conexion = obtener_conexion()
                        cursor = conexion.cursor()
                        cursor.execute(
                            """INSERT INTO clientes 
                            (telefono, nombre, direccion, rfc, email) 
                            VALUES (%s, %s, %s, %s, %s)""",
                            (datos_factura['telefono'], 
                            datos_factura['razon_social'],
                            datos_factura['direccion_fiscal'],
                            datos_factura['rfc'],
                            datos_factura['email'])
                        )
                        conexion.commit()
                        
                        # Actualizar cliente actual con los nuevos datos
                        self.cliente_actual = {
                            'telefono': datos_factura['telefono'],
                            'nombre': datos_factura['razon_social'],
                            'direccion': datos_factura['direccion_fiscal'],
                            'rfc': datos_factura['rfc'],
                            'email': datos_factura['email']
                        }
                        
                        # Actualizar el campo de teléfono en la interfaz
                        self.telefono_input.setText(datos_factura['telefono'])
                        self.cliente_info.setText(f"Cliente: {datos_factura['razon_social']}")
                        
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"No se pudo registrar el cliente:\n{e}")
                        return
                    finally:
                        cursor.close()
                        conexion.close()
        
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            total = sum(cant * precio for _, _, cant, precio in self.productos_agregados)
            
            cursor.execute("SELECT IFNULL(MAX(id_venta), 0) + 1 FROM venta")
            id_venta = cursor.fetchone()[0]
            fecha = datetime.now().date()
            metodo_pago = "EFECTIVO" if self.radio_efectivo.isChecked() else "TARJETA"
            
            # Usar teléfono del cliente actual o del cliente general
            telefono_cliente = self.cliente_actual['telefono'] if self.cliente_actual else '0000000000'
            
            cursor.execute(
                """INSERT INTO venta (id_venta, fecha, importe, telefono, id_empleado, metodo_pago) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (id_venta, fecha, total, telefono_cliente, id_empleado, metodo_pago)
            )
            
            if datos_factura:
                cursor.execute(
                    """INSERT INTO facturas 
                    (id_venta, rfc, razon_social, direccion_fiscal, email) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (id_venta, datos_factura['rfc'], datos_factura['razon_social'], 
                    datos_factura['direccion_fiscal'], datos_factura['email'])
                )
            
            for codigo, _, cantidad, precio in self.productos_agregados:
                cursor.execute(
                    "INSERT INTO detalles_venta (id_venta, codigo, cantidad, precio) VALUES (%s, %s, %s, %s)",
                    (id_venta, codigo, cantidad, precio)
                )
                
                cursor.execute(
                    "UPDATE articulos SET existencias = existencias - %s WHERE codigo = %s",
                    (cantidad, codigo)
                )
            
            conexion.commit()
            
            resumen = f"VENTA #{id_venta}\n"
            resumen += f"Fecha: {fecha.strftime('%d/%m/%Y %H:%M')}\n"
            resumen += f"Cliente: {self.cliente_actual['nombre'] if self.cliente_actual else 'General'}\n"
            resumen += f"Empleado: {empleado[0]} (ID: {id_empleado})\n"
            resumen += f"Método de pago: {metodo_pago}\n"
            
            if self.radio_efectivo.isChecked():
                monto_recibido = float(self.monto_efectivo.text())
                cambio = monto_recibido - total
                resumen += f"Monto recibido: ${monto_recibido:.2f}\n"
                resumen += f"Cambio: ${cambio:.2f}\n"
            
            if datos_factura:
                resumen += "--------------------------------\n"
                resumen += "DATOS DE FACTURA:\n"
                resumen += f"RFC: {datos_factura['rfc']}\n"
                resumen += f"Razón Social: {datos_factura['razon_social']}\n"
                resumen += f"Dirección Fiscal: {datos_factura['direccion_fiscal']}\n"
                resumen += f"Email: {datos_factura['email']}\n"
            
            resumen += "--------------------------------\n"
            
            for codigo, nombre, cantidad, precio in self.productos_agregados:
                resumen += f"{nombre[:20]:<20} {cantidad:>3} x ${precio:.2f} = ${cantidad*precio:.2f}\n"
            
            resumen += "--------------------------------\n"
            resumen += f"TOTAL: ${total:.2f}\n"
            resumen += "Gracias por su compra!"
            
            QMessageBox.information(
                self, 
                "Venta registrada", 
                resumen
            )
            
            self.limpiar_venta()
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo registrar la venta:\n{e}")
        finally:
            cursor.close()
            conexion.close()

    def limpiar_venta(self):
        self.telefono_input.clear()
        self.cliente_actual = None
        self.cliente_info.setText("Cliente: General (0000000000)")
        self.codigo_input.clear()
        self.cantidad_spin.setValue(1)
        self.productos_agregados = []
        self.actualizar_tabla()
        # Deseleccionamos ambos métodos de pago al limpiar
        self.radio_efectivo.setChecked(False)
        self.radio_tarjeta.setChecked(False)
        self.monto_efectivo.clear()
        self.id_empleado_input.clear()
        self.empleado_nombre_label.setText("Empleado: No asignado")
        self.telefono_input.setFocus()
        # Actualizamos el estado de los controles de pago
        self.actualizar_metodo_pago()