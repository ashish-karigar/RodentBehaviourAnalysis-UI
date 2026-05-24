from pathlib import Path

from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.api_client import health_check, upload_video, get_job_status, download_result
from src.config import POLL_INTERVAL_MS


class UploadWorker(QThread):
    success = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, video_path: str):
        super().__init__()
        self.video_path = video_path

    def run(self):
        try:
            result = upload_video(self.video_path)
            self.success.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class DownloadWorker(QThread):
    success = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, job_id: str, save_path: str):
        super().__init__()
        self.job_id = job_id
        self.save_path = save_path

    def run(self):
        try:
            download_result(self.job_id, self.save_path)
            self.success.emit(self.save_path)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rodent Behaviour Analysis UI")
        self.resize(760, 500)

        self.selected_video_path = None
        self.current_job_id = None
        self.current_status = None
        self.original_video_name = None

        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll_job_status)

        self.build_ui()
        self.check_backend()

    def build_ui(self):
        root = QWidget()
        layout = QVBoxLayout(root)

        title = QLabel("Rodent Behaviour Analysis")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin: 8px;")
        layout.addWidget(title)

        backend_row = QHBoxLayout()
        self.backend_label = QLabel("Backend: checking...")
        backend_row.addWidget(self.backend_label)
        layout.addLayout(backend_row)

        file_row = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select a raw video file...")
        self.file_input.setReadOnly(True)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.select_video)

        file_row.addWidget(self.file_input)
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        action_row = QHBoxLayout()

        self.upload_btn = QPushButton("Upload & Process")
        self.upload_btn.clicked.connect(self.upload_selected_video)
        self.upload_btn.setEnabled(False)

        self.download_btn = QPushButton("Download Result")
        self.download_btn.clicked.connect(self.download_processed_result)
        self.download_btn.setEnabled(False)

        action_row.addWidget(self.upload_btn)
        action_row.addWidget(self.download_btn)
        layout.addLayout(action_row)

        self.status_label = QLabel("Status: No job submitted")
        self.status_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        layout.addWidget(self.status_label)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.setCentralWidget(root)

    def log(self, message: str):
        self.log_box.append(message)

    def check_backend(self):
        try:
            result = health_check()
            self.backend_label.setText(f"Backend: connected ({result.get('service')})")
            self.log("Backend connected.")
        except Exception as e:
            self.backend_label.setText("Backend: not connected")
            self.log(f"Backend connection failed: {e}")

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Raw Video",
            "",
            "Video Files (*.mp4 *.mov *.avi *.mkv *.m4v)",
        )

        if file_path:
            self.selected_video_path = file_path
            self.file_input.setText(file_path)
            self.upload_btn.setEnabled(True)
            self.download_btn.setEnabled(False)
            self.current_job_id = None
            self.current_status = None
            self.original_video_name = Path(file_path).name
            self.status_label.setText("Status: Video selected")
            self.log(f"Selected video: {file_path}")

    def upload_selected_video(self):
        if not self.selected_video_path:
            QMessageBox.warning(self, "No video", "Please select a video first.")
            return

        self.upload_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.status_label.setText("Status: Uploading...")
        self.log("Uploading video to backend...")

        self.upload_worker = UploadWorker(self.selected_video_path)
        self.upload_worker.success.connect(self.on_upload_success)
        self.upload_worker.error.connect(self.on_upload_error)
        self.upload_worker.start()

    def on_upload_success(self, result: dict):
        self.current_job_id = result["job_id"]
        self.original_video_name = result.get("original_video_name", self.original_video_name)

        self.status_label.setText("Status: queued")
        self.log(f"Job submitted: {self.current_job_id}")

        self.poll_timer.start(POLL_INTERVAL_MS)

    def on_upload_error(self, error: str):
        self.status_label.setText("Status: Upload failed")
        self.upload_btn.setEnabled(True)
        self.log(f"Upload failed: {error}")
        QMessageBox.critical(self, "Upload failed", error)

    def poll_job_status(self):
        if not self.current_job_id:
            return

        try:
            job = get_job_status(self.current_job_id)
            status = job.get("status")

            if status != self.current_status:
                self.current_status = status
                self.status_label.setText(f"Status: {status}")
                self.log(f"Job status: {status}")

            if status == "completed":
                self.poll_timer.stop()
                self.download_btn.setEnabled(True)
                self.log("Processing completed. Result is ready to download.")

            elif status in {"failed", "expired", "downloaded"}:
                self.poll_timer.stop()
                self.download_btn.setEnabled(False)
                self.upload_btn.setEnabled(True)
                self.log(f"Job ended with status: {status}")

        except Exception as e:
            self.log(f"Status check failed: {e}")

    def download_processed_result(self):
        if not self.current_job_id:
            QMessageBox.warning(self, "No job", "No completed job available.")
            return

        default_name = "processed_result.zip"
        if self.original_video_name:
            default_name = f"{Path(self.original_video_name).stem}.zip"

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Processed Result",
            default_name,
            "ZIP Files (*.zip)",
        )

        if not save_path:
            return

        self.download_btn.setEnabled(False)
        self.status_label.setText("Status: Downloading...")
        self.log(f"Downloading result to: {save_path}")

        self.download_worker = DownloadWorker(self.current_job_id, save_path)
        self.download_worker.success.connect(self.on_download_success)
        self.download_worker.error.connect(self.on_download_error)
        self.download_worker.start()

    def on_download_success(self, save_path: str):
        self.status_label.setText("Status: downloaded")
        self.upload_btn.setEnabled(True)
        self.log(f"Downloaded result: {save_path}")
        QMessageBox.information(self, "Download complete", f"Saved to:\n{save_path}")

    def on_download_error(self, error: str):
        self.status_label.setText("Status: Download failed")
        self.download_btn.setEnabled(True)
        self.log(f"Download failed: {error}")
        QMessageBox.critical(self, "Download failed", error)