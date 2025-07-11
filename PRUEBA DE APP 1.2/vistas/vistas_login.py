# vistas/vistas_login.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QSpacerItem, QSizePolicy, QFrame)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
import database

class VistaLogin(QWidget):
    # Ahora la señal emite una cadena (el rol)
    login_exitoso = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # ... (código de la interfaz sin cambios)
        self.setStyleSheet("/* ... */")
        main_layout = QVBoxLayout(self); main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_container = QFrame(); form_container.setObjectName("form_container"); form_container.setFixedWidth(400)
        layout = QVBoxLayout(form_container); layout.setContentsMargins(40, 30, 40, 30); layout.setSpacing(15); layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label = QLabel(); logo_label.setFixedSize(64, 64); logo_label.setStyleSheet("background-color: #e0e0e0; border-radius: 8px;"); logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo = QLabel("DEMOGA EMALDO"); titulo.setObjectName("titulo"); titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo = QLabel("Iniciar Sesión"); subtitulo.setObjectName("subtitulo"); subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.usuario_input, usuario_frame = self.crear_campo_con_icono("📧", "Correo Electrónico (admin)")
        self.password_input, password_frame = self.crear_campo_con_icono("🔒", "Contraseña (1234)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Iniciar Sesión"); self.login_button.setObjectName("login_button")
        self.error_label = QLabel(""); self.error_label.setObjectName("error_label"); self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.error_label.setHidden(True)
        layout.addWidget(logo_label); layout.addSpacing(10); layout.addWidget(titulo); layout.addWidget(subtitulo); layout.addSpacing(20)
        layout.addWidget(usuario_frame); layout.addWidget(password_frame); layout.addWidget(self.error_label); layout.addSpacing(10); layout.addWidget(self.login_button)
        main_layout.addWidget(form_container); self.login_button.clicked.connect(self.check_login)

    def crear_campo_con_icono(self, icono, placeholder_text):
        frame = QFrame(); frame.setObjectName("input_frame"); layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 0, 0, 0); layout.setSpacing(5); icon_label = QLabel(icono)
        line_edit = QLineEdit(); line_edit.setPlaceholderText(placeholder_text); layout.addWidget(icon_label); layout.addWidget(line_edit)
        return line_edit, frame

    def check_login(self):
        email = self.usuario_input.text()
        password = self.password_input.text()
        
        user_role = database.check_user_credentials(email, password)
        if user_role:
            self.error_label.setHidden(True)
            self.login_exitoso.emit(user_role) # Emitir el rol del usuario
        else:
            self.error_label.setText("Correo o contraseña incorrectos.")
            self.error_label.setHidden(False)
