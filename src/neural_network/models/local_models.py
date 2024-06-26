import os
import random
import typing as T  # noqa
from os.path import join
from pathlib import Path

import nltk
from nltk import word_tokenize

from src.neural_network.base import NeuralNetworkBase
from src.neural_network.criteria_json import CRITERIA_JSON, ACHIEVEMENT_JSON
from src.settings.static import NN_MODELS_DIR


class ScoreGeneratorNNModel(NeuralNetworkBase):
    def __init__(self, nn_models_dir: Path = NN_MODELS_DIR):
        self._nn_models_dir = nn_models_dir
        self.models = {}

    def load_models(self, model_list: T.List[str]) -> None:
        self.models = {model_name: self._load_model(join(self._nn_models_dir, model_name)) for model_name in model_list}
        nltk_dir = join(self._nn_models_dir, 'nltk')
        if not os.path.exists(nltk_dir):
            nltk.download('punkt', download_dir=nltk_dir)
        nltk.data.path.append(nltk_dir)

    def predict(self, text, model_name: str) -> float:
        return self._predict(text, self.models[model_name])

    def predict_all(self, text: str, model_names: T.List[str]):
        scores = {}
        for model_name in model_names:
            scores[model_name] = self.predict(text, model_name)
        scores['ta_Appropriate word count'] = self.ta_appropriate_word_count(text)
        return scores

    @staticmethod
    def select_random_advice(results):
        selected_advice = {}
        for result_key, score in results.items():
            subcategory = result_key[3:]
            for category, subcategories in ACHIEVEMENT_JSON.items():
                if subcategory in subcategories:
                    if score >= 7:
                        advice = random.choice(ACHIEVEMENT_JSON[category][subcategory])
                    else:
                        advice = random.choice(CRITERIA_JSON[category][subcategory])
                    if category not in selected_advice:
                        selected_advice[category] = {}
                    selected_advice[category][subcategory] = advice
                    break
        return selected_advice

    @staticmethod
    def ta_appropriate_word_count(text: str) -> float:
        words = word_tokenize(text)
        words_count = len([w for w in words if w.isalpha()])
        return 9.0 if words_count >= 250 else 4.0
