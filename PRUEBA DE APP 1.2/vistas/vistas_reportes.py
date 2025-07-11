# vistas/vistas_reportes.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                             QComboBox, QFileDialog, QMessageBox, QDateEdit, QGridLayout)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QDate
import database
import pandas as pd
import os
import qtawesome as qta

class VistaReportes(QWidget):
    def __init__(self):
        super().__init__()
        self.current_report_data = []
        self.current_report_headers = []

        self.setStyleSheet("""
            #main_widget {
                background-color: #f8f9fa;
                font-family: Manrope;
            }
            #header {
                background-color: white;
                border-bottom: 1px solid #dee2e6;
            }
            #card {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            #report_title {
                font-size: 28px;
                font-weight: bold;
                color: #212529;
            }
            QComboBox, QDateEdit {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QPushButton#export_button {
                background-color: #198754; /* Verde */
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
            }
            QTableWidget {
                border: none;
                gridline-color: #e9ecef;
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
        content_layout.setSpacing(20)

        # --- Panel de Filtros ---
        filter_box = QFrame()
        filter_box.setObjectName("card")
        filter_layout = QGridLayout(filter_box)
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["Ventas Detalladas", "Productos más vendidos", "Ventas por Cliente"])
        self.report_type_combo.currentTextChanged.connect(self.toggle_filters)

        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        self.end_date_edit.setCalendarPopup(True)
        
        self.customer_combo = QComboBox()
        
        generate_button = QPushButton(qta.icon('fa5s.cogs'), " Generar Reporte")
        generate_button.clicked.connect(self.generar_reporte)
        
        self.export_button = QPushButton(qta.icon('fa5s.file-csv'), " Exportar a CSV")
        self.export_button.clicked.connect(self.exportar_a_csv)
        self.export_button.setEnabled(False)

        filter_layout.addWidget(QLabel("Tipo de Reporte:"), 0, 0)
        filter_layout.addWidget(self.report_type_combo, 0, 1, 1, 3)
        self.start_date_label = QLabel("Fecha de Inicio:")
        filter_layout.addWidget(self.start_date_label, 1, 0)
        filter_layout.addWidget(self.start_date_edit, 1, 1)
        self.end_date_label = QLabel("Fecha de Fin:")
        filter_layout.addWidget(self.end_date_label, 1, 2)
        filter_layout.addWidget(self.end_date_edit, 1, 3)
        self.customer_label = QLabel("Cliente:")
        filter_layout.addWidget(self.customer_label, 2, 0)
        filter_layout.addWidget(self.customer_combo, 2, 1, 1, 3)
        filter_layout.addWidget(generate_button, 3, 2)
        filter_layout.addWidget(self.export_button, 3, 3)

        # --- Tabla de Resultados ---
        self.tabla_reporte = QTableWidget()
        
        content_layout.addWidget(QLabel("Módulo de Reportes", objectName="report_title"))
        content_layout.addWidget(filter_box)
        content_layout.addWidget(self.tabla_reporte, 1)

        layout.addWidget(header)
        layout.addWidget(content_area, 1)
        
        self.cargar_filtros()
        self.toggle_filters(self.report_type_combo.currentText()) # Inicializar visibilidad de filtros

    def crear_header(self):
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 15, 25, 15)
        self.boton_dashboard = QPushButton("← Volver al Dashboard")
        self.boton_dashboard.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_dashboard.setStyleSheet("border: none; font-size: 14px; font-weight: bold; color: #0c7ff2;")
        header_layout.addWidget(self.boton_dashboard)
        header_layout.addStretch()
        return header

    def cargar_filtros(self):
        """Carga los clientes en el ComboBox."""
        self.customer_combo.clear()
        self.customer_combo.addItem("Todos")
        customers = database.get_all_customers()
        for customer in customers:
            self.customer_combo.addItem(customer[1])

    def toggle_filters(self, report_type):
        """Activa o desactiva los filtros según el reporte seleccionado."""
        is_sales_detailed = (report_type == "Ventas Detalladas")
        for widget in [self.start_date_label, self.start_date_edit, self.end_date_label, self.end_date_edit, self.customer_label, self.customer_combo]:
            widget.setVisible(is_sales_detailed)

    def generar_reporte(self):
        """Obtiene los datos de la DB con los filtros y los muestra."""
        reporte_seleccionado = self.report_type_combo.currentText()
        
        if reporte_seleccionado == "Ventas Detalladas":
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            customer_name = self.customer_combo.currentText()
            self.current_report_data = database.get_filtered_sales_report(start_date, end_date, customer_name)
            self.current_report_headers = ["Fecha", "Factura", "Código (EDP)", "Descripción", "Cant.", "P. Venta", "P. Costo", "Utilidad", "Utilidad Total", "Cliente"]
            self.popular_tabla_ventas_detalladas()
        elif reporte_seleccionado == "Productos más vendidos":
            self.current_report_data = database.get_top_selling_products()
            self.current_report_headers = ["Código", "Nombre del Producto", "Cantidad Vendida"]
            self.popular_tabla_simple(self.current_report_data, self.current_report_headers)
        elif reporte_seleccionado == "Ventas por Cliente":
            self.current_report_data = database.get_sales_by_customer()
            self.current_report_headers = ["Nombre del Cliente", "Total Comprado"]
            self.popular_tabla_simple(self.current_report_data, self.current_report_headers, is_currency=True)
        
        self.export_button.setEnabled(bool(self.current_report_data))

    def popular_tabla_ventas_detalladas(self):
        self.tabla_reporte.setRowCount(0)
        self.tabla_reporte.setColumnCount(len(self.current_report_headers))
        self.tabla_reporte.setHorizontalHeaderLabels(self.current_report_headers)
        self.tabla_reporte.setRowCount(len(self.current_report_data))
        for fila, data_row in enumerate(self.current_report_data):
            # data_row: (sale_date, invoice, code, name, qty, sale_price, cost_price, customer)
            utilidad_unitaria = data_row[5] - data_row[6]
            utilidad_total = utilidad_unitaria * data_row[4]
            display_row = [data_row[0], data_row[1], data_row[2], data_row[3], data_row[4], f"${data_row[5]:,.2f}", f"${data_row[6]:,.2f}", f"${utilidad_unitaria:,.2f}", f"${utilidad_total:,.2f}", data_row[7]]
            for col, data_cell in enumerate(display_row):
                self.tabla_reporte.setItem(fila, col, QTableWidgetItem(str(data_cell)))
        self.tabla_reporte.resizeColumnsToContents()

    def popular_tabla_simple(self, datos, headers, is_currency=False):
        self.tabla_reporte.setRowCount(0)
        self.tabla_reporte.setColumnCount(len(headers))
        self.tabla_reporte.setHorizontalHeaderLabels(headers)
        self.tabla_reporte.setRowCount(len(datos))
        for fila, data_row in enumerate(datos):
            for col, data_cell in enumerate(data_row):
                if is_currency and col == 1:
                    data_cell = f"${float(data_cell):,.2f}"
                self.tabla_reporte.setItem(fila, col, QTableWidgetItem(str(data_cell)))
        self.tabla_reporte.resizeColumnsToContents()

    def exportar_a_csv(self):
        if not self.current_report_data:
            QMessageBox.warning(self, "Exportar Error", "No hay datos para exportar.")
            return
        default_dir = os.path.join(os.path.expanduser('~'), "Downloads")
        report_name = self.report_type_combo.currentText().replace(" ", "_").lower()
        default_filename = os.path.join(default_dir, f"reporte_{report_name}.csv")
        filePath, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte", default_filename, "CSV Files (*.csv);;All Files (*)")
        if filePath:
            try:
                if self.report_type_combo.currentText() == "Ventas Detalladas":
                    export_data = []
                    for row in self.current_report_data:
                        utilidad_unitaria = row[5] - row[6]
                        utilidad_total = utilidad_unitaria * row[4]
                        export_data.append(list(row) + [utilidad_unitaria, utilidad_total])
                    df = pd.DataFrame(export_data, columns=self.current_report_headers)
                else:
                    df = pd.DataFrame(self.current_report_data, columns=self.current_report_headers)
                
                df.to_csv(filePath, index=False, encoding='utf-8-sig')
                QMessageBox.information(self, "Éxito", f"Reporte exportado exitosamente a:\n{filePath}")
            except Exception as e:
                QMessageBox.critical(self, "Error de Exportación", f"Ocurrió un error al guardar el archivo:\n{e}")
