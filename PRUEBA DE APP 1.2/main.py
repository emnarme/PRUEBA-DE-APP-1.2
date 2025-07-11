# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox

# Importar todas las vistas
from vistas.vistas_login import VistaLogin
from vistas.vistas_dashboard import VistaDashboard
from vistas.vistas_compras import VistaCompras
from vistas.vistas_ventas import VistaVentas
from vistas.vistas_inventario import VistaInventario
from vistas.vistas_entradas import VistaEntradas
from vistas.vistas_usuarios import VistaUsuarios
from vistas.vistas_reportes import VistaReportes
from vistas.vistas_contactos import VistaContactos
from vistas.vistas_notificacion import NotificationWidget

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DEMOGA EMALDO - Sistema de Gestión")
        self.setGeometry(100, 100, 700, 500)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.current_user_role = None
        self.notifications = []

        # --- Creación de todas las instancias de las vistas ---
        self.vista_login = VistaLogin()
        self.vista_dashboard = VistaDashboard()
        self.vista_compras = VistaCompras()
        self.vista_ventas = VistaVentas()
        self.vista_inventario = VistaInventario()
        self.vista_entradas = VistaEntradas()
        self.vista_usuarios = VistaUsuarios()
        self.vista_reportes = VistaReportes()
        self.vista_contactos = VistaContactos()
        
        # Añadir todas las vistas al QStackedWidget
        for w in [self.vista_login, self.vista_dashboard, self.vista_compras, self.vista_ventas, self.vista_inventario, self.vista_entradas, self.vista_usuarios, self.vista_reportes, self.vista_contactos]:
            self.stacked_widget.addWidget(w)

        # Conectar señales de navegación
        self.vista_login.login_exitoso.connect(self.handle_login_success)
        
        # Conexiones desde el Dashboard
        self.vista_dashboard.boton_compras.clicked.connect(self.mostrar_compras)
        self.vista_dashboard.boton_ventas.clicked.connect(self.mostrar_ventas)
        self.vista_dashboard.boton_inventario.clicked.connect(self.mostrar_inventario)
        self.vista_dashboard.boton_usuarios.clicked.connect(self.mostrar_usuarios)
        self.vista_dashboard.boton_entradas.clicked.connect(self.mostrar_entradas)
        self.vista_dashboard.boton_reportes.clicked.connect(self.mostrar_reportes)
        self.vista_dashboard.boton_contactos.clicked.connect(self.mostrar_contactos)
        
        # Conexiones para "Volver al Dashboard"
        for vista in [self.vista_compras, self.vista_ventas, self.vista_inventario, self.vista_entradas, self.vista_usuarios, self.vista_reportes, self.vista_contactos]:
            if hasattr(vista, 'boton_dashboard'):
                vista.boton_dashboard.clicked.connect(self.mostrar_dashboard)

        self.mostrar_login()

    def handle_login_success(self, role):
        """Se activa al iniciar sesión, guarda el rol y muestra el dashboard."""
        self.current_user_role = role
        self.mostrar_dashboard()

    def check_permission(self, required_role="Administrador"):
        """Verifica si el usuario actual tiene el rol requerido."""
        if self.current_user_role == required_role:
            return True
        else:
            self.show_notification("No tienes permiso para acceder a esta sección.", "error")
            return False

    def show_notification(self, message, message_type='success'):
        notification = NotificationWidget(message, message_type, self)
        pos_y = 10
        for notif in self.notifications:
            pos_y += notif.height() + 5
        notification.show_notification(pos_y)
        self.notifications.append(notification)
        notification.animation.finished.connect(lambda: self.remove_notification(notification))

    def remove_notification(self, notification):
        try:
            self.notifications.remove(notification)
            for i, notif in enumerate(self.notifications):
                new_y = 10 + (i * (notif.height() + 5))
                notif.move(notif.x(), new_y)
        except ValueError:
            pass

    def mostrar_login(self):
        self.stacked_widget.setCurrentWidget(self.vista_login)
    
    def mostrar_dashboard(self):
        if self.current_user_role:
            self.vista_dashboard.update_permissions(self.current_user_role)
            self.vista_dashboard.refresh_data()
            self.stacked_widget.setCurrentWidget(self.vista_dashboard)
        
    def mostrar_compras(self):
        self.vista_compras.cargar_datos_tabla()
        self.stacked_widget.setCurrentWidget(self.vista_compras)

    # --- MÉTODO CORREGIDO ---
    def mostrar_ventas(self):
        self.vista_ventas.cargar_datos_ordenes()
        self.vista_ventas.cargar_datos_historial()
        self.stacked_widget.setCurrentWidget(self.vista_ventas)

    def mostrar_inventario(self):
        self.vista_inventario.cargar_datos_tabla()
        self.stacked_widget.setCurrentWidget(self.vista_inventario)

    def mostrar_entradas(self):
        self.vista_entradas.cargar_datos_tabla()
        self.stacked_widget.setCurrentWidget(self.vista_entradas)

    def mostrar_usuarios(self):
        if self.check_permission():
            self.vista_usuarios.cargar_datos_tabla()
            self.stacked_widget.setCurrentWidget(self.vista_usuarios)

    def mostrar_reportes(self):
        if self.check_permission():
            self.vista_reportes.cargar_filtros()
            self.stacked_widget.setCurrentWidget(self.vista_reportes)
            
    def mostrar_contactos(self):
        if self.check_permission():
            self.vista_contactos.cargar_clientes()
            self.vista_contactos.cargar_proveedores()
            self.stacked_widget.setCurrentWidget(self.vista_contactos)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
# "ESTA ES UNA PRUEBA PARA VER LA FUNCIONALIDAD DEL REPOSITORIO"