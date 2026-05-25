import requests

from src.config import FIREBASE_PROJECT_ID


class FirestoreUserError(Exception):
    pass


def _firestore_user_url(local_id: str) -> str:
    return (
        f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}"
        f"/databases/(default)/documents/users/{local_id}"
    )


def get_user_profile(local_id: str, id_token: str) -> dict:
    url = _firestore_user_url(local_id)

    print("Firestore project:", FIREBASE_PROJECT_ID)
    print("Looking for user profile:", local_id)
    print("Firestore URL:", url)

    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {id_token}"},
        timeout=20,
    )

    if response.status_code != 200:
        print("Firestore status:", response.status_code)
        print("Firestore response:", response.text)

        raise FirestoreUserError(
            f"Could not load user profile. Firestore status: {response.status_code}"
        )

    data = response.json()
    fields = data.get("fields", {})

    return {
        "email": fields.get("email", {}).get("stringValue"),
        "must_change_password": fields.get("mustChangePassword", {}).get("booleanValue", False),
    }


def set_must_change_password(local_id: str, id_token: str, value: bool):
    url = _firestore_user_url(local_id)

    payload = {
        "fields": {
            "mustChangePassword": {"booleanValue": value}
        }
    }

    response = requests.patch(
        url,
        headers={"Authorization": f"Bearer {id_token}"},
        json=payload,
        timeout=20,
    )

    if response.status_code not in {200, 201}:
        raise FirestoreUserError("Could not update user profile.")

    return response.json()