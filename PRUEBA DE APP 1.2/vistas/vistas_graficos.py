# vistas/vistas_graficos.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class MplCanvas(FigureCanvas):
    """Base class for a Matplotlib canvas widget to embed in PyQt."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        
        self.setParent(parent)
        self.fig.patch.set_alpha(0) # Fondo transparente

class PieChartWidget(QWidget):
    """Widget para mostrar un gráfico de torta."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.canvas = MplCanvas(self, width=5, height=4, dpi=80)
        layout.addWidget(self.canvas)
        self.update_chart([], []) # Gráfico inicial vacío

    def update_chart(self, labels, sizes):
        self.canvas.axes.clear()
        if not sizes or sum(sizes) == 0:
            self.canvas.axes.text(0.5, 0.5, 'No hay datos de ventas', ha='center', va='center')
        else:
            colors = ['#4ade80', '#22d3ee', '#f43f5e', '#a855f7', '#facc15']
            self.canvas.axes.pie(sizes, labels=None, autopct='%1.1f%%', startangle=90, colors=colors,
                                wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
            self.canvas.axes.legend(labels, loc="center left", bbox_to_anchor=(0.9, 0, 0.5, 1))
            self.canvas.axes.axis('equal')
        self.canvas.axes.set_facecolor('#FFFFFF00')
        self.canvas.draw()

class LineChartWidget(QWidget):
    """Widget para mostrar un gráfico de líneas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.canvas = MplCanvas(self, width=6, height=4, dpi=80)
        layout.addWidget(self.canvas)
        self.update_chart({}) # Gráfico inicial vacío

    def update_chart(self, monthly_sales):
        self.canvas.axes.clear()
        if not monthly_sales:
            self.canvas.axes.text(0.5, 0.5, 'No hay datos de ventas', ha='center', va='center')
        else:
            months = list(monthly_sales.keys())
            sales = list(monthly_sales.values())
            
            self.canvas.axes.plot(months, sales, marker='o', linestyle='-', color='#0c7ff2')
            self.canvas.axes.fill_between(months, sales, color='#0c7ff2', alpha=0.1)
            
            self.canvas.axes.set_ylabel('Monto de Venta ($)', fontsize=10)
            self.canvas.axes.grid(True, linestyle='--', alpha=0.6)
            self.canvas.axes.tick_params(axis='x', rotation=25, labelsize=8)
            
            # --- LÍNEA CORREGIDA ---
            # Accedemos a 'fig' a través de 'self.canvas'
            self.canvas.fig.tight_layout()

        self.canvas.axes.set_facecolor('#FFFFFF00')
        self.canvas.draw()
