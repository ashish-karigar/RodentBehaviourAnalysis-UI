from PyQt6.QtCore import Qt, pyqtSignal
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

from src.config import APP_WIDTH, APP_HEIGHT
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = PROJECT_ROOT / "assets"

MOON_ICON = ASSETS_DIR / "moon.png"
SUN_ICON = ASSETS_DIR / "sun.png"
LOGOUT_ICON = ASSETS_DIR / "people-4.png"


class AppWindow(QMainWindow):
    logout_requested = pyqtSignal()
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rodent Behaviour Analysis")
        self.resize(APP_WIDTH, APP_HEIGHT)
        self.setMinimumSize(APP_WIDTH, APP_HEIGHT)

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

        self.theme_btn = QPushButton()
        self.theme_btn.setFixedSize(44, 36)
        self.theme_btn.setIconSize(QSize(22, 22))
        self.theme_btn.setToolTip("Switch theme")
        self.theme_btn.clicked.connect(self.toggle_theme)

        self.logout_btn = QPushButton()
        self.logout_btn.setFixedSize(44, 36)
        self.logout_btn.setIcon(QIcon(str(LOGOUT_ICON)))
        self.logout_btn.setIconSize(QSize(22, 22))
        self.logout_btn.setToolTip("Logout")
        self.logout_btn.clicked.connect(self.logout_requested.emit)

        top_bar.addLayout(title_box)
        top_bar.addStretch()
        top_bar.addWidget(self.theme_btn)
        top_bar.addWidget(self.logout_btn)

        self.tabs = QTabWidget()
        self.process_page = ProcessPage(self.theme)
        self.visualize_page = VisualizePage(self.theme)

        self.tabs.addTab(self.process_page, "Process")
        self.tabs.addTab(self.visualize_page, "Visualize")

        root_layout.addLayout(top_bar)
        root_layout.addWidget(self.tabs)
        footer = QLabel("Developed by @ashish.karigar")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            f"""
            color: {self.theme["border"]};
            font-size: 12px;
            font-weight: 600;
            """
        )
        root_layout.addWidget(footer)
        self.footer = footer

        self.setCentralWidget(root)

    def apply_theme(self):
        self.setStyleSheet(app_stylesheet(self.theme))

        if self.process_page:
            self.process_page.set_theme(self.theme)

        if self.visualize_page:
            self.visualize_page.set_theme(self.theme)

        icon_path = SUN_ICON if self.is_dark else MOON_ICON
        self.theme_btn.setIcon(QIcon(str(icon_path)))
        self.theme_btn.setText("")

        if hasattr(self, "footer"):
            self.footer.setStyleSheet(
                f"""
                color: #FE5E00;
                font-size: 12px;
                font-weight: 400;
                """
            )

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.theme = DARK_THEME if self.is_dark else LIGHT_THEME
        self.apply_theme()