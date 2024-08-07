from fuzzywuzzy import process, fuzz

from data.other.idioms import IDIOMS_LIST
from src.neural_network.base import NeuralNetworkBase
from src.neural_network.nn_models.utils.timeit import timeit
from src.repos.factories.user_question_metric import TgUserQuestionMetricRepo
from src.settings import NNModelsSettings


class LrIdiomaticVocabulary(NeuralNetworkBase):
    def __init__(self, settings: NNModelsSettings, uq_metric_repo: TgUserQuestionMetricRepo):
        super().__init__(settings, uq_metric_repo)
        self.idioms = None

    def load(self):
        if not self.idioms:
            self.idioms = IDIOMS_LIST
        super().load()

    @timeit
    def lr_idiomatic_vocabulary_or_expressions(self, text, threshold=65, **kwargs):
        found_idioms = []
        for idiom in self.idioms:
            if process.extractOne(idiom, [text], scorer=fuzz.partial_ratio)[1] >= threshold:
                found_idioms.append(idiom)
        found_idioms = list(set(found_idioms))

        return 9.0 if len(found_idioms) >= 2 else 6.0
