import os

import nltk
from nltk import word_tokenize

from src.neural_network.base import NeuralNetworkBase
from src.neural_network.nn_models.utils.timeit import timeit
from src.settings import NNModelsSettings


class TAAppropriateWordCount(NeuralNetworkBase):
    def __init__(self, settings: NNModelsSettings):
        self.nltk_dir = os.path.join(self._nn_models_dir, 'nltk')  # noqa
        super().__init__(settings)

    def load(self):
        if not os.path.exists(self.nltk_dir):
            nltk.download('punkt', download_dir=self.nltk_dir)
        nltk.data.path.append(self.nltk_dir)
        super().load()

    @staticmethod
    @timeit
    def ta_appropriate_word_count(text: str, **kwargs) -> float:
        words = word_tokenize(text)
        words_count = len([w for w in words if w.isalpha()])
        return 9.0 if words_count >= 250 else 4.0
