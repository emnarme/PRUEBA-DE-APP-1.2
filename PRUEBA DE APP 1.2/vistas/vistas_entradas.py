# vistas/vistas_entradas.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import database

class VistaEntradas(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            #main_widget {
                background-color: #f8f9fa;
                font-family: Manrope;
            }
            #header {
                background-color: white;
                border-bottom: 1px solid #dee2e6;
            }
            QTableWidget {
                border: none;
                gridline-color: #e9ecef;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px;
                border: none;
                font-weight: 500;
                font-size: 13px;
                color: #6c757d;
            }
        """)
        self.setObjectName("main_widget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = self.crear_header()
        
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 30, 40, 30)
        
        self.tabla_entradas = QTableWidget()
        self.tabla_entradas.setColumnCount(6)
        self.tabla_entradas.setHorizontalHeaderLabels(["Fecha", "No. Orden (PO)", "Producto", "Proveedor", "Cantidad Recibida", "Estado"])
        self.tabla_entradas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        content_layout.addWidget(self.tabla_entradas)

        layout.addWidget(header)
        layout.addWidget(content_area, 1)

    def crear_header(self):
        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 15, 25, 15)
        self.boton_dashboard = QPushButton("← Volver al Dashboard")
        self.boton_dashboard.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_dashboard.setStyleSheet("border: none; font-size: 14px; font-weight: bold; color: #0c7ff2;")
        titulo_app = QLabel("Historial de Entradas")
        titulo_app.setFont(QFont("Manrope", 18, QFont.Weight.Bold))
        header_layout.addWidget(self.boton_dashboard)
        header_layout.addSpacing(20)
        header_layout.addWidget(titulo_app)
        header_layout.addStretch()
        return header

    def cargar_datos_tabla(self):
        """Carga el historial de compras desde la base de datos."""
        self.tabla_entradas.setRowCount(0)
        datos = database.get_purchase_history()
        
        self.tabla_entradas.setRowCount(len(datos))
        for fila, data_row in enumerate(datos):
            for col, data_cell in enumerate(data_row):
                self.tabla_entradas.setItem(fila, col, QTableWidgetItem(str(data_cell)))
