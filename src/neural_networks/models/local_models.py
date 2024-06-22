import asyncio
import random
import statistics
import typing as T  # noqa
import os.path
from pathlib import Path

from nltk import word_tokenize

from src.neural_networks.base import NeuralNetworkBase
from src.neural_networks.criteria_json import CRITERIA_JSON, ACHIEVEMENT_JSON
from src.settings.static import NN_MODELS_DIR


class ScoreGeneratorNNModel(NeuralNetworkBase):
    def __init__(self, nn_models_dir: Path = NN_MODELS_DIR):
        self._nn_models_dir = nn_models_dir
        self.models = {}

    def load_models(self, model_list: T.List[str]) -> None:
        self.models = {model_name: self._load_model(os.path.join(self._nn_models_dir, model_name)) for model_name in model_list}

    def predict(self, text, model_name: str) -> float:
        return self._predict(text, self.models[model_name])

    def predict_all(self, text: str, model_names: T.List[str]):
        scores = {}
        for model_name in model_names:
            scores[model_name] = self.predict(text, model_name)
        scores['ta_Appropriate word count'] = self.ta_appropriate_word_count(text)
        return scores

    @staticmethod
    def format_predict_to_scores(predictions: T.Dict[str, float]) -> T.Tuple:
        gr_total_score = min(predictions['gr_Clear and correct grammar'], predictions['gr_Mix of complex & simple sentences'])
        ta_total_score = min(predictions['ta_Relevant & specific examples'], predictions['ta_Complete response'],
                             predictions['ta_Clear & comprehensive ideas'], predictions['ta_Appropriate word count'])
        lr_total_score = min(predictions['lr_Accurate spelling & word formation'], predictions['lr_Varied vocabulary'])
        cc_total_score = min(predictions['cc_Supported main points'], predictions['cc_Logical structure'],
                             predictions['cc_Introduction & conclusion present'], predictions['cc_Variety in linking words'],
                             predictions['cc_Accurate linking words'])
        overall_score = statistics.fmean([gr_total_score, ta_total_score, lr_total_score, cc_total_score])
        return overall_score, gr_total_score, ta_total_score, lr_total_score, cc_total_score

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
