# vistas/vistas_dashboard.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QGridLayout, QFrame)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import locale
import database
from .vistas_graficos import PieChartWidget, LineChartWidget

class VistaDashboard(QWidget):
    def __init__(self):
        super().__init__()
        
        try: 
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except locale.Error: 
            locale.setlocale(locale.LC_ALL, '')

        self.setStyleSheet("""
            #main_widget { background-color: #f8f9fa; font-family: Manrope; }
            #header { background-color: white; border-bottom: 1px solid #dee2e6; }
            #dashboard_title { font-size: 28px; font-weight: bold; color: #212529; }
            QFrame.card { background-color: white; border-radius: 8px; border: 1px solid #e9ecef; }
            QLabel.kpi_title { font-size: 14px; color: #6c757d; }
            QLabel.kpi_value { font-size: 26px; font-weight: bold; color: #212529; }
            QLabel.kpi_icon { font-size: 20px; }
            QLabel.chart_title { font-size: 16px; font-weight: bold; color: #343a40; padding-bottom: 10px; }
            QPushButton.nav_button { font-size: 14px; font-weight: 500; color: #6c757d; border: none; padding: 10px; }
            QPushButton.nav_button_active { font-size: 14px; font-weight: bold; color: #0c7ff2; border: none; padding: 10px; }
        """)
        self.setObjectName("main_widget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = self.crear_header()
        
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(25)
        
        dashboard_title = QLabel("Dashboard")
        dashboard_title.setObjectName("dashboard_title")
        
        # --- KPIs ---
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(25)
        self.card_ventas = self.crear_tarjeta_kpi("Ventas del Mes", "$0.00", "📈", "#28a745")
        self.card_inventario = self.crear_tarjeta_kpi("Valor Inventario", "$0.00", "📦", "#0c7ff2")
        self.card_ordenes = self.crear_tarjeta_kpi("Órdenes de Compra", "0", "📋", "#fd7e14")
        self.kpi_layout.addWidget(self.card_ventas)
        self.kpi_layout.addWidget(self.card_inventario)
        self.kpi_layout.addWidget(self.card_ordenes)

        # --- Gráficos ---
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(25)
        
        pie_card = QFrame()
        pie_card.setObjectName("card")
        pie_layout = QVBoxLayout(pie_card)
        pie_layout.addWidget(QLabel("Ventas por Cliente", objectName="chart_title"))
        self.pie_chart = PieChartWidget()
        pie_layout.addWidget(self.pie_chart)
        
        line_card = QFrame()
        line_card.setObjectName("card")
        line_layout = QVBoxLayout(line_card)
        line_layout.addWidget(QLabel("Ventas Mensuales", objectName="chart_title"))
        self.line_chart = LineChartWidget()
        line_layout.addWidget(self.line_chart)

        charts_layout.addWidget(pie_card, 35)
        charts_layout.addWidget(line_card, 65)

        content_layout.addWidget(dashboard_title)
        content_layout.addLayout(self.kpi_layout)
        content_layout.addLayout(charts_layout)
        content_layout.addStretch(1)

        layout.addWidget(header)
        layout.addWidget(content_area)
        
        self.refresh_data()

    def refresh_data(self):
        kpis = database.get_dashboard_kpis()
        self.card_ventas.findChild(QLabel, "kpi_value").setText(f"${kpis['ventas_mes']:,.2f}")
        self.card_inventario.findChild(QLabel, "kpi_value").setText(f"${kpis['valor_inventario']:,.2f}")
        self.card_ordenes.findChild(QLabel, "kpi_value").setText(str(kpis['ordenes_pendientes']))
        
        pie_data = database.get_sales_by_customer()
        pie_labels = [item[0] for item in pie_data]
        pie_sizes = [item[1] for item in pie_data]
        self.pie_chart.update_chart(pie_labels, pie_sizes)

        line_data = database.get_monthly_sales_summary()
        monthly_sales_dict = {item[0]: item[1] for item in line_data}
        self.line_chart.update_chart(monthly_sales_dict)

    def crear_header(self):
        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        title = QLabel("DEMOGA EMALDO")
        title.setFont(QFont("Manrope", 16, QFont.Weight.Bold))
        
        # --- Barra de navegación completa ---
        self.boton_inicio = QPushButton("Inicio")
        self.boton_ventas = QPushButton("Ventas")
        self.boton_compras = QPushButton("Compras")
        self.boton_entradas = QPushButton("Entradas")
        self.boton_inventario = QPushButton("Inventario")
        self.boton_usuarios = QPushButton("Usuarios")
        self.boton_contactos = QPushButton("Contactos")
        self.boton_reportes = QPushButton("Reportes")
        
        self.boton_inicio.setObjectName("nav_button_active")
        for btn in [self.boton_ventas, self.boton_compras, self.boton_entradas, self.boton_inventario, self.boton_usuarios, self.boton_contactos, self.boton_reportes]:
            btn.setObjectName("nav_button")

        notif_icon = QLabel("🔔")
        notif_icon.setFont(QFont("Manrope", 16))
        profile_pic = QLabel()
        profile_pic.setFixedSize(36, 36)
        profile_pic.setStyleSheet("background-color: #adb5bd; border-radius: 18px;")

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.boton_inicio)
        header_layout.addWidget(self.boton_ventas)
        header_layout.addWidget(self.boton_compras)
        header_layout.addWidget(self.boton_entradas)
        header_layout.addWidget(self.boton_inventario)
        header_layout.addWidget(self.boton_usuarios)
        header_layout.addWidget(self.boton_contactos)
        header_layout.addWidget(self.boton_reportes)
        header_layout.addStretch()
        header_layout.addWidget(notif_icon)
        header_layout.addSpacing(15)
        header_layout.addWidget(profile_pic)
        return header

    def crear_tarjeta_kpi(self, titulo, valor, icono, color_icono):
        card = QFrame()
        card.setObjectName("card")
        layout = QGridLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        title_label = QLabel(titulo)
        title_label.setObjectName("kpi_title")
        value_label = QLabel(valor)
        value_label.setObjectName("kpi_value")
        icon_label = QLabel(icono)
        icon_label.setObjectName("kpi_icon")
        icon_label.setStyleSheet(f"color: {color_icono};")
        layout.addWidget(title_label, 0, 0)
        layout.addWidget(icon_label, 0, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(value_label, 1, 0, 1, 2)
        return card

    def update_permissions(self, role):
        """Muestra u oculta botones basados en el rol del usuario."""
        is_admin = (role == "Administrador")
        
        self.boton_usuarios.setVisible(is_admin)
        self.boton_reportes.setVisible(is_admin)
        self.boton_contactos.setVisible(is_admin)
