from conexion import obtener_conexion
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QDateEdit, QLabel, QGroupBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QDoubleValidator, QIntValidator

class VentanaDetallesVenta(QWidget):
    def __init__(self, conexion):
        super().__init__()
        self.conexion = conexion
        
        self.init_ui()
        self.cargar_ventas()

    def init_ui(self):
        self.setWindowTitle("Detalles de Ventas")
        
        # Widgets para filtros
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDisplayFormat("dd/MM/yyyy")
        
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setDate(QDate.currentDate())
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDisplayFormat("dd/MM/yyyy")
        
        self.id_venta_input = QLineEdit()
        self.id_venta_input.setPlaceholderText("ID de venta")
        self.id_venta_input.setValidator(QIntValidator(1, 999999))
        
        self.telefono_cliente_input = QLineEdit()
        self.telefono_cliente_input.setPlaceholderText("Teléfono cliente")
        self.telefono_cliente_input.setValidator(QIntValidator())
        self.telefono_cliente_input.setMaxLength(10)
        
        # Botones
        self.boton_buscar = QPushButton("🔍 Buscar")
        self.boton_buscar.setStyleSheet("background-color: #4CAF50; color: white;")
        
        self.boton_limpiar = QPushButton("🧹 Limpiar")
        self.boton_limpiar.setStyleSheet("background-color: #f44336; color: white;")
        
        # Tablas
        self.tabla_ventas = QTableWidget()
        self.configurar_tabla_ventas()
        
        self.tabla_detalles = QTableWidget()
        self.configurar_tabla_detalles()
        
        # Layouts
        filtros_layout = QHBoxLayout()
        filtros_layout.addWidget(QLabel("Desde:"))
        filtros_layout.addWidget(self.fecha_inicio)
        filtros_layout.addWidget(QLabel("Hasta:"))
        filtros_layout.addWidget(self.fecha_fin)
        filtros_layout.addWidget(QLabel("ID Venta:"))
        filtros_layout.addWidget(self.id_venta_input)
        filtros_layout.addWidget(QLabel("Teléfono:"))
        filtros_layout.addWidget(self.telefono_cliente_input)
        filtros_layout.addWidget(self.boton_buscar)
        filtros_layout.addWidget(self.boton_limpiar)
        
        ventas_group = QGroupBox("Ventas")
        ventas_group.setLayout(QVBoxLayout())
        ventas_group.layout().addWidget(self.tabla_ventas)
        
        detalles_group = QGroupBox("Detalles de Venta")
        detalles_group.setLayout(QVBoxLayout())
        detalles_group.layout().addWidget(self.tabla_detalles)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(filtros_layout)
        main_layout.addWidget(ventas_group)
        main_layout.addWidget(detalles_group)
        
        self.setLayout(main_layout)
        
        # Conexiones
        self.boton_buscar.clicked.connect(self.cargar_ventas)
        self.boton_limpiar.clicked.connect(self.limpiar_filtros)
        self.tabla_ventas.itemSelectionChanged.connect(self.cargar_detalles_venta)

    def configurar_tabla_ventas(self):
        self.tabla_ventas.setColumnCount(7)
        self.tabla_ventas.setHorizontalHeaderLabels([
            "ID", "Fecha", "Importe", "Cliente", "Empleado", "Teléfono", "Factura"
        ])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_ventas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_ventas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Ajustar ancho de columnas
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

    def configurar_tabla_detalles(self):
        self.tabla_detalles.setColumnCount(5)
        self.tabla_detalles.setHorizontalHeaderLabels([
            "Producto", "Descripción", "Cantidad", "Precio", "Subtotal"
        ])
        self.tabla_detalles.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_detalles.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_detalles.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Ajustar ancho de columnas
        self.tabla_detalles.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_detalles.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_detalles.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_detalles.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

    def cargar_ventas(self):
        try:
            # Obtener parámetros de filtro
            fecha_inicio = self.fecha_inicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")
            id_venta = self.id_venta_input.text()
            telefono = self.telefono_cliente_input.text()
            
            # Construir consulta SQL con filtros
            query = """
                SELECT v.id_venta, v.fecha, v.importe, 
                       IFNULL(c.nombre, 'General') AS cliente, 
                       e.nombre AS empleado,
                       v.telefono,
                       IF(f.id_venta IS NULL, 'No', 'Sí') AS facturado
                FROM venta v
                LEFT JOIN clientes c ON v.telefono = c.telefono
                JOIN empleado e ON v.id_empleado = e.id_empleado
                LEFT JOIN facturas f ON v.id_venta = f.id_venta
                WHERE v.fecha BETWEEN %s AND %s
            """
            params = [fecha_inicio, fecha_fin]
            
            if id_venta:
                query += " AND v.id_venta = %s"
                params.append(int(id_venta))
                
            if telefono:
                query += " AND v.telefono = %s"
                params.append(telefono)
                
            query += " ORDER BY v.fecha DESC, v.id_venta DESC"
            
            # Ejecutar consulta
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(query, params)
            
            # Limpiar tabla
            self.tabla_ventas.setRowCount(0)
            
            # Llenar tabla
            for row_idx, (id_venta, fecha, importe, cliente, empleado, telefono, facturado) in enumerate(cursor.fetchall()):
                self.tabla_ventas.insertRow(row_idx)
                
                self.tabla_ventas.setItem(row_idx, 0, QTableWidgetItem(str(id_venta)))
                self.tabla_ventas.setItem(row_idx, 1, QTableWidgetItem(fecha.strftime("%d/%m/%Y %H:%M")))
                
                item_importe = QTableWidgetItem(f"${importe:.2f}")
                item_importe.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.tabla_ventas.setItem(row_idx, 2, item_importe)
                
                self.tabla_ventas.setItem(row_idx, 3, QTableWidgetItem(cliente))
                self.tabla_ventas.setItem(row_idx, 4, QTableWidgetItem(empleado))
                self.tabla_ventas.setItem(row_idx, 5, QTableWidgetItem(telefono if telefono else ""))
                self.tabla_ventas.setItem(row_idx, 6, QTableWidgetItem(facturado))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar ventas:\n{e}")
        finally:
            cursor.close()
            conexion.close()

    def cargar_detalles_venta(self):
        selected = self.tabla_ventas.currentRow()
        
        if selected < 0:
            return
            
        id_venta = self.tabla_ventas.item(selected, 0).text()
        
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            # Cargar detalles de los productos
            cursor.execute("""
                SELECT a.codigo, a.nombre, dv.cantidad, dv.precio
                FROM detalles_venta dv
                JOIN articulos a ON dv.codigo = a.codigo
                WHERE dv.id_venta = %s
                ORDER BY a.nombre
            """, (int(id_venta),))
            
            # Limpiar tabla
            self.tabla_detalles.setRowCount(0)
            
            # Llenar tabla
            for row_idx, (codigo, nombre, cantidad, precio) in enumerate(cursor.fetchall()):
                self.tabla_detalles.insertRow(row_idx)
                
                self.tabla_detalles.setItem(row_idx, 0, QTableWidgetItem(codigo))
                self.tabla_detalles.setItem(row_idx, 1, QTableWidgetItem(nombre))
                
                item_cantidad = QTableWidgetItem(str(cantidad))
                item_cantidad.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.tabla_detalles.setItem(row_idx, 2, item_cantidad)
                
                item_precio = QTableWidgetItem(f"${precio:.2f}")
                item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.tabla_detalles.setItem(row_idx, 3, item_precio)
                
                subtotal = cantidad * precio
                item_subtotal = QTableWidgetItem(f"${subtotal:.2f}")
                item_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.tabla_detalles.setItem(row_idx, 4, item_subtotal)
            
            # Cargar datos de factura si existe
            cursor.execute("""
                SELECT rfc, razon_social, direccion_fiscal, email
                FROM facturas
                WHERE id_venta = %s
            """, (int(id_venta),))
            
            factura = cursor.fetchone()
            if factura:
                # Agregar fila con datos de factura
                row_idx = self.tabla_detalles.rowCount()
                self.tabla_detalles.insertRow(row_idx)
                
                self.tabla_detalles.setItem(row_idx, 0, QTableWidgetItem("DATOS DE FACTURA:"))
                self.tabla_detalles.setSpan(row_idx, 0, 1, 5)
                
                rfc, razon_social, direccion, email = factura
                
                row_idx += 1
                self.tabla_detalles.insertRow(row_idx)
                self.tabla_detalles.setItem(row_idx, 0, QTableWidgetItem(f"RFC: {rfc}"))
                self.tabla_detalles.setSpan(row_idx, 0, 1, 5)
                
                row_idx += 1
                self.tabla_detalles.insertRow(row_idx)
                self.tabla_detalles.setItem(row_idx, 0, QTableWidgetItem(f"Razón Social: {razon_social}"))
                self.tabla_detalles.setSpan(row_idx, 0, 1, 5)
                
                row_idx += 1
                self.tabla_detalles.insertRow(row_idx)
                self.tabla_detalles.setItem(row_idx, 0, QTableWidgetItem(f"Dirección: {direccion}"))
                self.tabla_detalles.setSpan(row_idx, 0, 1, 5)
                
                row_idx += 1
                self.tabla_detalles.insertRow(row_idx)
                self.tabla_detalles.setItem(row_idx, 0, QTableWidgetItem(f"Email: {email}"))
                self.tabla_detalles.setSpan(row_idx, 0, 1, 5)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar detalles:\n{e}")
        finally:
            cursor.close()
            conexion.close()

    def limpiar_filtros(self):
        self.fecha_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_fin.setDate(QDate.currentDate())
        self.id_venta_input.clear()
        self.telefono_cliente_input.clear()
        self.cargar_ventas()