LIGHT_THEME = {
    "bg": "#F7F8FA",
    "surface": "#FFFFFF",
    "surface_alt": "#F1F5F9",
    "text": "#111827",
    "muted": "#6B7280",
    "border": "#E5E7EB",
    "accent": "#B7F000",
    "accent_text": "#111827",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#3B82F6",
}

DARK_THEME = {
    "bg": "#0F172A",
    "surface": "#111827",
    "surface_alt": "#1F2937",
    "text": "#F9FAFB",
    "muted": "#9CA3AF",
    "border": "#334155",
    "accent": "#B7F000",
    "accent_text": "#111827",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#60A5FA",
}


def app_stylesheet(theme: dict) -> str:
    return f"""
    QMainWindow {{
        background: {theme["bg"]};
    }}

    QWidget {{
        font-family: Arial;
        font-size: 14px;
        color: {theme["text"]};
    }}

    QLabel {{
        color: {theme["text"]};
    }}

    QFrame#Card {{
        background: {theme["surface"]};
        border: 1px solid {theme["border"]};
        border-radius: 16px;
    }}

    QLineEdit {{
        background: {theme["surface"]};
        border: 1px solid {theme["border"]};
        border-radius: 10px;
        padding: 10px;
        color: {theme["text"]};
    }}
    
        QListWidget {{
        background: {theme["surface"]};
        border: 1px solid {theme["border"]};
        border-radius: 12px;
        padding: 6px;
        color: {theme["text"]};
    }}

    QListWidget::item {{
        padding: 12px;
        border-bottom: 1px solid {theme["border"]};
    }}

    QListWidget::item:selected {{
        background: {theme["surface_alt"]};
        color: {theme["text"]};
        border-radius: 8px;
    }}

    QTextEdit {{
        background: {theme["surface"]};
        border: 1px solid {theme["border"]};
        border-radius: 12px;
        padding: 8px;
        color: {theme["text"]};
    }}

    QPushButton {{
        background: {theme["surface_alt"]};
        border: 1px solid {theme["border"]};
        border-radius: 10px;
        padding: 9px 14px;
        color: {theme["text"]};
    }}

    QPushButton:hover {{
        border: 1px solid {theme["accent"]};
    }}

    QPushButton#PrimaryButton {{
        background: {theme["accent"]};
        color: {theme["accent_text"]};
        border: none;
        font-weight: bold;
    }}

    QPushButton#DangerButton {{
        background: {theme["danger"]};
        color: white;
        border: none;
        font-weight: bold;
    }}

    QPushButton:disabled {{
        opacity: 0.8;
    }}

    QTabWidget::pane {{
        border: 0;
    }}

    QTabBar::tab {{
        background: {theme["surface_alt"]};
        color: {theme["muted"]};
        padding: 10px 22px;
        border-radius: 10px;
        margin-right: 6px;
    }}

    QTabBar::tab:selected {{
        background: {theme["accent"]};
        color: {theme["accent_text"]};
        font-weight: bold;
    }}
    
        QScrollArea {{
        background: transparent;
        border: none;
    }}

    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}

    QFrame#JobCard {{
        background: {theme["surface"]};
        border: 1px solid {theme["border"]};
        border-radius: 16px;
    }}

    QProgressBar {{
        background: {theme["surface_alt"]};
        border: none;
        border-radius: 4px;
    }}

    QProgressBar::chunk {{
        background: {theme["accent"]};
        border-radius: 4px;
    }}

    QPushButton#MutedButton {{
        background: {theme["surface_alt"]};
        color: {theme["muted"]};
        border: 1px solid {theme["border"]};
        font-weight: bold;
    }}

    QPushButton#WarningButton {{
        background: {theme["warning"]};
        color: #111827;
        border: none;
        font-weight: bold;
    }}
    
    QPushButton#DownloadedButton {{
        background: {theme["surface_alt"]};
        color: {theme["muted"]};
        border: 1px solid {theme["success"]};
        font-weight: bold;
    }}
    """