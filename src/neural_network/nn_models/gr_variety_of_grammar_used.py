import re
from collections import Counter

from data.other.gr_variety_of_grammar_constants import (GR_VARIETY_OF_GRAMMAR_CONJUNCTIONS,
                                                        GR_VARIETY_OF_GRAMMAR_TENSES, GR_VARIETY_OF_GRAMMAR_WEIGHTS)
from src.neural_network.base import NeuralNetworkBase
from src.neural_network.nn_models.utils.timeit import timeit


class GrVarietyOfGrammarUsed(NeuralNetworkBase):
    @timeit
    def gr_variety_of_grammar_used(self, text: str, **kwargs) -> float:
        tense_counts, conjunction_count = self.analyze_grammar(text)
        diversity_score = self.calculate_diversity_score(tense_counts)
        score = self.determine_band_gr(diversity_score, conjunction_count)
        return score

    @staticmethod
    def analyze_grammar(transcript):
        tenses = GR_VARIETY_OF_GRAMMAR_TENSES

        tense_counts = Counter()
        for tense, pattern in tenses.items():
            tense_counts[tense] = len(re.findall(pattern, transcript, re.IGNORECASE))
        conjunction_count = len(re.findall(GR_VARIETY_OF_GRAMMAR_CONJUNCTIONS, transcript, re.IGNORECASE))

        return tense_counts, conjunction_count

    @staticmethod
    def calculate_diversity_score(tense_counts):
        weights = GR_VARIETY_OF_GRAMMAR_WEIGHTS
        weighted_sum = sum((tense_counts[tense] > 0) * weight for tense, weight in weights.items())
        total_weights = sum(weights.values())
        diversity_score = weighted_sum / total_weights
        return diversity_score

    @staticmethod
    def determine_band_gr(diversity_score, conjunction_count):
        if diversity_score >= 0.6 and conjunction_count >= 15:
            band = 9.0
        elif diversity_score >= 0.5 and conjunction_count >= 12:
            band = 8.0
        elif diversity_score >= 0.4 and conjunction_count >= 10:
            band = 7.0
        elif diversity_score >= 0.3 and conjunction_count >= 8:
            band = 6.0
        else:
            band = 5.0

        return band
