import sys
from conexion import obtener_conexion
from PyQt6.QtWidgets import QApplication, QTabWidget, QWidget, QVBoxLayout
from PyQt6.QtGui import QIcon
from empleado import VentanaEmpleados  
from categoria import Ventanacatego
from cliente import VentanaClientes
from proveedor import VentanaProveedores
from unidad import VentanaUnidad
from articulo import VentanaArticulos
from venta import VentanaVenta
from detalles_venta import VentanaDetallesVenta

class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Punto de Venta")
        self.setWindowIcon(QIcon('icon.png'))
        self.resize(1100, 650)
        
        try:
            self.conexion = obtener_conexion()
        except Exception as e:
            self.mostrar_error(f"No se pudo conectar a la base de datos:\n{str(e)}")
            sys.exit(1)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                padding: 10px;
                min-width: 100px;
                font-size: 12px;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                margin-top: 5px;
            }
        """)
        
        self.tabs.addTab(VentanaEmpleados(self.conexion), "👨‍💼 Empleados")
        self.tabs.addTab(Ventanacatego(self.conexion), "📁 Categorías")
        self.tabs.addTab(VentanaClientes(self.conexion), "👥 Clientes")
        self.tabs.addTab(VentanaProveedores(self.conexion), "🏭 Proveedores")
        self.tabs.addTab(VentanaUnidad(self.conexion), "📏 Unidades")
        self.tabs.addTab(VentanaArticulos(self.conexion), "🛒 Artículos")
        self.tabs.addTab(VentanaVenta(self.conexion), "💰 Ventas")
        self.tabs.addTab(VentanaDetallesVenta(self.conexion), "📋 Detalles Ventas")

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def mostrar_error(self, mensaje):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(mensaje)
        msg.setWindowTitle("Error")
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())