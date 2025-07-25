import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("src/resources/keys/recipe-it-3a7e1-firebase-adminsdk-fbsvc-ca60eb0c11.json")
firebase_admin.initialize_app(cred)

def send_notification(token: str, title: str, body: str, image_url: str):
    registration_token = token

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=image_url,
        ),
        token=registration_token
    )

    response = messaging.send(message)
    return response
