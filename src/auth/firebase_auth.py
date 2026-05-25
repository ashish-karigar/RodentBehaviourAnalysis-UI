import requests

from src.config import FIREBASE_WEB_API_KEY


class FirebaseAuthError(Exception):
    pass


def sign_in_with_email_password(email: str, password: str) -> dict:
    if FIREBASE_WEB_API_KEY == "PASTE_YOUR_FIREBASE_WEB_API_KEY_HERE":
        raise FirebaseAuthError("Firebase API key is missing. Add it in src/config.py.")

    url = (
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    )

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }

    response = requests.post(url, json=payload, timeout=20)
    data = response.json()

    if response.status_code != 200:
        message = data.get("error", {}).get("message", "Firebase login failed.")
        raise FirebaseAuthError(message)

    return {
        "email": data.get("email"),
        "local_id": data.get("localId"),
        "id_token": data.get("idToken"),
        "refresh_token": data.get("refreshToken"),
        "expires_in": data.get("expiresIn"),
    }

def send_password_reset_email(email: str) -> dict:
    if not FIREBASE_WEB_API_KEY:
        raise FirebaseAuthError("Firebase API key is missing.")

    url = (
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
    )

    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email,
    }

    response = requests.post(url, json=payload, timeout=20)
    data = response.json()

    if response.status_code != 200:
        message = data.get("error", {}).get("message", "Password reset failed.")
        raise FirebaseAuthError(message)

    return data

def update_password(id_token: str, new_password: str) -> dict:
    if not FIREBASE_WEB_API_KEY:
        raise FirebaseAuthError("Firebase API key is missing.")

    url = (
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:update?key={FIREBASE_WEB_API_KEY}"
    )

    payload = {
        "idToken": id_token,
        "password": new_password,
        "returnSecureToken": True,
    }

    response = requests.post(url, json=payload, timeout=20)
    data = response.json()

    if response.status_code != 200:
        message = data.get("error", {}).get("message", "Password update failed.")
        raise FirebaseAuthError(message)

    return {
        "email": data.get("email"),
        "local_id": data.get("localId"),
        "id_token": data.get("idToken"),
        "refresh_token": data.get("refreshToken"),
        "expires_in": data.get("expiresIn"),
    }