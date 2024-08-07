import asyncio
import math
import os.path
import random
import typing as T  # noqa
from os.path import join
from pathlib import Path

import pandas as pd

from src.neural_network.nn_models.accurate_spelling_and_word_formation import AccurateSpellingAndWordFormation
from src.neural_network.nn_models.fluency_coherence import FluencyCoherence
from src.neural_network.nn_models.gr_clear_and_correct_grammar import GRClearAndCorrectGrammar
from src.neural_network.nn_models.gr_variety_of_grammar_used import GrVarietyOfGrammarUsed
from src.neural_network.nn_models.lr_idiomatic_vocabulary_or_expressions import LrIdiomaticVocabulary
from src.neural_network.nn_models.gr_mix_of_complex_and_simple_sentences import MixOfComplexAndSimpleSentences
from src.neural_network.nn_models.lr_paraphrases_effectively import LrParaphraseEffectively
from src.neural_network.nn_models.ta_appropriate_word_count import TAAppropriateWordCount
from src.neural_network.nn_models.lr_varied_vocabulary import LRVariedVocabulary
from src.neural_network.nn_models.pr_pronunciation import PrPronunciation
from src.neural_network.nn_models.utils.timeit import timeit
from src.postgres.enums import CompetenceEnum
from src.repos.factories.user_question_metric import TgUserQuestionMetricRepo
from src.settings import NNModelsSettings
from src.settings.static import NN_MODELS_DIR, OTHER_DATA_DIR


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
    LrParaphraseEffectively,
):
    def __init__(
        self,
        settings: NNModelsSettings,
        uq_metric_repo: TgUserQuestionMetricRepo,
        nn_models_dir: Path = NN_MODELS_DIR
    ):
        self._nn_models_dir = nn_models_dir
        super().__init__(settings, uq_metric_repo)
        self.advices_xlsx = join(nn_models_dir, 'advices.xlsx')
        self.lookup = None
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
                'lr_paraphrase_effectively': self.lr_paraphrase_effectively,
                'gr_Complexity of the verb phrase': self.gr_variety_of_grammar_used,
                'gr_Flexible Use of Complex Structures': self.gr_mix_of_complex_and_simple_sentences,
                'lr_Variety of words used': self.lr_varied_vocabulary,
                'lr_Idiomatic Vocabulary or Expressions': self.lr_idiomatic_vocabulary_or_expressions,
                'fc_Speech rate': self.fc_speech_speed,
                'fc_Minimal Self-Correction': self.fc_self_corrections,
                'fc_Relevance of spoken sentences to the general purpose of a turn': self.fc_topics_developed_logically,
                'fc_Range of Linking Words and Discourse Markers': self.range_of_linking_words_and_discourse_markers,
                'pr_Pronunciation': self.get_pronunciation_score,
            }
        }

    @timeit
    def load(self):
        if self.lookup is None:
            loaded_xlsx = ScoreGeneratorNNModel.xlsx_to_dict()
            self.lookup = ScoreGeneratorNNModel.create_lookup(loaded_xlsx)
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
        score = math.floor(average * 2) / 2

        uq_id: T.Optional[int] = kwargs.get('uq_id', None)
        if uq_id is not None:
            asyncio.create_task(self.save_metric_data(uq_id, 'fc_c_ross', score))

        return math.floor(average * 2) / 2

    def range_of_linking_words_and_discourse_markers(self, text: str, **kwargs) -> float:
        models = ['cc_Variety in linking words', 'cc_Accurate linking words']
        scores = [self.predict(text, model_name) for model_name in models]
        average = sum(scores) / len(scores)
        score = math.floor(average * 2) / 2
        return score

    def select_random_advice(self, results, competence: CompetenceEnum):
        selected_advice = {}
        for result_key, score in results.items():
            subcategory = result_key[3:]
            subcategory_lower = subcategory.lower()
            record = self.find_random_lookup_record(competence.name.lower(), subcategory_lower, score)
            category = record['Top criteria']
            if category not in selected_advice:
                selected_advice[category] = {}
            selected_advice[category][subcategory] = record['Achivement text']
        return selected_advice

    def find_random_lookup_record(self, test_type: str, criteria, score):
        type_ = 'Achievement' if score >= 7 else 'Suggestion'
        key = (test_type, type_, criteria)
        records = self.lookup.get(key, [])
        if records:
            return random.choice(records)
        return None

    @staticmethod
    def xlsx_to_dict(advices_xlsx=os.path.join(OTHER_DATA_DIR, 'advices.xlsx')) -> T.List[T.Dict[str, T.Any]]:
        xls = pd.ExcelFile(advices_xlsx)
        data_dict = {}
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name)
            data_dict[sheet_name] = df.to_dict(orient='records')
        return data_dict['Sheet1']

    @staticmethod
    def create_lookup(data):
        lookup = {}
        for record in data:
            record['Test type'] = record['Test type'].lower()
            record['Criteria'] = record['Criteria'].lower()
            key = (record['Test type'], record['Type'], record['Criteria'])
            if key not in lookup:
                lookup[key] = []
            lookup[key].append(record)
        return lookup
