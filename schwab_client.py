import os
import requests


CLIENT_ID = os.environ.get("SCHWAB_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SCHWAB_CLIENT_SECRET")

CALLBACK_URL = "https://127.0.0.1:5556"


def credentials_available():
    return bool(CLIENT_ID and CLIENT_SECRET)


def get_config():
    return {
        "client_id_loaded": bool(CLIENT_ID),
        "client_secret_loaded": bool(CLIENT_SECRET),
        "callback_url": CALLBACK_URL,
    }


if __name__ == "__main__":
    print(get_config())
