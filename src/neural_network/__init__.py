import math
import random
import typing as T  # noqa
from os.path import join
from pathlib import Path

from data.other.criteria_json import CRITERIA_JSON_WRITING, ACHIEVEMENT_JSON_WRITING, ACHIEVEMENT_JSON_SPEAKING, \
    CRITERIA_JSON_SPEAKING
from src.neural_network.nn_models.accurate_spelling_and_word_formation import AccurateSpellingAndWordFormation
from src.neural_network.nn_models.fluency_coherence import FluencyCoherence
from src.neural_network.nn_models.gr_clear_and_correct_grammar import GRClearAndCorrectGrammar
from src.neural_network.nn_models.gr_variety_of_grammar_used import GrVarietyOfGrammarUsed
from src.neural_network.nn_models.lr_idiomatic_vocabulary_or_expressions import LrIdiomaticVocabulary
from src.neural_network.nn_models.gr_mix_of_complex_and_simple_sentences import MixOfComplexAndSimpleSentences
from src.neural_network.nn_models.ta_appropriate_word_count import TAAppropriateWordCount
from src.neural_network.nn_models.lr_varied_vocabulary import LRVariedVocabulary
from src.neural_network.nn_models.pr_pronunciation import PrPronunciation
from src.neural_network.nn_models.utils.timeit import timeit
from src.postgres.enums import CompetenceEnum
from src.settings import NNModelsSettings
from src.settings.static import NN_MODELS_DIR


class ScoreGeneratorNNModel(
    GRClearAndCorrectGrammar,
    MixOfComplexAndSimpleSentences,
    LRVariedVocabulary,
    AccurateSpellingAndWordFormation,
    PrPronunciation,
    TAAppropriateWordCount,
    LrIdiomaticVocabulary,
    FluencyCoherence,
    GrVarietyOfGrammarUsed,
):
    def __init__(self, settings: NNModelsSettings, nn_models_dir: Path = NN_MODELS_DIR):
        self._nn_models_dir = nn_models_dir
        super().__init__(settings)
        self.models = {}
        self.func_models: T.Dict[CompetenceEnum, T.Dict[str, T.Callable[[str], T.Any]]] = {
            CompetenceEnum.writing: {
                'clear_grammar_result': self.gr_clear_and_correct_grammar,
                'ta_Appropriate word count': self.ta_appropriate_word_count,
                'gr_Mix of complex & simple sentences': self.gr_mix_of_complex_and_simple_sentences,
                'lr_Varied vocabulary': self.lr_varied_vocabulary,
                'lr_Accurate spelling & word formation': self.lr_accurate_spelling_and_word_formation,
            },
            CompetenceEnum.speaking: {
                'clear_grammar_result': self.gr_clear_and_correct_grammar,
                'gr_Wide Range of Grammar Used': self.gr_variety_of_grammar_used,
                'gr_Flexible Use of Complex Structures': self.gr_mix_of_complex_and_simple_sentences,
                'lr_Wide Range of Vocabulary': self.lr_varied_vocabulary,
                'lr_Idiomatic Vocabulary or Expressions': self.lr_idiomatic_vocabulary_or_expressions,
                'fc_Minimal Hesitation': self.fc_minimal_hesitations,
                'fc_Minimal Self-Correction': self.fc_self_corrections,
                'fc_Topics Developed Logically': self.fc_topics_developed_logically,
                'fc_Range of Linking Words and Discourse Markers': self.range_of_linking_words_and_discourse_markers,
                'pr_Pronunciation': self.get_pronunciation_score,
            }
        }

    @timeit
    def load(self):
        super().load()

    def load_models(self, model_list: T.List[str]) -> None:
        self.models = {model_name: self._load_model(join(self._nn_models_dir, model_name)) for model_name in model_list}
        self.load()

    def predict(self, text, model_name: str, **kwargs) -> T.Any:
        competence = kwargs.get('competence', CompetenceEnum.writing)
        if model_name in self.func_models[competence]:
            return self.func_models[competence][model_name](text=text, **kwargs)  # noqa
        return self._predict(text=text, model_info=self.models[model_name])

    def predict_all(self, text: str, model_names: T.List[str], **kwargs):
        scores = {}
        for model_name in model_names:
            scores[model_name] = self.predict(text, model_name, **kwargs)
        return scores

    def fc_topics_developed_logically(self, text: str, **kwargs) -> float:
        models = ['ta_Relevant & specific examples', 'ta_Complete response', 'ta_Clear & comprehensive ideas',
                  'cc_Supported main points', 'cc_Logical structure']
        scores = [self.predict(text, model_name) for model_name in models]
        average = sum(scores) / len(scores)
        return math.floor(average * 2) / 2

    def range_of_linking_words_and_discourse_markers(self, text: str, **kwargs) -> float:
        models = ['cc_Variety in linking words', 'cc_Accurate linking words']
        scores = [self.predict(text, model_name) for model_name in models]
        average = sum(scores) / len(scores)
        return math.floor(average * 2) / 2

    @staticmethod
    def select_random_advice(results, competence: CompetenceEnum):
        selected_advice = {}
        if competence == CompetenceEnum.writing:
            achievement_json = ACHIEVEMENT_JSON_WRITING
            criteria_json = CRITERIA_JSON_WRITING
        elif competence == CompetenceEnum.speaking:
            achievement_json = ACHIEVEMENT_JSON_SPEAKING
            criteria_json = CRITERIA_JSON_SPEAKING
        else:
            return
        for result_key, score in results.items():
            subcategory = result_key[3:]
            for category, subcategories in achievement_json.items():
                if subcategory in subcategories:
                    if score >= 7:
                        advice = random.choice(achievement_json[category][subcategory])
                    else:
                        advice = random.choice(criteria_json[category][subcategory])
                    if category not in selected_advice:
                        selected_advice[category] = {}
                    selected_advice[category][subcategory] = advice
                    break
        return selected_advice
