import os
import time
from typing import Any

from amplitude import Amplitude, BaseEvent


class Logger:
    amplitude: Amplitude = None
    
    @staticmethod
    def set_config(config: dict[str, Any]):
        Logger.amplitude = Amplitude(os.getenv("AMPLITUDE_API_KEY", ""))
        Logger.amplitude.config = config

    @staticmethod
    def log_event(func_name: str, targets: dict[str, Any]):
        targets = {k: str(v) for k, v in targets.items()}
        Logger.amplitude.track(BaseEvent(
            event_type="Processor/"+func_name,
            time=int(time.time()*1000),
            user_id=Logger.amplitude.config["user_id"],
            event_properties={
                **Logger.amplitude.config,
                **targets,
            },
        ))


if __name__ == "__main__":
    Logger.set_config({
        "user_id": "userid_123",
        "user_name": "John Doe",
    })

    Logger.log_event("test", {
        "test": "test",
    })
    
    Logger.amplitude.flush()
    Logger.amplitude.shutdown()