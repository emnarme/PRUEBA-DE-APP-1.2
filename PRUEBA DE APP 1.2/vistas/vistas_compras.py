# vistas/vistas_compras.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                             QLineEdit, QDialog, QFormLayout, QComboBox, QSpinBox,
                             QDialogButtonBox, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import database
import qtawesome as qta

# --- La clase RegisterPurchaseDialog no cambia ---
class RegisterPurchaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Nueva Compra"); layout = QFormLayout(self)
        self.product_combo = QComboBox(); self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 9999); self.supplier_input = QLineEdit()
        self.products = database.get_all_products()
        for product in self.products:
            self.product_combo.addItem(f"{product[1]} (Código: {product[0]})", userData=product[0])
        layout.addRow("Producto:", self.product_combo); layout.addRow("Cantidad Recibida:", self.quantity_spinbox)
        layout.addRow("Nombre del Proveedor:", self.supplier_input)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    def get_purchase_data(self):
        product_code = self.product_combo.currentData(); quantity = self.quantity_spinbox.value()
        supplier = self.supplier_input.text()
        if not supplier: return None
        return {"product_code": product_code, "quantity": quantity, "supplier_name": supplier}

# --- La clase EditPurchaseDialog no cambia ---
class EditPurchaseDialog(QDialog):
    def __init__(self, purchase_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Editar Compra {purchase_data['po']}")
        layout = QFormLayout(self)
        self.supplier_input = QLineEdit(purchase_data['supplier'])
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Recibido", "Pendiente", "Cancelado"])
        self.status_combo.setCurrentText(purchase_data['status'])
        layout.addRow("Nombre del Proveedor:", self.supplier_input)
        layout.addRow("Estado:", self.status_combo)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    def get_data(self):
        if not self.supplier_input.text(): return None
        return {"supplier_name": self.supplier_input.text(), "status": self.status_combo.currentText()}

# --- Clase Principal de la Vista de Compras ---
class VistaCompras(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("/* ... */"); self.setObjectName("main_widget")
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        header = self.crear_header(); content_area = QWidget(); content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 30, 40, 30); content_layout.setSpacing(20)
        title_layout = QHBoxLayout(); title = QLabel("Seguimiento de Órdenes de Compra")
        title.setFont(QFont("Manrope", 18, QFont.Weight.Bold))
        
        add_icon = qta.icon('fa5s.truck-loading')
        add_button = QPushButton(add_icon, " Registrar Compra")
        add_button.setStyleSheet("background-color: #0c7ff2; color: white; font-weight: bold; padding: 10px;")
        add_button.clicked.connect(self.abrir_dialogo_compra)
        
        title_layout.addWidget(title); title_layout.addStretch(); title_layout.addWidget(add_button)
        self.tabla_compras = QTableWidget(); self.tabla_compras.setColumnCount(7)
        self.tabla_compras.setHorizontalHeaderLabels(["Fecha", "No. Orden (PO)", "Producto", "Proveedor", "Cantidad", "Estado", "Acciones"])
        self.tabla_compras.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_compras.setSortingEnabled(True)
        self.tabla_compras.horizontalHeader().sectionClicked.connect(self.ordenar_tabla)
        self.sort_order = {}
        self.cargar_datos_tabla()
        content_layout.addLayout(title_layout); content_layout.addWidget(self.tabla_compras)
        layout.addWidget(header); layout.addWidget(content_area, 1)

    def crear_header(self):
        header = QFrame(); header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 15, 25, 15); self.boton_dashboard = QPushButton("← Volver al Dashboard")
        self.boton_dashboard.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_dashboard.setStyleSheet("border: none; font-size: 14px; font-weight: bold; color: #0c7ff2;")
        header_layout.addWidget(self.boton_dashboard); header_layout.addStretch()
        return header

    def cargar_datos_tabla(self):
        self.tabla_compras.setSortingEnabled(False)
        self.tabla_compras.setRowCount(0)
        datos = database.get_purchase_history()
        self.tabla_compras.setRowCount(len(datos))
        for fila, data_row in enumerate(datos):
            for col, data_cell in enumerate(data_row):
                if col == 4:
                    item = QTableWidgetItem(); item.setData(Qt.ItemDataRole.EditRole, int(data_cell)); item.setText(str(data_cell))
                else:
                    item = QTableWidgetItem(str(data_cell))
                self.tabla_compras.setItem(fila, col, item)
            
            actions_widget = QWidget(); actions_layout = QHBoxLayout(actions_widget)
            edit_icon = qta.icon('fa5s.edit', color='#0c7ff2')
            delete_icon = qta.icon('fa5s.times-circle', color='#ef4444')
            edit_button = QPushButton(edit_icon, " Editar"); edit_button.setStyleSheet("background-color: #e7f1ff; color: #0c7ff2;")
            delete_button = QPushButton(delete_icon, " Anular"); delete_button.setStyleSheet("background-color: #fdf2f2; color: #ef4444;")
            
            po_number = data_row[1]
            edit_button.clicked.connect(lambda checked, po=po_number: self.editar_compra(po))
            delete_button.clicked.connect(lambda checked, po=po_number: self.eliminar_compra(po))
            
            actions_layout.addWidget(edit_button); actions_layout.addWidget(delete_button)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            self.tabla_compras.setCellWidget(fila, 6, actions_widget)
        self.tabla_compras.setSortingEnabled(True)

    def ordenar_tabla(self, column_index):
        if column_index == 6: return
        current_order = self.sort_order.get(column_index, Qt.SortOrder.AscendingOrder)
        self.tabla_compras.sortItems(column_index, current_order)
        if current_order == Qt.SortOrder.AscendingOrder: self.sort_order[column_index] = Qt.SortOrder.DescendingOrder
        else: self.sort_order[column_index] = Qt.SortOrder.AscendingOrder

    def editar_compra(self, po_number):
        purchase_data_tuple = database.get_purchase_by_po(po_number)
        if not purchase_data_tuple: QMessageBox.critical(self, "Error", "No se pudo encontrar la orden de compra."); return
        purchase_data = {"po": po_number, "supplier": purchase_data_tuple[0], "status": purchase_data_tuple[1]}
        dialog = EditPurchaseDialog(purchase_data, self)
        if dialog.exec():
            new_data = dialog.get_data()
            if new_data:
                database.update_purchase(po_number, new_data['supplier_name'], new_data['status'])
                QMessageBox.information(self, "Éxito", "Orden de compra actualizada."); self.cargar_datos_tabla()

    def eliminar_compra(self, po_number):
        confirmacion = QMessageBox.question(self, "Confirmar Anulación", f"¿Estás seguro de que quieres anular la compra {po_number}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmacion == QMessageBox.StandardButton.Yes:
            result = database.delete_purchase(po_number)
            QMessageBox.information(self, "Resultado de la Anulación", result); self.cargar_datos_tabla()

    def abrir_dialogo_compra(self):
        dialog = RegisterPurchaseDialog(self)
        if dialog.exec():
            purchase_data = dialog.get_purchase_data()
            if purchase_data:
                result = database.register_purchase(purchase_data["product_code"], purchase_data["quantity"], purchase_data["supplier_name"])
                QMessageBox.information(self, "Resultado de la Compra", result); self.cargar_datos_tabla()
            else:
                QMessageBox.warning(self, "Error", "El nombre del proveedor es obligatorio.")
