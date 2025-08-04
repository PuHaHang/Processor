import firebase_admin
import logfire
from firebase_admin import credentials, messaging

cred = credentials.Certificate("src/resources/keys/recipe-it-fcm-admin.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

def send_notification(token: str, title: str, body: str, image_url: str):
    registration_token = token

    logfire.info('FCM 알림 전송 시작 {title}, token: {token}', title=title, token=token[:10] + '...')

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=image_url,
        ),
        token=registration_token
    )

    try:
        response = messaging.send(message)
        logfire.info('FCM 알림 전송 성공 {title}, response: {response}', title=title, response=response)
        return response
    except Exception as e:
        logfire.error('FCM 알림 전송 실패 {title}, error: {error}', title=title, error=str(e))
        raise
