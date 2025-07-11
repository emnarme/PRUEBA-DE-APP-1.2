# vistas/vistas_ventas.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                             QTabWidget, QDialog, QFormLayout, QComboBox, QSpinBox,
                             QDialogButtonBox, QMessageBox, QDateEdit)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QDate
import database # Se asume que este módulo tiene las funciones necesarias
import qtawesome as qta

# --- Diálogo para Registrar Orden de Cliente (Sin cambios) ---
class RegisterCustomerOrderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Orden de Cliente")
        layout = QFormLayout(self)
        
        self.customer_combo = QComboBox()
        self.product_combo = QComboBox()
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 9999)
        self.required_date_edit = QDateEdit(QDate.currentDate().addDays(7))
        self.required_date_edit.setCalendarPopup(True)
        
        self.description_label = QLabel("...")
        self.price_label = QLabel("$0.00")

        customers = database.get_all_customers()
        for customer in customers:
            self.customer_combo.addItem(customer[1], userData=customer[0])
        
        self.products = database.get_all_products()
        for product in self.products:
            self.product_combo.addItem(f"{product[1]} (Stock: {product[4]})", userData=product)
        
        self.product_combo.currentIndexChanged.connect(self.update_product_info)
        
        layout.addRow("Cliente:", self.customer_combo)
        layout.addRow("Fecha Requerida:", self.required_date_edit)
        layout.addRow("Item (Producto):", self.product_combo)
        layout.addRow("Descripción:", self.description_label)
        layout.addRow("Precio de Venta:", self.price_label)
        layout.addRow("Cantidad Requerida:", self.quantity_spinbox)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.update_product_info()

    def update_product_info(self):
        product_data = self.product_combo.currentData()
        if product_data:
            self.description_label.setText(product_data[2] or "N/A")
            self.price_label.setText(f"${product_data[6]:,.2f}")

    def get_data(self):
        product_data = self.product_combo.currentData()
        return {
            "customer_id": self.customer_combo.currentData(),
            "product_code": product_data[0] if product_data else None,
            "quantity": self.quantity_spinbox.value(),
            "required_date": self.required_date_edit.date().toString("yyyy-MM-dd")
        }

# --- NUEVO: Diálogo para Procesar Orden y Registrar Venta ---
class ProcessOrderDialog(QDialog):
    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Venta desde Orden")
        self.order_data = order_data
        
        layout = QFormLayout(self)
        
        # Mostrar información de la orden (no editable)
        layout.addRow(QLabel("<b>Cliente:</b>"), QLabel(order_data['customer_name']))
        layout.addRow(QLabel("<b>Producto:</b>"), QLabel(order_data['product_description']))
        layout.addRow(QLabel("<b>Cantidad:</b>"), QLabel(str(order_data['quantity'])))
        layout.addRow(QLabel("<b>Total Venta:</b>"), QLabel(f"${order_data['sale_price'] * order_data['quantity']:.2f}"))
        
        layout.addRow(QFrame()) # Separador visual

        # Campo para seleccionar el vendedor
        self.seller_combo = QComboBox()
        # Asumimos que existe una función para obtener los usuarios/vendedores
        sellers = database.get_all_users() 
        for seller in sellers:
            self.seller_combo.addItem(seller[1], userData=seller[0])
        
        layout.addRow("Vendedor:", self.seller_combo)
        
        # Botones de Aceptar y Cancelar
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_seller_id(self):
        return self.seller_combo.currentData()

# --- Clase Principal de la Vista de Ventas (Modificada) ---
class VistaVentas(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("main_widget")
        self.setStyleSheet("""
            #main_widget { background-color: #f8f9fa; font-family: Manrope; }
            #header { background-color: white; border-bottom: 1px solid #dee2e6; }
            QTabWidget::pane { border: none; }
            QTabBar::tab { padding: 10px 25px; font-size: 14px; font-weight: bold; }
            QTabBar::tab:selected { color: #0c7ff2; border-bottom: 2px solid #0c7ff2; }
            QTableWidget { border: 1px solid #e9ecef; }
        """)
        
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
        header = self.crear_header()
        
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 20, 40, 30)
        
        self.tab_widget = QTabWidget()
        self.tab_ordenes = self.crear_panel_ordenes()
        self.tab_historial = self.crear_panel_historial()
        
        self.tab_widget.addTab(self.tab_ordenes, "   Órdenes de Cliente   ")
        self.tab_widget.addTab(self.tab_historial, "   Historial de Salidas   ")
        
        content_layout.addWidget(self.tab_widget)
        main_layout.addWidget(header); main_layout.addWidget(content_area)

        # Cargar datos iniciales
        self.cargar_datos_ordenes()
        self.cargar_datos_historial()

    def crear_header(self):
        header = QFrame(); header_layout = QHBoxLayout(header); header_layout.setContentsMargins(25, 15, 25, 15)
        self.boton_dashboard = QPushButton("← Volver al Dashboard")
        self.boton_dashboard.setStyleSheet("border: none; font-size: 14px; font-weight: bold; color: #0c7ff2;")
        header_layout.addWidget(self.boton_dashboard); header_layout.addStretch()
        return header

    def crear_panel_ordenes(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setSpacing(15); top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Seguimiento de Órdenes de Cliente", font=QFont("Manrope", 18, QFont.Weight.Bold)))
        top_layout.addStretch()
        add_button = QPushButton(qta.icon('fa5s.plus'), " Registrar Orden")
        add_button.clicked.connect(self.abrir_dialogo_orden)
        top_layout.addWidget(add_button)
        
        self.tabla_ordenes = QTableWidget()
        # MODIFICADO: Se añade la columna "Acciones"
        self.tabla_ordenes.setColumnCount(9)
        self.tabla_ordenes.setHorizontalHeaderLabels(["Cliente", "Fecha de Entrada", "Fecha Requerida", "Item (Código)", "Descripción", "Precio Venta", "Cant. Req.", "Estado", "Acciones"])
        self.tabla_ordenes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_ordenes.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Hacer tabla no editable
        
        layout.addLayout(top_layout); layout.addWidget(self.tabla_ordenes)
        return panel

    def crear_panel_historial(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setSpacing(15)
        layout.addWidget(QLabel("Historial de Salidas (Ventas Finalizadas)", font=QFont("Manrope", 18, QFont.Weight.Bold)))
        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(7) # Se quita la columna de acciones por ahora
        self.tabla_historial.setHorizontalHeaderLabels(["Fecha", "Factura", "Producto", "Categoría", "Cliente", "Total Venta", "Vendedor"])
        self.tabla_historial.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_historial.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Hacer tabla no editable
        layout.addWidget(self.tabla_historial)
        return panel

    def cargar_datos_ordenes(self):
        self.tabla_ordenes.setRowCount(0)
        data = database.get_all_customer_orders()
        self.tabla_ordenes.setRowCount(len(data))
        for row, row_data in enumerate(data):
            # Extraer datos para facilitar el acceso
            order_id, customer_name, entry_date, required_date, product_code, product_description, sale_price, quantity, status = row_data
            
            display_data = [customer_name, entry_date, required_date, product_code, product_description, f"${sale_price:,.2f}", str(quantity), status]
            
            for col, cell_data in enumerate(display_data):
                self.tabla_ordenes.setItem(row, col, QTableWidgetItem(str(cell_data)))
            
            # --- NUEVO: Añadir botón de acción ---
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            actions_layout.setSpacing(5)

            process_button = QPushButton(qta.icon('fa5s.check-circle'), " Procesar Venta")
            
            # Si la orden ya está completada, deshabilitar el botón
            if status.lower() == 'completada':
                process_button.setEnabled(False)
                process_button.setToolTip("Esta orden ya ha sido procesada.")
            else:
                # Conectar el botón a la función que procesa la orden
                # Usamos lambda para pasar los datos de la fila actual
                process_button.clicked.connect(lambda checked, r=row_data: self.abrir_dialogo_procesar_orden(r))

            actions_layout.addWidget(process_button)
            actions_layout.addStretch()
            self.tabla_ordenes.setCellWidget(row, 8, actions_widget)

    def cargar_datos_historial(self):
        self.tabla_historial.setRowCount(0)
        data = database.get_sales_history()
        self.tabla_historial.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, cell_data in enumerate(row_data):
                if col == 5: # Columna de Total Venta
                    cell_text = f"${float(cell_data):,.2f}"
                else:
                    cell_text = str(cell_data)
                self.tabla_historial.setItem(row, col, QTableWidgetItem(cell_text))
    
    def abrir_dialogo_orden(self):
        dialog = RegisterCustomerOrderDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data and data['product_code']:
                database.add_customer_order(data['customer_id'], data['product_code'], data['quantity'], data['required_date'])
                self.cargar_datos_ordenes() # Recargar datos

    # --- NUEVO: Método para abrir el diálogo de procesamiento de orden ---
    def abrir_dialogo_procesar_orden(self, order_data_tuple):
        # Convertir tupla de datos a un diccionario para mejor manejo
        order_data = {
            'order_id': order_data_tuple[0],
            'customer_name': order_data_tuple[1],
            'product_code': order_data_tuple[4],
            'product_description': order_data_tuple[5],
            'sale_price': order_data_tuple[6],
            'quantity': order_data_tuple[7]
        }

        # 1. Verificar stock antes de continuar
        stock_disponible = database.get_product_stock(order_data['product_code'])
        if stock_disponible < order_data['quantity']:
            QMessageBox.warning(self, "Stock Insuficiente", 
                                f"No hay suficiente stock para el producto '{order_data['product_description']}'.\n"
                                f"Requerido: {order_data['quantity']}, Disponible: {stock_disponible}")
            return

        # 2. Abrir diálogo para confirmar y seleccionar vendedor
        dialog = ProcessOrderDialog(order_data, self)
        if dialog.exec():
            seller_id = dialog.get_seller_id()
            try:
                # 3. Llamar a la función de la base de datos para procesar la venta
                # Esta función debería hacer todo: crear venta, actualizar stock, cambiar estado de orden
                database.process_order_to_sale(order_data['order_id'], seller_id)
                
                QMessageBox.information(self, "Éxito", "La venta ha sido registrada correctamente.")

                # 4. Recargar ambas tablas para reflejar los cambios
                self.cargar_datos_ordenes()
                self.cargar_datos_historial()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ocurrió un error al procesar la venta:\n{e}")
