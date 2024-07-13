from fuzzywuzzy import process, fuzz

from data.other.idioms import IDIOMS_LIST
from src.neural_network.base import NeuralNetworkBase
from src.settings import NNModelsSettings


class LrIdiomaticVocabulary(NeuralNetworkBase):
    def __init__(self, settings: NNModelsSettings):
        super().__init__(settings)
        self.idioms = None

    def load(self):
        if not self.idioms:
            self.idioms = IDIOMS_LIST
        super().load()

    def lr_idiomatic_vocabulary_or_expressions(self, text, threshold=65):
        found_idioms = []
        for idiom in self.idioms:
            if process.extractOne(idiom, [text], scorer=fuzz.partial_ratio)[1] >= threshold:
                found_idioms.append(idiom)
        found_idioms = list(set(found_idioms))

        return 9 if len(found_idioms) >= 2 else 6
