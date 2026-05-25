import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from src.auth.auth_state import AuthState
from src.config import validate_config
from src.ui.app_window import AppWindow
from src.ui.login_window import LoginWindow


def main():
    app = QApplication(sys.argv)

    try:
        validate_config()
    except RuntimeError as e:
        QMessageBox.critical(None, "Configuration Error", str(e))
        sys.exit(1)

    auth_state = AuthState()

    windows = {
        "login": None,
        "app": None,
    }

    def show_login():
        auth_state.logout()

        login_window = LoginWindow()
        windows["login"] = login_window

        def on_login_success(auth_result: dict):
            auth_state.login(auth_result)
            show_app()
            login_window.close()

        login_window.login_success.connect(on_login_success)
        login_window.show()

    def show_app():
        app_window = AppWindow(auth_state)
        windows["app"] = app_window

        def on_logout():
            app_window.close()
            show_login()

        app_window.logout_requested.connect(on_logout)
        app_window.show()

    show_login()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()