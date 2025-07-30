import os

import logfire

from src.subscriber.subscriber import poll_messages


logfire.configure(token=os.getenv("LOGFIRE_TOKEN", ""))

if __name__ == "__main__":
    logfire.info('메인 애플리케이션 시작')
    poll_messages()
