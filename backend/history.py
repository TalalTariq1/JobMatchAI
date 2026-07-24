from datetime import datetime, timezone
from firebase_client import db


def save_application(user_id, application_data):
    """
    Saves a completed match result as a new application record under this
    user. This is the moment the 'applications' collection and its fields
    actually get created in Firestore — there's no separate schema step,
    this dictionary IS the schema.
    """
    doc_ref = (
        db.collection("users")
        .document(user_id)
        .collection("applications")
        .document()
    )
    application_data["createdAt"] = datetime.now(timezone.utc)
    doc_ref.set(application_data)
    return doc_ref.id


def save_sent_email(user_id, application_id, email_data):
    """
    Saves a sent email record, linked back to the application it belongs to
    via applicationId, so the history view can show which email was sent
    for which job.
    """
    doc_ref = (
        db.collection("users")
        .document(user_id)
        .collection("emails")
        .document()
    )
    email_data["applicationId"] = application_id
    email_data["sentAt"] = datetime.now(timezone.utc)
    doc_ref.set(email_data)
    return doc_ref.id


def get_user_history(user_id):
    """
    Returns every past application and every sent email for this user,
    so the frontend sidebar can display a full history.
    """
    applications_ref = (
        db.collection("users").document(user_id).collection("applications")
    )
    emails_ref = db.collection("users").document(user_id).collection("emails")

    applications = [
        {**doc.to_dict(), "id": doc.id} for doc in applications_ref.stream()
    ]
    emails = [{**doc.to_dict(), "id": doc.id} for doc in emails_ref.stream()]

    return {"applications": applications, "emails": emails}


if __name__ == "__main__":
    test_user_id = "test_user_123"

    print("[1/3] Saving a test application...")
    app_id = save_application(test_user_id, {
        "jobTitle": "Web Developer",
        "company": "Test Company",
        "matchScore": 56.2,
        "matchedSkills": ["Html5", "Api Integration"],
        "missingSkills": ["Php", "Wordpress"],
    })
    print(f"Saved application with id: {app_id}")

    print("\n[2/3] Saving a test sent email linked to that application...")
    email_id = save_sent_email(test_user_id, app_id, {
        "subject": "Test Subject Line",
        "body": "Test email body content.",
        "status": "sent",
    })
    print(f"Saved email with id: {email_id}")

    print("\n[3/3] Reading back full history for this user...")
    history = get_user_history(test_user_id)
    print(history)