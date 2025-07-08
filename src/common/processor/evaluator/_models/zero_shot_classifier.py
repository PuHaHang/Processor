import os
from typing import Any
import numpy as np

import onnx
import onnxruntime as ort
from transformers import AutoTokenizer


class ZeroShotClassifier:
    max_length: int = 128
    label_names = ["entailment", "neutral", "contradiction"]


    def __init__(self, model_name: str):
        model_path = os.getenv("MODEL_PATH", ".") + "/" + model_name
        self._validate_model(model_path)
        self.tokenizer = self._load_tokenizer(model_name)
        self.session = self._load_session(model_path)

    def evaluate(self, sequence: str|dict[str, Any]) -> bool:
        if not sequence:
            raise ValueError("Sequence is empty")

        if isinstance(sequence, dict):
            for key, value in sequence.items():
                sequence[key] = self._classify(str(value))
            pred_dict = {
                "entailment": 0.0,
                "neutral": 0.0,
                "contradiction": 0.0,
            }
            for key, value in sequence.items():
                pred_dict["entailment"] += value["entailment"]
                pred_dict["neutral"] += value["neutral"]
                pred_dict["contradiction"] += value["contradiction"]
            pred_dict["entailment"] /= (len(sequence) if len(sequence) > 0 else 1)
            pred_dict["neutral"] /= (len(sequence) if len(sequence) > 0 else 1)
            pred_dict["contradiction"] /= (len(sequence) if len(sequence) > 0 else 1)
        else:
            pred_dict = self._classify(sequence)
        
        return pred_dict["entailment"] > pred_dict["neutral"] + pred_dict["contradiction"]

    def _classify(self, sequence: str) -> dict[str, float]:
        hypothesis = "이 문장은 레시피에 관한 것이다."
        encoded = self.tokenizer(sequence, hypothesis, return_tensors="np", truncation=True, padding="max_length", max_length=128)

        onnx_inputs = {
            "input_ids": encoded["input_ids"].astype(np.int64),
            "attention_mask": encoded["attention_mask"].astype(np.int64),
        }

        outputs = self.session.run(["logits"], onnx_inputs)
        probs = np.exp(outputs[0][0]) / np.sum(np.exp(outputs[0][0]))  # softmax
        pred_dict = {name: round(float(prob) * 100, 2) for name, prob in zip(self.label_names, probs)}
        return pred_dict

    def _load_tokenizer(self, model_name: str):
        return AutoTokenizer.from_pretrained(model_name)

    def _load_session(self, model_name: str):
        return ort.InferenceSession(f"{model_name}.onnx")

    def _validate_model(self, model_name: str):
        if not os.path.exists(f"{model_name}.onnx"):
            raise FileNotFoundError(f"Model file {model_name}.onnx not found")
        
        onnx.checker.check_model(onnx.load(f"{model_name}.onnx"))