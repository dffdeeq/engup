class AccurateSpellingAndWordFormation:
    def __init__(self):
        self.language_tool = None

    def lr_accurate_spelling_and_word_formation(self, text) -> float:
        matches = self.language_tool.check(text)
        lexical_errors = [match for match in matches if 'spelling' in match.ruleIssueType.lower()]
        total_words = len(text.split())
        lexical_error_rate = len(lexical_errors) / total_words if total_words > 0 else 0

        thresholds = [(0.005, 9), (0.01, 8), (0.015, 7), (0.02, 6), (0.03, 5), (0.04, 4), (0.05, 3), (0.06, 2)]
        return float(next((score for threshold, score in thresholds if lexical_error_rate <= threshold), 1))
