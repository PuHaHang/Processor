import os

import logfire

from src.subscriber.subscriber import poll_messages

api_key = os.getenv("LOGFIRE_TOKEN", "")
print(repr(api_key))
if type(api_key) == bytes:
    api_key = api_key.decode("utf-8")
os.environ["LOGFIRE_TOKEN"] = api_key
logfire.configure()

if __name__ == "__main__":
    logfire.info('메인 애플리케이션 시작')
    poll_messages()
