from pathlib import Path
import os
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QCheckBox,
)

from src.api_client import upload_video, get_job_status, download_result
from src.config import POLL_INTERVAL_MS
from src.ui.components.job_card import JobCard


VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}


class UploadWorker(QThread):
    success = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, video_path: str):
        super().__init__()
        self.video_path = video_path

    def run(self):
        try:
            self.success.emit(upload_video(self.video_path))
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


class ProcessPage(QWidget):
    def __init__(self, theme: dict):
        super().__init__()
        self.theme = theme

        self.folder_path: Path | None = None
        self.video_paths: list[Path] = []
        self.pending_uploads: list[Path] = []

        self.jobs: dict[str, dict] = {}
        self.completed_jobs: dict[str, dict] = {}
        self.job_cards: dict[str, JobCard] = {}

        self.active_upload_worker = None
        self.download_worker = None

        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll_job_statuses)

        self.build_ui()

        self.queued_video_paths: set[str] = set()

    def build_ui(self):
        root = QHBoxLayout(self)
        root.setSpacing(18)

        # =========================
        # Left panel: input videos
        # =========================
        left_card = QFrame()
        left_card.setObjectName("Card")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(14)

        left_title = QLabel("Input Videos")
        left_title.setStyleSheet("font-size: 18px; font-weight: 800;")

        left_subtitle = QLabel("Choose a folder. Supported videos will appear below.")
        left_subtitle.setStyleSheet(f"color: {self.theme['muted']};")

        browse_row = QHBoxLayout()

        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet(f"color: {self.theme['muted']};")

        browse_btn = QPushButton("Browse Folder")
        browse_btn.clicked.connect(self.browse_folder)

        browse_row.addWidget(self.folder_label)
        browse_row.addStretch()
        browse_row.addWidget(browse_btn)

        self.select_all_checkbox = QCheckBox("Select all videos")
        self.select_all_checkbox.setChecked(True)
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all_videos)

        self.video_list = QListWidget()
        self.video_list.setMinimumHeight(360)

        action_row = QHBoxLayout()

        self.start_btn = QPushButton("Add to Queue")
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.clicked.connect(self.start_processing_selected)
        self.start_btn.setEnabled(False)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("DangerButton")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)

        action_row.addWidget(self.start_btn)
        action_row.addWidget(self.stop_btn)

        left_layout.addWidget(left_title)
        left_layout.addWidget(left_subtitle)
        left_layout.addLayout(browse_row)
        left_layout.addWidget(self.select_all_checkbox)
        left_layout.addWidget(self.video_list)
        left_layout.addLayout(action_row)

        # =========================
        # Right panel: job cards
        # =========================
        right_card = QFrame()
        right_card.setObjectName("Card")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(14)

        right_title = QLabel("Processing Queue")
        right_title.setStyleSheet("font-size: 18px; font-weight: 800;")

        self.queue_label = QLabel("No jobs submitted")
        self.queue_label.setStyleSheet("font-size: 16px; font-weight: 700;")

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()

        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.cards_scroll.setWidget(self.cards_container)

        right_layout.addWidget(right_title)
        right_layout.addWidget(self.queue_label)
        right_layout.addWidget(self.cards_scroll)

        root.addWidget(left_card, 5)
        root.addWidget(right_card, 5)

    def set_theme(self, theme: dict):
        self.theme = theme

    def log(self, message: str):
        print(message)

    # =========================
    # Folder + video selection
    # =========================
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder Containing Videos")

        if not folder:
            return

        self.folder_path = Path(folder)
        self.folder_label.setText(self.folder_path.name)

        videos = [
            p for p in sorted(self.folder_path.iterdir())
            if p.is_file() and p.suffix.lower() in VIDEO_EXTS
        ]

        self.video_paths = videos
        self.video_list.clear()

        for video in videos:
            item = QListWidgetItem(f"  {video.name}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, str(video))
            self.video_list.addItem(item)

        self.select_all_checkbox.setChecked(True)
        self.start_btn.setEnabled(bool(videos))

        self.log(f"Selected folder: {self.folder_path}")
        self.log(f"Found {len(videos)} supported video(s).")

    def toggle_select_all_videos(self):
        state = (
            Qt.CheckState.Checked
            if self.select_all_checkbox.isChecked()
            else Qt.CheckState.Unchecked
        )

        for i in range(self.video_list.count()):
            self.video_list.item(i).setCheckState(state)

    def get_checked_videos(self) -> list[Path]:
        checked = []

        for i in range(self.video_list.count()):
            item = self.video_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                checked.append(Path(item.data(Qt.ItemDataRole.UserRole)))

        return checked

    # =========================
    # Upload / queue handling
    # =========================
    def start_processing_selected(self):
        selected = [
            p for p in self.get_checked_videos()
            if str(p.resolve()) not in self.queued_video_paths
        ]

        if not selected:
            QMessageBox.warning(self, "No videos selected", "Please select at least one video.")
            return

        self.pending_uploads = selected.copy()
        for p in selected:
            self.queued_video_paths.add(str(p.resolve()))
        self.stop_btn.setEnabled(True)

        self.queue_label.setText(f"Submitting {len(self.pending_uploads)} video(s)...")
        self.log(f"Starting upload for {len(self.pending_uploads)} video(s).")

        self.upload_next_video()

    def upload_next_video(self):
        if not self.pending_uploads:
            self.log("All selected videos have been submitted to backend queue.")
            self.poll_timer.start(POLL_INTERVAL_MS)
            return

        next_video = self.pending_uploads.pop(0)
        self.queue_label.setText(f"Uploading: {next_video.name}")
        self.log(f"Uploading: {next_video.name}")

        self.active_upload_worker = UploadWorker(str(next_video))
        self.active_upload_worker.success.connect(self.on_upload_success)
        self.active_upload_worker.error.connect(self.on_upload_error)
        self.active_upload_worker.start()

    def on_upload_success(self, result: dict):
        job_id = result["job_id"]
        video_name = result.get("original_video_name", "unknown")

        self.jobs[job_id] = {
            "job_id": job_id,
            "video_name": video_name,
            "status": "queued",
        }

        self.add_or_update_job_card(job_id, video_name, "queued")
        self.log(f"Submitted {video_name}: {job_id}")

        self.upload_next_video()

    def on_upload_error(self, error: str):
        self.log(f"Upload failed: {error}")
        QMessageBox.critical(self, "Upload failed", error)

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    # =========================
    # Job card handling
    # =========================
    def add_or_update_job_card(self, job_id: str, video_name: str, status: str):
        if job_id in self.job_cards:
            self.job_cards[job_id].update_status(status)
            return

        index = len(self.job_cards) + 1

        card = JobCard(
            index=index,
            job_id=job_id,
            video_name=video_name,
            status=status,
            on_download=self.download_job_by_id,
        )

        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        self.job_cards[job_id] = card

    def poll_job_statuses(self):
        if not self.jobs:
            return

        active_count = 0
        completed_count = 0

        for job_id, job_info in list(self.jobs.items()):
            try:
                job = get_job_status(job_id)
                status = job.get("status")
                video_name = job.get("original_video_name", job_info["video_name"])

                self.jobs[job_id]["status"] = status
                self.jobs[job_id]["video_name"] = video_name

                self.add_or_update_job_card(job_id, video_name, status)

                if status == "completed":
                    self.completed_jobs[job_id] = job
                    completed_count += 1

                elif status in {"queued", "processing"}:
                    active_count += 1

            except Exception as e:
                self.log(f"Status check failed for {job_id}: {e}")

        total = len(self.jobs)
        self.queue_label.setText(f"{completed_count}/{total} completed")

        if active_count == 0:
            self.poll_timer.stop()
            # self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.log("All active jobs finished.")

    # =========================
    # Download
    # =========================
    def download_job_by_id(self, job_id: str):
        job = self.jobs.get(job_id)

        if not job or job.get("status") != "completed":
            QMessageBox.warning(self, "Job not ready", "This job is not completed yet.")
            return

        video_name = job.get("video_name", "processed_result")
        downloads_dir = Path.home() / "Downloads"
        default_name = str(downloads_dir / f"{Path(video_name).stem}.zip")

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Processed Result",
            default_name,
            "ZIP Files (*.zip)",
        )

        if not save_path:
            return

        self.log(f"Downloading {video_name} to {save_path}")

        self.download_worker = DownloadWorker(job_id, save_path)
        self.download_worker.success.connect(lambda path: self.on_download_success(job_id, path))
        self.download_worker.error.connect(self.on_download_error)
        self.download_worker.start()

    def on_download_success(self, job_id: str, save_path: str):
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = "downloaded"
            self.add_or_update_job_card(
                job_id,
                self.jobs[job_id]["video_name"],
                "downloaded",
            )

        self.completed_jobs.pop(job_id, None)

        self.log(f"Downloaded result: {save_path}")
        # QMessageBox.information(self, "Download complete", f"Saved to:\n{save_path}")

    def on_download_error(self, error: str):
        self.log(f"Download failed: {error}")
        QMessageBox.critical(self, "Download failed", error)

    # =========================
    # Stop local process
    # =========================
    def stop_processing(self):
        self.pending_uploads = []

        if self.active_upload_worker and self.active_upload_worker.isRunning():
            self.active_upload_worker.terminate()
            self.active_upload_worker.wait()

        self.poll_timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self.queue_label.setText("Processing stopped locally")
        self.log("Stopped local upload/status polling.")

        QMessageBox.information(
            self,
            "Stopped",
            "Stopped local uploads and status polling. Jobs already submitted to the backend may still continue processing.",
        )