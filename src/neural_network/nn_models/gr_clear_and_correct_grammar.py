import typing as T  # noqa

import language_tool_python
from language_tool_python import Match

from src.neural_network.base import NeuralNetworkBase
from src.neural_network.nn_models.utils.timeit import timeit
from src.postgres.enums import CompetenceEnum
from src.settings import NNModelsSettings


class GRClearAndCorrectGrammar(NeuralNetworkBase):
    def __init__(self, settings: NNModelsSettings):
        super().__init__(settings)
        self.language_tool: T.Optional[language_tool_python.LanguageTool] = None

    def load(self):
        if not self.language_tool:
            self.language_tool = language_tool_python.LanguageTool('en-US')
        super().load()

    @timeit
    def gr_clear_and_correct_grammar(self, text, **kwargs) -> T.Tuple[float, T.List, T.List, T.List]:
        text_ = kwargs.get('answers_text_only', None)
        if text_ is None:
            text_ = text
        grammar_score, grammar_errors, lexical_errors, punctuation_errors = self.get_grammar_score_and_grammar_errors(
            text=text_, tool=self.language_tool, competence=kwargs.get('competence', CompetenceEnum.writing))
        return grammar_score, grammar_errors, lexical_errors, punctuation_errors

    def get_grammar_score_and_grammar_errors(
        self,
        text: str,
        tool: language_tool_python.LanguageTool,
        competence: CompetenceEnum = CompetenceEnum.writing
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
                if match.category != "PUNCTUATION":
                    grammar_errors.append(match)
        grammar_errors_len = len(grammar_errors)
        total_words = len(text.split())
        error_density = grammar_errors_len / total_words if total_words > 0 else 0
        return (float(self.get_grammar_score(grammar_errors_len if competence == CompetenceEnum.writing
                                             else error_density, competence)),
                grammar_errors, lexical_errors, punctuation_errors)

    @staticmethod
    def get_grammar_score(value, competence: CompetenceEnum = CompetenceEnum.writing):
        if competence == CompetenceEnum.writing:
            if value < 2:
                return 9
            elif value < 4:
                return 8
            elif value < 6:
                return 7
            elif value < 11:
                return 6
            elif value < 16:
                return 5
            elif value < 21:
                return 4
            elif value < 26:
                return 3
            elif value < 31:
                return 2
        elif competence == CompetenceEnum.speaking:
            if value <= 0.02:
                return 9
            elif value <= 0.04:
                return 8
            elif value <= 0.06:
                return 7
            elif value <= 0.08:
                return 6
            elif value <= 0.10:
                return 5
            elif value <= 0.12:
                return 4
            elif value <= 0.14:
                return 3
            elif value <= 0.16:
                return 2
        return 1
