# vistas/vistas_contactos.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                             QTabWidget, QDialog, QFormLayout, QLineEdit, QMessageBox,
                             QDialogButtonBox, QComboBox, QSpinBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import database
import qtawesome as qta

# --- Diálogo para Añadir/Editar Cliente ---
class CustomerDialog(QDialog):
    def __init__(self, customer_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Datos del Cliente" if not customer_data else "Editar Cliente")
        layout = QFormLayout(self)
        
        # Llenar con datos existentes si es para editar, o dejar en blanco si es para añadir
        self.name_input = QLineEdit(customer_data[1] if customer_data else "")
        self.email_input = QLineEdit(customer_data[2] if customer_data else "")
        self.phone_input = QLineEdit(customer_data[3] if customer_data else "")
        self.address_input = QLineEdit(customer_data[4] if customer_data else "")
        self.razon_social_input = QLineEdit(customer_data[5] if customer_data else "")
        
        self.tipo_pago_input = QComboBox()
        self.tipo_pago_input.addItems(["PUE - Pago en una sola exhibición", "PPD - Pago en parcialidades o diferido", "Efectivo", "Transferencia"])
        if customer_data: self.tipo_pago_input.setCurrentText(customer_data[6])
            
        self.uso_cfdi_input = QComboBox()
        self.uso_cfdi_input.addItems(["G01 - Adquisición de mercancías", "G03 - Gastos en general", "I08 - Otra maquinaria y equipo"])
        if customer_data: self.uso_cfdi_input.setCurrentText(customer_data[7])
            
        self.payment_terms_input = QSpinBox()
        self.payment_terms_input.setRange(0, 120)
        if customer_data: self.payment_terms_input.setValue(customer_data[8])

        layout.addRow("Nombre:", self.name_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Teléfono:", self.phone_input)
        layout.addRow("Dirección:", self.address_input)
        layout.addRow("Razón Social:", self.razon_social_input)
        layout.addRow("Tipo de Pago:", self.tipo_pago_input)
        layout.addRow("Uso de CFDI:", self.uso_cfdi_input)
        layout.addRow("Plazo de Pago (días):", self.payment_terms_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        if not self.name_input.text(): return None
        return {
            "name": self.name_input.text(), "email": self.email_input.text(),
            "phone": self.phone_input.text(), "address": self.address_input.text(),
            "razon_social": self.razon_social_input.text(),
            "tipo_pago": self.tipo_pago_input.currentText(),
            "uso_cfdi": self.uso_cfdi_input.currentText(),
            "payment_terms": self.payment_terms_input.value()
        }

# --- Diálogo para Añadir/Editar Proveedor ---
class SupplierDialog(QDialog):
    def __init__(self, supplier_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Datos del Proveedor" if not supplier_data else "Editar Proveedor")
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit(supplier_data[1] if supplier_data else "")
        self.contact_input = QLineEdit(supplier_data[2] if supplier_data else "")
        self.email_input = QLineEdit(supplier_data[3] if supplier_data else "")
        self.phone_input = QLineEdit(supplier_data[4] if supplier_data else "")
        self.address_input = QLineEdit(supplier_data[5] if supplier_data else "")
        self.razon_social_input = QLineEdit(supplier_data[6] if supplier_data else "")
        
        self.tipo_pago_input = QComboBox()
        self.tipo_pago_input.addItems(["PUE - Pago en una sola exhibición", "PPD - Pago en parcialidades o diferido", "Efectivo", "Transferencia"])
        if supplier_data: self.tipo_pago_input.setCurrentText(supplier_data[7])
            
        self.uso_cfdi_input = QComboBox()
        self.uso_cfdi_input.addItems(["G01 - Adquisición de mercancías", "G03 - Gastos en general", "I08 - Otra maquinaria y equipo", "P01 - Por definir"])
        if supplier_data: self.uso_cfdi_input.setCurrentText(supplier_data[8])
            
        self.payment_terms_input = QSpinBox()
        self.payment_terms_input.setRange(0, 120)
        if supplier_data: self.payment_terms_input.setValue(supplier_data[9])

        layout.addRow("Nombre Empresa:", self.name_input)
        layout.addRow("Persona de Contacto:", self.contact_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Teléfono:", self.phone_input)
        layout.addRow("Dirección:", self.address_input)
        layout.addRow("Razón Social:", self.razon_social_input)
        layout.addRow("Tipo de Pago:", self.tipo_pago_input)
        layout.addRow("Uso de CFDI:", self.uso_cfdi_input)
        layout.addRow("Plazo de Pago (días):", self.payment_terms_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        if not self.name_input.text(): return None
        return {
            "name": self.name_input.text(), "contact_person": self.contact_input.text(),
            "email": self.email_input.text(), "phone": self.phone_input.text(),
            "address": self.address_input.text(), "razon_social": self.razon_social_input.text(),
            "tipo_pago": self.tipo_pago_input.currentText(), "uso_cfdi": self.uso_cfdi_input.currentText(),
            "payment_terms": self.payment_terms_input.value()
        }

# --- Vista Principal de Contactos ---
class VistaContactos(QWidget):
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
        self.tab_clientes = self.crear_panel_clientes()
        self.tab_proveedores = self.crear_panel_proveedores()
        
        self.tab_widget.addTab(self.tab_clientes, "  Clientes  ")
        self.tab_widget.addTab(self.tab_proveedores, "  Proveedores  ")
        
        content_layout.addWidget(self.tab_widget)
        main_layout.addWidget(header); main_layout.addWidget(content_area)

    def crear_header(self):
        header = QFrame(); header_layout = QHBoxLayout(header); header_layout.setContentsMargins(25, 15, 25, 15)
        self.boton_dashboard = QPushButton("← Volver al Dashboard")
        self.boton_dashboard.setStyleSheet("border: none; font-size: 14px; font-weight: bold; color: #0c7ff2;")
        header_layout.addWidget(self.boton_dashboard); header_layout.addStretch()
        return header

    def crear_panel_clientes(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setSpacing(15); top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Gestión de Clientes", font=QFont("Manrope", 18, QFont.Weight.Bold)))
        top_layout.addStretch(); add_button = QPushButton(qta.icon('fa5s.user-plus'), " Añadir Cliente")
        add_button.clicked.connect(self.anadir_cliente); top_layout.addWidget(add_button)
        
        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(9)
        self.tabla_clientes.setHorizontalHeaderLabels(["Nombre", "Email", "Teléfono", "Dirección", "Razón Social", "Tipo de Pago", "Uso CFDI", "Plazo (días)", "Acciones"])
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addLayout(top_layout); layout.addWidget(self.tabla_clientes)
        return panel

    def crear_panel_proveedores(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setSpacing(15); top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Gestión de Proveedores", font=QFont("Manrope", 18, QFont.Weight.Bold)))
        top_layout.addStretch(); add_button = QPushButton(qta.icon('fa5s.truck'), " Añadir Proveedor")
        add_button.clicked.connect(self.anadir_proveedor); top_layout.addWidget(add_button)
        
        self.tabla_proveedores = QTableWidget()
        self.tabla_proveedores.setColumnCount(10)
        self.tabla_proveedores.setHorizontalHeaderLabels(["Empresa", "Contacto", "Email", "Teléfono", "Dirección", "Razón Social", "Tipo de Pago", "Uso CFDI", "Plazo (días)", "Acciones"])
        self.tabla_proveedores.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addLayout(top_layout); layout.addWidget(self.tabla_proveedores)
        return panel

    def cargar_clientes(self):
        self.tabla_clientes.setRowCount(0); data = database.get_all_customers()
        self.tabla_clientes.setRowCount(len(data))
        for row, row_data in enumerate(data):
            customer_id = row_data[0]
            for col, cell_data in enumerate(row_data[1:]):
                self.tabla_clientes.setItem(row, col, QTableWidgetItem(str(cell_data)))
            self.tabla_clientes.setCellWidget(row, 8, self.crear_botones_acciones("cliente", customer_id, row_data))

    def cargar_proveedores(self):
        self.tabla_proveedores.setRowCount(0); data = database.get_all_suppliers()
        self.tabla_proveedores.setRowCount(len(data))
        for row, row_data in enumerate(data):
            supplier_id = row_data[0]
            for col, cell_data in enumerate(row_data[1:]):
                self.tabla_proveedores.setItem(row, col, QTableWidgetItem(str(cell_data)))
            self.tabla_proveedores.setCellWidget(row, 9, self.crear_botones_acciones("proveedor", supplier_id, row_data))

    def crear_botones_acciones(self, entity_type, entity_id, data):
        widget = QWidget(); layout = QHBoxLayout(widget); edit_button = QPushButton(qta.icon('fa5s.edit'), " Editar")
        delete_button = QPushButton(qta.icon('fa5s.trash-alt'), " Eliminar")
        if entity_type == "cliente":
            edit_button.clicked.connect(lambda _, eid=entity_id, d=data: self.editar_cliente(eid, d))
            delete_button.clicked.connect(lambda _, eid=entity_id: self.eliminar_cliente(eid))
        else:
            edit_button.clicked.connect(lambda _, eid=entity_id, d=data: self.editar_proveedor(eid, d))
            delete_button.clicked.connect(lambda _, eid=entity_id: self.eliminar_proveedor(eid))
        layout.addWidget(edit_button); layout.addWidget(delete_button); layout.setContentsMargins(0,0,0,0)
        return widget

    def anadir_cliente(self):
        dialog = CustomerDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data: database.add_customer(**data); self.cargar_clientes()
    
    def editar_cliente(self, customer_id, data):
        dialog = CustomerDialog(customer_data=data, parent=self)
        if dialog.exec():
            new_data = dialog.get_data()
            if new_data: database.update_customer(customer_id, **new_data); self.cargar_clientes()

    def eliminar_cliente(self, customer_id):
        if QMessageBox.question(self, "Confirmar", "¿Seguro que quieres eliminar este cliente?") == QMessageBox.StandardButton.Yes:
            database.delete_customer(customer_id); self.cargar_clientes()

    def anadir_proveedor(self):
        dialog = SupplierDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data: database.add_supplier(**data); self.cargar_proveedores()

    def editar_proveedor(self, supplier_id, data):
        dialog = SupplierDialog(supplier_data=data, parent=self)
        if dialog.exec():
            new_data = dialog.get_data()
            if new_data: database.update_supplier(supplier_id, **new_data); self.cargar_proveedores()

    def eliminar_proveedor(self, supplier_id):
        if QMessageBox.question(self, "Confirmar", "¿Seguro que quieres eliminar este proveedor?") == QMessageBox.StandardButton.Yes:
            database.delete_supplier(supplier_id); self.cargar_proveedores()
