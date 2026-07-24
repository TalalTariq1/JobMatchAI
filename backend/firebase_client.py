import firebase_admin
from firebase_admin import credentials, firestore

# This is the one-time setup step: it reads your private key file and uses it
# to prove to Google's servers that these requests are really coming from your
# backend, not some random program pretending to be you.
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

# This gives you an actual object you can use to read/write data —
# think of `db` as your remote control for talking to Firestore from now on.
db = firestore.client()


if __name__ == "__main__":
    print("Firebase app initialized:", firebase_admin.get_app().name)