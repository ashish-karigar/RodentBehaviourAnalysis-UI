from pathlib import Path
import requests

from src.config import BACKEND_BASE_URL


def health_check() -> dict:
    response = requests.get(f"{BACKEND_BASE_URL}/health", timeout=10)
    response.raise_for_status()
    return response.json()


def upload_video(video_path: str, id_token: str) -> dict:
    path = Path(video_path)

    with path.open("rb") as f:
        files = {"file": (path.name, f, "application/octet-stream")}
        response = requests.post(
            f"{BACKEND_BASE_URL}/jobs/upload-video",
            headers=auth_headers(id_token),
            files=files,
            timeout=120,
        )

    response.raise_for_status()
    return response.json()


def get_job_status(job_id: str, id_token: str) -> dict:
    response = requests.get(
        f"{BACKEND_BASE_URL}/jobs/{job_id}/status",
        headers=auth_headers(id_token),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def download_result(job_id: str, save_path: str, id_token: str) -> None:
    response = requests.get(
        f"{BACKEND_BASE_URL}/jobs/{job_id}/download",
        headers=auth_headers(id_token),
        stream=True,
        timeout=120,
    )
    response.raise_for_status()

    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)


def mark_password_change_complete(id_token: str) -> dict:
    response = requests.post(
        f"{BACKEND_BASE_URL}/jobs/auth/password-change-complete",
        headers={
            "Authorization": f"Bearer {id_token}",
        },
        timeout=20,
    )

    response.raise_for_status()
    return response.json()


def auth_headers(id_token: str) -> dict:
    return {
        "Authorization": f"Bearer {id_token}",
    }