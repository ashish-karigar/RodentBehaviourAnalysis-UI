from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class VisualizePage(QWidget):
    def __init__(self, theme: dict):
        super().__init__()
        self.theme = theme
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Visualize page coming next.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

    def set_theme(self, theme: dict):
        self.theme = theme