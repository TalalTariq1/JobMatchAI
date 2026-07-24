import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase using either:
# 1) the JSON service account stored locally at `firebase-key.json` (existing behavior), or
# 2) the `FIREBASE_SERVICE_ACCOUNT_JSON` environment variable (recommended for Render).
sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
cred = None
if sa_json:
    try:
        sa_info = json.loads(sa_json)
    except Exception:
        # Support base64-encoded JSON as well
        import base64

        sa_info = json.loads(base64.b64decode(sa_json).decode())

    cred = credentials.Certificate(sa_info)
else:
    # Fallback to local file for developer convenience
    cred = credentials.Certificate("firebase-key.json")

firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()


if __name__ == "__main__":
    print("Firebase app initialized:", firebase_admin.get_app().name)