import typing as T  # noqa
import pandas as pd
from lexicalrichness import LexicalRichness


class VariedVocabulary:
    def __init__(self):
        self.ielts_academic_vocabulary: T.Optional[T.List[str]] = None

    @staticmethod
    def load_ielts_academic_words(file_path):
        df = pd.read_csv(file_path, header=None, names=["words"])
        return df['words'].tolist()

    @staticmethod
    def calculate_metric_score(value, thresholds):
        return next((score for threshold, score in thresholds if value >= threshold), 1)

    def lr_varied_vocabulary(self, text) -> float:
        lex = LexicalRichness(text)
        cttr = lex.cttr
        terms = lex.terms
        ielts_count = sum(1 for word in self.ielts_academic_vocabulary if word in set(text.lower().split()))
        thresholds = {
            'cttr': [(7.385, 9), (7.058, 8), (6.790, 7), (6.535, 6), (6.014, 5),
                     (5.690, 4), (4.251, 3), (3.251, 2), (2.251, 1)],
            'terms': [(250, 9), (200, 8), (150, 7), (100, 6), (75, 5), (50, 4), (25, 3)],
            'ielts_count': [(15, 9), (12, 8), (9, 7), (6, 6), (4, 5), (3, 4), (2, 3), (1, 2)]
        }
        scores = [
            VariedVocabulary.calculate_metric_score(cttr, thresholds['cttr']),
            VariedVocabulary.calculate_metric_score(terms, thresholds['terms']),
            VariedVocabulary.calculate_metric_score(ielts_count, thresholds['ielts_count'])
        ]
        final_score = round(sum(scores) / 3)
        return float(final_score)
