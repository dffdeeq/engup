import typing as T  # noqa
import asyncio
import os

import nltk
from nltk import word_tokenize

from src.neural_network.base import NeuralNetworkBase
from src.neural_network.nn_models.utils.timeit import timeit
from src.repos.factories.user_question_metric import TgUserQuestionMetricRepo
from src.settings import NNModelsSettings


class TAAppropriateWordCount(NeuralNetworkBase):
    def __init__(self, settings: NNModelsSettings, uq_metric_repo: TgUserQuestionMetricRepo):
        self.nltk_dir = os.path.join(self._nn_models_dir, 'nltk')  # noqa
        super().__init__(settings, uq_metric_repo)

    def load(self):
        if not os.path.exists(self.nltk_dir):
            nltk.download('punkt', download_dir=self.nltk_dir)
        nltk.data.path.append(self.nltk_dir)
        super().load()

    @timeit
    def ta_appropriate_word_count(self, text: str, **kwargs) -> float:
        words = word_tokenize(text)
        words_count = len([w for w in words if w.isalpha()])

        score = 9.0 if words_count >= 250 else 4.0

        uq_id: T.Optional[int] = kwargs.get('uq_id', None)
        if uq_id is not None:
            asyncio.create_task(self.save_metric_data(uq_id, 'ta_awc', score))

        return score
