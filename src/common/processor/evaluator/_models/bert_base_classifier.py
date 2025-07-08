import os

import onnx
import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer

target_labels = [
    "recipe",
    "cooking",
    "drink",
    "food",
]

other_labels = [
    "movie",
    "music",
    "sports",
    "news",
    "technology",
    "politics",
    "science",
    "health",
    "business",
    "entertainment",
    "lifestyle",
    "travel",
    "fashion",
    "art",
    "books",
    "tv",
    "game",
    "animal",
    "plant",
    "weather",
    "other",
]


class BertBaseClassifier:
    def __init__(self, model_name: str):
        model_path = os.getenv("MODEL_PATH", ".") + "/" + model_name
        self._validate_model(model_path)
        self.tokenizer = self._load_tokenizer(model_name)
        self.session = self._load_session(model_path)
    
    def evaluate(self, sequence: str) -> bool:
        pred = self._classify(sequence)
        print(pred)
        return pred["recipe"] > 0.5

    def _classify(self, sequence: str) -> dict[str, float]:
        inputs = self.tokenizer(sequence, return_tensors="np", padding="max_length", truncation=True, max_length=128)
        onnx_inputs = {
            "input_ids": inputs["input_ids"].astype(np.int64),
            "attention_mask": inputs["attention_mask"].astype(np.int64),
        }
        outputs = self.session.run(["logits"], onnx_inputs)
        return outputs[0][0]

    def _load_tokenizer(self, model_name: str):
        return AutoTokenizer.from_pretrained(model_name)

    def _load_session(self, model_name: str):
        return ort.InferenceSession(f"{model_name}.onnx")

    def _validate_model(self, model_name: str):
        if not os.path.exists(f"{model_name}.onnx"):
            raise FileNotFoundError(f"Model file {model_name}.onnx not found")
        
        onnx.checker.check_model(onnx.load(f"{model_name}.onnx"))