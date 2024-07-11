import typing as T  # noqa

import language_tool_python
from language_tool_python import Match

from src.neural_network.base import NeuralNetworkBase
from src.settings import NNModelsSettings


class GrClearAndCorrectGrammar(NeuralNetworkBase):
    def __init__(self, settings: NNModelsSettings):
        super().__init__(settings)
        self.language_tool: T.Optional[language_tool_python.LanguageTool] = None

    def load(self):
        if not self.language_tool:
            self.language_tool = language_tool_python.LanguageTool('en-US')
        super().load()

    def gr_clear_and_correct_grammar(self, text) -> T.Tuple[float, T.List, T.List, T.List]:
        grammar_score, grammar_errors, lexical_errors, punctuation_errors = self.get_grammar_score_and_grammar_errors(
            text=text, tool=self.language_tool)
        return grammar_score, grammar_errors, lexical_errors, punctuation_errors

    def get_grammar_score_and_grammar_errors(
        self,
        text: str,
        tool: language_tool_python.LanguageTool
    ) -> T.Tuple[float, T.List[Match], T.List[Match], T.List[Match]]:
        matches = tool.check(text)
        grammar_errors = []
        lexical_errors = []
        punctuation_errors = []
        for match in matches:
            issue_type = match.ruleIssueType.lower()
            if 'grammar' in issue_type:
                grammar_errors.append(match)
            elif 'typographical' in issue_type or 'whitespace' in issue_type:
                punctuation_errors.append(match)
            elif 'spelling' in issue_type:
                lexical_errors.append(match)
            else:
                grammar_errors.append(match)
        grammar_errors_len = len(grammar_errors)
        return self.get_grammar_score(grammar_errors_len), grammar_errors, lexical_errors, punctuation_errors

    @staticmethod
    def get_grammar_score(grammar_errors_num):
        bands = {
            range(0, 2): 9,
            range(2, 4): 8,
            range(4, 6): 7,
            range(6, 11): 6,
            range(11, 16): 5,
            range(16, 21): 4,
            range(21, 26): 3,
            range(26, 31): 2
        }
        return next((band for error_range, band in bands.items() if grammar_errors_num in error_range), 1)
