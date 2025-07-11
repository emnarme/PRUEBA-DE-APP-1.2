# vistas/vistas_usuarios.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                             QLineEdit, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import database
import qtawesome as qta

# --- Las clases de Diálogo no cambian ---
class AddUserDialog(QDialog):
    # ... (código existente sin cambios)
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Añadir Nuevo Usuario"); self.form_layout = QFormLayout(self)
        self.name_input = QLineEdit(self); self.email_input = QLineEdit(self)
        self.password_input = QLineEdit(self); self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.role_input = QComboBox(self); self.role_input.addItems(["Administrador", "Vendedor", "Almacenista"])
        self.form_layout.addRow("Nombre Completo:", self.name_input); self.form_layout.addRow("Correo Electrónico:", self.email_input)
        self.form_layout.addRow("Contraseña:", self.password_input); self.form_layout.addRow("Rol:", self.role_input)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject); self.form_layout.addWidget(self.button_box)
    def get_data(self):
        if not all([self.name_input.text(), self.email_input.text(), self.password_input.text()]): return None
        return {"name": self.name_input.text(), "email": self.email_input.text(), "password": self.password_input.text(), "role": self.role_input.currentText()}
class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Cambiar Contraseña"); layout = QFormLayout(self)
        self.new_password1 = QLineEdit(); self.new_password1.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password2 = QLineEdit(); self.new_password2.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Nueva Contraseña:", self.new_password1); layout.addRow("Confirmar Contraseña:", self.new_password2)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject); layout.addWidget(self.button_box)
    def get_password(self):
        if self.new_password1.text() == self.new_password2.text() and self.new_password1.text(): return self.new_password1.text()
        return None
class EditUserDialog(QDialog):
    def __init__(self, user_data, parent=None):
        super().__init__(parent); self.setWindowTitle("Editar Usuario"); self.user_email = user_data['email']
        self.main_layout = QVBoxLayout(self); form_layout = QFormLayout()
        self.name_input = QLineEdit(user_data['name']); self.email_input = QLineEdit(user_data['email'])
        self.role_input = QComboBox(); self.role_input.addItems(["Administrador", "Vendedor", "Almacenista"])
        self.role_input.setCurrentText(user_data['role'])
        form_layout.addRow("Nombre Completo:", self.name_input); form_layout.addRow("Correo Electrónico:", self.email_input)
        form_layout.addRow("Rol:", self.role_input)
        self.change_password_button = QPushButton("Cambiar Contraseña..."); self.change_password_button.clicked.connect(self.open_change_password_dialog)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject)
        self.main_layout.addLayout(form_layout); self.main_layout.addWidget(self.change_password_button); self.main_layout.addWidget(self.button_box)
    def open_change_password_dialog(self):
        dialog = ChangePasswordDialog(self)
        if dialog.exec():
            new_password = dialog.get_password()
            if new_password:
                database.update_user_password(self.user_email, new_password)
                self.parent().window().show_notification("La contraseña ha sido actualizada.", "success")
            else:
                self.parent().window().show_notification("Las contraseñas no coinciden o están vacías.", "error")
    def get_data(self):
        if not all([self.name_input.text(), self.email_input.text()]): return None
        return {"name": self.name_input.text(), "email": self.email_input.text(), "role": self.role_input.currentText()}

# --- Clase Principal de la Vista de Usuarios ---
class VistaUsuarios(QWidget):
    def __init__(self):
        super().__init__()
        # ... (código de la interfaz sin cambios)
        self.setStyleSheet("/* ... */"); self.setObjectName("main_widget")
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        header = self.crear_header(); content_area = QWidget(); content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(40, 30, 40, 30); content_layout.setSpacing(20)
        title_layout = QHBoxLayout(); title = QLabel("Gestión de Usuarios")
        title.setFont(QFont("Manrope", 18, QFont.Weight.Bold)); add_icon = qta.icon('fa5s.user-plus'); add_button = QPushButton(add_icon, " Añadir Usuario")
        add_button.setStyleSheet("background-color: #0c7ff2; color: white; font-weight: bold; padding: 10px;")
        add_button.clicked.connect(self.abrir_dialogo_anadir_usuario); title_layout.addWidget(title); title_layout.addStretch(); title_layout.addWidget(add_button)
        self.tabla_usuarios = QTableWidget(); self.tabla_usuarios.setColumnCount(4); self.tabla_usuarios.setHorizontalHeaderLabels(["Nombre Completo", "Correo Electrónico", "Rol", "Acciones"])
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_usuarios.setSortingEnabled(True); self.tabla_usuarios.horizontalHeader().sectionClicked.connect(self.ordenar_tabla); self.sort_order = {}
        self.cargar_datos_tabla(); content_layout.addLayout(title_layout); content_layout.addWidget(self.tabla_usuarios)
        layout.addWidget(header); layout.addWidget(content_area, 1)

    def crear_header(self):
        # ... (código existente sin cambios)
        header = QFrame(); header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 15, 25, 15); self.boton_dashboard = QPushButton("← Volver al Dashboard")
        self.boton_dashboard.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_dashboard.setStyleSheet("border: none; font-size: 14px; font-weight: bold; color: #0c7ff2;")
        header_layout.addWidget(self.boton_dashboard); header_layout.addStretch()
        return header

    def cargar_datos_tabla(self):
        # ... (código existente sin cambios)
        self.tabla_usuarios.setSortingEnabled(False); self.tabla_usuarios.setRowCount(0); datos = database.get_all_users()
        self.tabla_usuarios.setRowCount(len(datos))
        for fila, data_row in enumerate(datos):
            for col, data_cell in enumerate(data_row): self.tabla_usuarios.setItem(fila, col, QTableWidgetItem(str(data_cell)))
            actions_widget = QWidget(); actions_layout = QHBoxLayout(actions_widget)
            edit_icon = qta.icon('fa5s.edit', color='#0c7ff2'); delete_icon = qta.icon('fa5s.trash-alt', color='#ef4444')
            edit_button = QPushButton(edit_icon, " Editar"); edit_button.setStyleSheet("background-color: #e7f1ff; color: #0c7ff2;")
            delete_button = QPushButton(delete_icon, " Eliminar"); delete_button.setStyleSheet("background-color: #fdf2f2; color: #ef4444;")
            email = data_row[1]
            edit_button.clicked.connect(lambda checked, e=email: self.editar_usuario_por_email(e))
            delete_button.clicked.connect(lambda checked, e=email: self.eliminar_usuario(e))
            actions_layout.addWidget(edit_button); actions_layout.addWidget(delete_button); actions_layout.setContentsMargins(5, 5, 5, 5)
            self.tabla_usuarios.setCellWidget(fila, 3, actions_widget)
        self.tabla_usuarios.setSortingEnabled(True)

    def ordenar_tabla(self, column_index):
        # ... (código existente sin cambios)
        if column_index == 3: return
        current_order = self.sort_order.get(column_index, Qt.SortOrder.AscendingOrder)
        self.tabla_usuarios.sortItems(column_index, current_order)
        if current_order == Qt.SortOrder.AscendingOrder: self.sort_order[column_index] = Qt.SortOrder.DescendingOrder
        else: self.sort_order[column_index] = Qt.SortOrder.AscendingOrder

    def editar_usuario_por_email(self, email):
        user_data_tuple = database.get_user_by_email(email)
        if not user_data_tuple: self.window().show_notification("No se pudo encontrar al usuario.", "error"); return
        user_data_dict = {"name": user_data_tuple[0], "email": user_data_tuple[1], "role": user_data_tuple[2]}
        dialog = EditUserDialog(user_data_dict, self)
        if dialog.exec():
            new_data = dialog.get_data()
            if new_data:
                success = database.update_user(email, new_data['name'], new_data['email'], new_data['role'])
                if success: self.window().show_notification("Usuario actualizado correctamente.", "success"); self.cargar_datos_tabla()
                else: self.window().show_notification("No se pudo actualizar (el email podría ya existir).", "error")

    def eliminar_usuario(self, email):
        user_data = database.get_user_by_email(email); nombre = user_data[0] if user_data else email
        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", f"¿Estás seguro de que quieres eliminar al usuario '{nombre}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmacion == QMessageBox.StandardButton.Yes:
            success = database.delete_user(email)
            if success: self.window().show_notification("Usuario eliminado correctamente.", "success"); self.cargar_datos_tabla()
            else: self.window().show_notification("No se pudo eliminar (el usuario 'admin' está protegido).", "error")

    def abrir_dialogo_anadir_usuario(self):
        dialog = AddUserDialog(self)
        if dialog.exec():
            new_user_data = dialog.get_data()
            if new_user_data:
                success = database.add_user(new_user_data['name'], new_user_data['email'], new_user_data['password'], new_user_data['role'])
                if success: self.window().show_notification("Usuario añadido con éxito.", "success"); self.cargar_datos_tabla()
                else: self.window().show_notification("El correo electrónico ya existe.", "error")
            else:
                self.window().show_notification("Todos los campos son obligatorios.", "warning")
