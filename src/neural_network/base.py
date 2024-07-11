import typing as T  # noqa
import json
import os
import torch

from pathlib import Path
from transformers import BertForSequenceClassification, BertTokenizer

from src.settings import NNModelsSettings


class NeuralNetworkBase:
    def __init__(self, settings: NNModelsSettings) -> None:
        self.settings = settings

    def load(self):
        pass

    def _load_model(self, model_path: T.Union[str, Path]) -> T.Dict[str, T.Any]:
        model = BertForSequenceClassification.from_pretrained(os.path.join(model_path, 'model'))
        tokenizer = BertTokenizer.from_pretrained(os.path.join(model_path, 'tokenizer'))
        label_to_int = self.load_json(os.path.join(model_path, 'label_to_int.json'))
        int_to_label = self.load_json(os.path.join(model_path, 'int_to_label.json'))
        return {
            "model": model,
            "tokenizer": tokenizer,
            "label_to_int": label_to_int,
            "int_to_label": int_to_label,
        }

    @staticmethod
    def load_json(file_path: str) -> T.Dict:
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def _predict(text: str, model_info: T.Dict[str, T.Any]) -> float:
        device = torch.device('cpu')
        model, tokenizer = model_info['model'], model_info['tokenizer']
        inputs = tokenizer(text, truncation=True, padding=True, return_tensors='pt').to(device)
        model.eval().to(device)
        with torch.no_grad():
            prediction = torch.argmax(model(**inputs).logits, dim=-1).item()
        return float(model_info['int_to_label'][str(prediction)])
