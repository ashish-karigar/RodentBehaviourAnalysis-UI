from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
)


class JobCard(QFrame):
    def __init__(self, index: int, job_id: str, video_name: str, status: str, on_download, theme: dict):
        super().__init__()

        self.index = index
        self.job_id = job_id
        self.theme = theme
        self.video_name = video_name
        self.status = status
        self.on_download = on_download

        self.setObjectName("JobCard")
        self.setMinimumHeight(92)
        self.setMaximumHeight(105)

        self.build_ui()
        self.update_status(status)

    def build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(14)

        self.number_label = QLabel(f"{self.index:02d}")
        self.number_label.setFixedWidth(52)
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number_color = "#B7F000" if self.theme["bg"] == "#0F172A" else "#FE5E00"

        self.number_label.setStyleSheet(
            f"""
            font-family: Monaco, Menlo, Consolas, monospace;
            font-size: 34px;
            font-weight: 900;
            color: {number_color};
            """
        )

        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)

        self.name_label = QLabel(f"Name: {self.video_name}")
        self.name_label.setWordWrap(False)
        self.name_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.name_label.setStyleSheet("font-weight: 700;")

        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-weight: 600;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setRange(0, 100)

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.status_label)
        info_layout.addWidget(self.progress_bar)

        self.download_btn = QPushButton("Download")
        self.download_btn.setFixedWidth(110)
        self.download_btn.clicked.connect(lambda: self.on_download(self.job_id))

        root.addWidget(self.number_label)
        root.addLayout(info_layout, 1)
        root.addWidget(self.download_btn)

    def update_status(self, status: str):
        self.status = status
        clean_status = status.title()
        self.status_label.setText(f"Status: {clean_status}")

        if status == "queued":
            self.progress_bar.setValue(10)
            self.download_btn.setEnabled(False)
            self.download_btn.setObjectName("MutedButton")
            self.download_btn.setText("Queued")

        elif status == "processing":
            self.progress_bar.setValue(55)
            self.download_btn.setEnabled(False)
            self.download_btn.setObjectName("WarningButton")
            self.download_btn.setText("Processing")

        elif status == "completed":
            self.progress_bar.setValue(100)
            self.download_btn.setEnabled(True)
            self.download_btn.setObjectName("PrimaryButton")
            self.download_btn.setText("Download")

        elif status == "downloaded":
            self.progress_bar.setValue(100)
            self.download_btn.setEnabled(False)
            self.download_btn.setObjectName("DownloadedButton")
            self.download_btn.setText("Downloaded")

        elif status == "expired":
            self.progress_bar.setValue(100)
            self.download_btn.setEnabled(False)
            self.download_btn.setObjectName("MutedButton")
            self.download_btn.setText("Expired")

        elif status == "failed":
            self.progress_bar.setValue(100)
            self.download_btn.setEnabled(False)
            self.download_btn.setObjectName("DangerButton")
            self.download_btn.setText("Failed")

        else:
            self.progress_bar.setValue(0)
            self.download_btn.setEnabled(False)
            self.download_btn.setObjectName("MutedButton")
            self.download_btn.setText("Unavailable")

        self.download_btn.style().unpolish(self.download_btn)
        self.download_btn.style().polish(self.download_btn)