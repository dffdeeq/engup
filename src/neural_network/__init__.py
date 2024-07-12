import random
import typing as T  # noqa
from os.path import join

from data.other.criteria_json import CRITERIA_JSON, ACHIEVEMENT_JSON
from src.neural_network.nn_models.accurate_spelling_and_word_formation import AccurateSpellingAndWordFormation
from src.neural_network.nn_models.gr_clear_and_correct_grammar import GRClearAndCorrectGrammar
from src.neural_network.nn_models.mix_of_complex_and_simple_sentences import MixOfComplexAndSimpleSentences
from src.neural_network.nn_models.ta_appropriate_word_count import TAAppropriateWordCount
from src.neural_network.nn_models.lr_varied_vocabulary import LRVariedVocabulary
from src.neural_network.nn_models.pr_pronunciation import PrPronunciation
from src.settings import NNModelsSettings


class ScoreGeneratorNNModel(
    GRClearAndCorrectGrammar,
    MixOfComplexAndSimpleSentences,
    LRVariedVocabulary,
    AccurateSpellingAndWordFormation,
    PrPronunciation,
    TAAppropriateWordCount,
):
    def __init__(self, settings: NNModelsSettings):
        super().__init__(settings)
        self.models = {}
        self.func_models: T.Dict[str, T.Callable[[str], T.Any]] = {
            'clear_grammar_result': self.gr_clear_and_correct_grammar,
            'ta_Appropriate word count': self.ta_appropriate_word_count,
            'gr_Mix of complex & simple sentences': self.gr_mix_of_complex_and_simple_sentences,
            'lr_Varied vocabulary': self.lr_varied_vocabulary,
            'lr_Accurate spelling & word formation': self.lr_accurate_spelling_and_word_formation,
        }

    def load(self):
        super().load()

    def load_models(self, model_list: T.List[str]) -> None:
        self.models = {model_name: self._load_model(join(self._nn_models_dir, model_name)) for model_name in model_list}
        self.load()

    def predict(self, text, model_name: str) -> T.Any:
        if model_name in self.func_models:
            return self.func_models[model_name](text)
        return self._predict(text, self.models[model_name])

    def predict_all(self, text: str, model_names: T.List[str]):
        scores = {}
        for model_name in model_names:
            scores[model_name] = self.predict(text, model_name)
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
