from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QHBoxLayout,
)
from src.auth.firestore_user import (
    get_user_profile,
    set_must_change_password,
    FirestoreUserError,
)
from src.config import APP_WIDTH, APP_HEIGHT
from src.ui.theme import LIGHT_THEME, app_stylesheet
from src.auth.firebase_auth import (
    sign_in_with_email_password,
    send_password_reset_email,
    update_password,
    FirebaseAuthError,
)

class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.theme = LIGHT_THEME
        self.password_visible = False

        self.setWindowTitle("Login - Rodent Behaviour Analysis")
        self.resize(APP_WIDTH, APP_HEIGHT)
        self.setMinimumSize(APP_WIDTH, APP_HEIGHT)
        self.setStyleSheet(app_stylesheet(self.theme))
        self.auth_result = None

        self.build_ui()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Full white/light background
        page = QWidget()
        page.setStyleSheet(f"background: {self.theme['surface']};")

        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(40, 40, 40, 40)
        page_layout.setSpacing(0)

        page_layout.addStretch()

        form_card = QFrame()
        form_card.setFixedWidth(460)
        form_card.setStyleSheet(
            f"""
            QFrame {{
                background: {self.theme['surface']};
                border: none;
            }}
            """
        )

        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(16)

        title = QLabel("Rodent Behaviour Analysis")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"""
            font-size: 28px;
            font-weight: 900;
            color: {self.theme['text']};
            """
        )

        subtitle = QLabel("Secure ML Processing Portal")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            f"""
            color: {self.theme['muted']};
            font-size: 14px;
            font-weight: 600;
            """
        )

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFixedHeight(44)

        password_row = QHBoxLayout()
        password_row.setSpacing(8)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(44)

        self.eye_btn = QPushButton("👁")
        self.eye_btn.setFixedSize(48, 44)
        self.eye_btn.clicked.connect(self.toggle_password_visibility)

        password_row.addWidget(self.password_input)
        password_row.addWidget(self.eye_btn)

        change_password_row = QHBoxLayout()
        change_password_row.setSpacing(8)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("New password")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setFixedHeight(44)
        self.new_password_input.hide()

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setFixedHeight(44)
        self.confirm_password_input.hide()

        change_password_row.addWidget(self.new_password_input)
        change_password_row.addWidget(self.confirm_password_input)

        self.signin_btn = QPushButton("Sign In")
        self.signin_btn.setObjectName("PrimaryButton")
        self.signin_btn.setFixedHeight(44)
        self.signin_btn.clicked.connect(self.handle_login)
        self.signin_btn.setStyleSheet(
            f"""
            QPushButton#PrimaryButton {{
                background-color: #FE5E00;
                color: #FFFFFF;
                border: none;
            }}
            """
        )

        self.forgot_btn = QPushButton("Forgot password?")
        self.forgot_btn.setFlat(True)
        self.forgot_btn.clicked.connect(self.handle_forgot_password)
        self.forgot_btn.setStyleSheet(
            """
            color: #FE5E00;
            font-size: 13px;
            font-weight: 600;
            text-align: center;
            """
        )

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet(
            """
            color: #EF4444;
            font-size: 13px;
            font-weight: 300;
            """
        )
        self.error_label.setWordWrap(True)


        access_note = QLabel("Need access? Contact administrator.")
        access_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        access_note.setStyleSheet(
            f"""
            color: {self.theme['muted']};
            font-size: 13px;
            font-weight: 600;
            """
        )

        developer_note = QLabel("Developed by @ashish.karigar")
        developer_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        developer_note.setStyleSheet(
            f"""
            color: #FE5E00;
            font-size: 12px;
            font-weight: 500;
            """
        )

        form_layout.addWidget(title)
        form_layout.addWidget(subtitle)
        form_layout.addSpacing(18)
        form_layout.addWidget(self.email_input)
        form_layout.addLayout(password_row)
        form_layout.addLayout(change_password_row)
        form_layout.addWidget(self.signin_btn)
        form_layout.addWidget(self.forgot_btn)
        form_layout.addWidget(self.error_label)
        form_layout.addWidget(access_note)
        form_layout.addWidget(developer_note)
        form_layout.addWidget(access_note)
        form_layout.addWidget(developer_note)


        page_layout.addWidget(form_card, alignment=Qt.AlignmentFlag.AlignCenter)
        page_layout.addStretch()

        root.addWidget(page)

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible

        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.eye_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.eye_btn.setText("👁")

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        self.set_error("")

        if not email or not password:
            self.set_error("Enter email and password.")
            return

        self.signin_btn.setEnabled(False)
        self.signin_btn.setText("Signing in...")

        try:
            auth_result = sign_in_with_email_password(email, password)
            self.auth_result = auth_result

            profile = get_user_profile(
                local_id=auth_result["local_id"],
                id_token=auth_result["id_token"],
            )

            if profile.get("must_change_password"):
                self.show_password_change_mode()
                return

            self.login_success.emit(auth_result)

        except FirebaseAuthError as e:
            self.set_error(str(e))

        except FirestoreUserError as e:
            self.set_error(str(e))

        except Exception as e:
            self.set_error(f"Unexpected error: {e}")

        finally:
            self.signin_btn.setEnabled(True)
            if self.auth_result and self.new_password_input.isVisible():
                self.signin_btn.setText("Update Password")
            else:
                self.signin_btn.setText("Sign In")

    def handle_forgot_password(self):
        email = self.email_input.text().strip()
        self.error_label.setText("")

        if not email:
            self.error_label.setText("Enter your email first, then click Forgot password.")
            return

        try:
            send_password_reset_email(email)
            self.error_label.setStyleSheet(
                """
                color: #22C55E;
                font-size: 13px;
                font-weight: 600;
                """
            )
            self.error_label.setText("If this email exists, a password reset link has been sent.")

        except FirebaseAuthError as e:
            self.error_label.setStyleSheet(
                """
                color: #EF4444;
                font-size: 13px;
                font-weight: 600;
                """
            )
            self.error_label.setText(str(e))

        except Exception as e:
            self.error_label.setText(f"Unexpected error: {e}")

    def set_error(self, message: str, success: bool = False):
        color = "#22C55E" if success else "#EF4444"
        self.error_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 13px;
            font-weight: 600;
            """
        )
        self.error_label.setText(message)

    def show_password_change_mode(self):
        self.set_error("First login detected. Please set a new password.", success=False)

        self.email_input.setEnabled(False)
        self.password_input.setEnabled(False)
        self.forgot_btn.hide()

        self.new_password_input.show()
        self.confirm_password_input.show()

        self.new_password_input.textChanged.connect(self.validate_new_password_fields)
        self.confirm_password_input.textChanged.connect(self.validate_new_password_fields)

        self.signin_btn.clicked.disconnect()
        self.signin_btn.clicked.connect(self.handle_password_update)
        self.signin_btn.setText("Update Password")

    def handle_password_update(self):
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        self.set_error("")

        if not new_password or not confirm_password:
            self.set_error("Enter and confirm your new password.")
            return

        if new_password != confirm_password:
            self.set_error("Passwords do not match.")
            return

        if len(new_password) < 8:
            self.set_error("Password must be at least 8 characters.")
            return

        self.signin_btn.setEnabled(False)
        self.signin_btn.setText("Updating...")

        try:
            updated_auth = update_password(
                self.auth_result["id_token"],
                new_password,
            )

            set_must_change_password(
                local_id=updated_auth["local_id"],
                id_token=updated_auth["id_token"],
                value=False,
            )

            self.set_error("Password updated successfully.", success=True)
            self.login_success.emit(updated_auth)

        except FirebaseAuthError as e:
            self.set_error(str(e))

        except Exception as e:
            self.set_error(f"Unexpected error: {e}")

        finally:
            self.signin_btn.setEnabled(True)
            self.signin_btn.setText("Update Password")

    def validate_new_password_fields(self):
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        default_style = """
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 10px;
        """

        green_style = """
            border: 1.5px solid #22C55E;
            border-radius: 10px;
            padding: 10px;
        """

        if len(new_password) >= 8:
            self.new_password_input.setStyleSheet(green_style)
        else:
            self.new_password_input.setStyleSheet(default_style)

        if confirm_password and confirm_password == new_password:
            self.confirm_password_input.setStyleSheet(green_style)
        else:
            self.confirm_password_input.setStyleSheet(default_style)