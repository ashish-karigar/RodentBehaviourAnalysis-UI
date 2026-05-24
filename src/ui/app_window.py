from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.ui.pages.process_page import ProcessPage
from src.ui.pages.visualize_page import VisualizePage
from src.ui.theme import LIGHT_THEME, DARK_THEME, app_stylesheet


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rodent Behaviour Analysis")
        self.resize(1100, 720)

        self.is_dark = False
        self.theme = LIGHT_THEME

        self.process_page = None
        self.visualize_page = None

        self.build_ui()
        self.apply_theme()

    def build_ui(self):
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(22, 18, 22, 18)
        root_layout.setSpacing(16)

        top_bar = QHBoxLayout()

        title_box = QVBoxLayout()
        title = QLabel("Rodent Behaviour Analysis")
        title.setStyleSheet("font-size: 24px; font-weight: 800;")
        subtitle = QLabel("Upload, process, and download rodent behavior analysis outputs")
        subtitle.setStyleSheet("font-size: 13px; color: #6B7280;")

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        self.theme_btn = QPushButton("Dark Mode")
        self.theme_btn.clicked.connect(self.toggle_theme)

        top_bar.addLayout(title_box)
        top_bar.addStretch()
        top_bar.addWidget(self.theme_btn)

        self.tabs = QTabWidget()
        self.process_page = ProcessPage(self.theme)
        self.visualize_page = VisualizePage(self.theme)

        self.tabs.addTab(self.process_page, "Process")
        self.tabs.addTab(self.visualize_page, "Visualize")

        root_layout.addLayout(top_bar)
        root_layout.addWidget(self.tabs)

        self.setCentralWidget(root)

    def apply_theme(self):
        self.setStyleSheet(app_stylesheet(self.theme))

        if self.process_page:
            self.process_page.set_theme(self.theme)

        if self.visualize_page:
            self.visualize_page.set_theme(self.theme)

        self.theme_btn.setText("Light Mode" if self.is_dark else "Dark Mode")

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.theme = DARK_THEME if self.is_dark else LIGHT_THEME
        self.apply_theme()