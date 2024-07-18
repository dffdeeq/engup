import os
import typing as T  # noqa
import spacy

from src.neural_network.base import NeuralNetworkBase
from src.settings import NNModelsSettings
from src.settings.static import NN_MODELS_DIR


class MixOfComplexAndSimpleSentences(NeuralNetworkBase):
    def __init__(self, settings: NNModelsSettings):
        super().__init__(settings)
        self.nlp: T.Optional[spacy.Language] = None

    def load(self):
        if not self.nlp:
            self.nlp = spacy.load(os.path.join(NN_MODELS_DIR, 'en_core_web_sm-3.7.1'))
        super().load()

    def gr_mix_of_complex_and_simple_sentences(self, text, **kwargs) -> int:
        doc = self.nlp(text)
        sentences = list(doc.sents)
        return self.score_sentence_mix(sentences)

    def classify_sentence(self, sentence):
        doc = self.nlp(sentence)
        has_conjunction = any(token.dep_ == 'cc' for token in doc)
        has_sub_conjunction = any(token.dep_ == 'mark' for token in doc)
        if has_conjunction and has_sub_conjunction:
            return "Compound-Complex Sentence"
        if has_conjunction:
            return "Compound Sentence"
        if has_sub_conjunction:
            return "Complex Sentence"
        return "Simple Sentence"

    def score_sentence_mix(self, sentences):
        counts = {"Simple Sentence": 0, "Compound Sentence": 0, "Complex Sentence": 0, "Compound-Complex Sentence": 0}

        for sentence in sentences:
            classification = self.classify_sentence(sentence.text.strip())
            counts[classification] += 1

        total_sentences = len(sentences)
        if total_sentences == 0:
            return 0.0

        complex_ratio = (counts["Complex Sentence"] + counts["Compound-Complex Sentence"]) / total_sentences
        simple_ratio = counts["Simple Sentence"] / total_sentences
        compound_ratio = counts["Compound Sentence"] / total_sentences

        bands = [
            (9.0, 0.6, 0.2, 0.3),
            (8.0, 0.5, 0.3, 0.4),
            (7.0, 0.4, 0.4, 0.5),
            (6.0, 0.3, 0.5, 0.6),
            (5.0, 0.2, 0.6, 0.7),
            (4.0, 0.1, 0.7, 0.8),
        ]
        for band, c_ratio, s_ratio, cmp_ratio in bands:
            if complex_ratio >= c_ratio and simple_ratio <= s_ratio and compound_ratio <= cmp_ratio:
                return band
        return 3.0
