from pathlib import Path
import requests

from src.config import BACKEND_BASE_URL


def health_check() -> dict:
    response = requests.get(f"{BACKEND_BASE_URL}/health", timeout=10)
    response.raise_for_status()
    return response.json()


def upload_video(video_path: str) -> dict:
    path = Path(video_path)

    with path.open("rb") as f:
        files = {"file": (path.name, f, "application/octet-stream")}
        response = requests.post(
            f"{BACKEND_BASE_URL}/jobs/upload-video",
            files=files,
            timeout=120,
        )

    response.raise_for_status()
    return response.json()


def get_job_status(job_id: str) -> dict:
    response = requests.get(
        f"{BACKEND_BASE_URL}/jobs/{job_id}/status",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def download_result(job_id: str, save_path: str) -> None:
    response = requests.get(
        f"{BACKEND_BASE_URL}/jobs/{job_id}/download",
        stream=True,
        timeout=120,
    )
    response.raise_for_status()

    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)