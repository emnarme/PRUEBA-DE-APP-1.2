# vistas/vistas_notificacion.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont
import qtawesome as qta

class NotificationWidget(QWidget):
    def __init__(self, message, message_type='info', parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Estilos según el tipo de mensaje
        styles = {
            'info': ("#e7f1ff", "#0c7ff2", 'fa5s.info-circle'),
            'success': ("#dcfce7", "#15803d", 'fa5s.check-circle'),
            'warning': ("#fef3c7", "#b45309", 'fa5s.exclamation-triangle'),
            'error': ("#fdf2f2", "#ef4444", 'fa5s.times-circle')
        }
        bg_color, icon_color, icon_name = styles.get(message_type, styles['info'])

        self.setStyleSheet(f"""
            background-color: {bg_color};
            border-radius: 8px;
            border: 1px solid {icon_color};
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)

        h_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon = qta.icon(icon_name, color=icon_color)
        icon_label.setPixmap(icon.pixmap(24, 24))
        icon_label.setStyleSheet("border: none;")
        
        self.message_label = QLabel(message)
        self.message_label.setFont(QFont("Manrope", 10, QFont.Weight.Bold))
        self.message_label.setStyleSheet(f"color: {icon_color}; border: none;")
        self.message_label.setWordWrap(True)
        
        h_layout.addWidget(icon_label)
        h_layout.addWidget(self.message_label)
        h_layout.addStretch()
        
        main_layout.addLayout(h_layout)
        
        self.setFixedSize(350, 60)

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        QTimer.singleShot(4000, self.animate_out)

    def show_notification(self, pos_y):
        start_pos_x = self.parent.width()
        end_pos_x = self.parent.width() - self.width() - 10

        self.setGeometry(start_pos_x, pos_y, self.width(), self.height())
        self.show()
        
        self.animation.setStartValue(QRect(start_pos_x, pos_y, self.width(), self.height()))
        self.animation.setEndValue(QRect(end_pos_x, pos_y, self.width(), self.height()))
        self.animation.start()

    def animate_out(self):
        self.animation.setDirection(QPropertyAnimation.Direction.Backward)
        self.animation.finished.connect(self.close)
        self.animation.start()
