import logging
import math
import typing as T  # noqa

from sqlalchemy.ext.asyncio import async_sessionmaker

from data.other.criteria_json import GRAMMAR_AND_LEXICAL_ERRORS_ADVICE
from src.libs.adapter import Adapter
from src.libs.factories.gpt.models.result import Result
from src.neural_network import ScoreGeneratorNNModel
from src.postgres.enums import CompetenceEnum
from src.repos.factories.question import QuestionRepo
from src.services.constants import NeuralNetworkConstants
from src.services.factory import ServiceFactory
from src.settings import Settings


class ResultService(ServiceFactory):
    def __init__(
        self,
        repo:
        QuestionRepo,
        adapter: Adapter,
        session: async_sessionmaker,
        settings: Settings,
        nn_service: ScoreGeneratorNNModel
    ) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo
        self.nn_service = nn_service

    def check_or_load_models(self):
        if not self.nn_service.models:
            self.nn_service.load_models(NeuralNetworkConstants.predict_params)

    def _generate_result_local_model(
        self,
        text: str,
        competence: CompetenceEnum,
        premium: bool = False
    ) -> T.List[str]:
        self.check_or_load_models()
        results = self.nn_service.predict_all(text=text, model_names=NeuralNetworkConstants.predict_params)
        gr_score, gr_errors, lxc_errors, pnkt_errors = results.pop('clear_grammar_result')
        results['gr_Clear and correct grammar'] = gr_score
        advice_dict = self.nn_service.select_random_advice(results)
        print(advice_dict)
        logging.info(advice_dict)
        advice_dict['Grammatical Range']['Clear and correct grammar'] = GRAMMAR_AND_LEXICAL_ERRORS_ADVICE[gr_score]
        result = self.format_advice(advice_dict, results, competence)
        if premium:
            grammar_errors = self.format_grammar_errors(gr_errors, lxc_errors, pnkt_errors)
            result.append(grammar_errors)
        return result

    async def generate_result(
        self, text: str,
        competence: CompetenceEnum,
        local_model: bool = False,
        premium: bool = False
    ) -> T.Union[Result, T.List]:
        if local_model:
            return self._generate_result_local_model(text, competence, premium)
        return await self.adapter.gpt_client.generate_result(text=text, competence=competence)

    @staticmethod
    def format_advice(advice_dict, results, competence: CompetenceEnum):
        output_texts = []
        all_category_min_scores = []
        for category, subcategories in advice_dict.items():
            sorted_advice = sorted(
                ((results.get(key, 0), advice) for subcategory, advice in subcategories.items() for key in results if
                 subcategory in key),
                reverse=False, key=lambda x: x[0]
            )
            if sorted_advice:
                category_min_score = sorted_advice[0][0]
                all_category_min_scores.append(category_min_score)
                category_advice_text = [f"{'✅' if score >= 7 else '⚠️'} {advice}" for score, advice in sorted_advice]
                category_text = f"<b>{category} (score {category_min_score}):</b>\n\n" + "\n".join(category_advice_text)
                output_texts.append(category_text)
        if all_category_min_scores:
            average_score = math.floor(sum(all_category_min_scores) / len(all_category_min_scores) * 2) / 2
            output_texts.insert(0, f"\nYour <b>IELTS</b> {competence.value} <b>score</b> is <b>{average_score:.1f}</b>")
        return output_texts

    @staticmethod
    def format_error_examples(error_list, error_type):
        examples = [f"    <b>{error_type} Mistakes</b> ({len(error_list)}):\n"]
        for i, error in enumerate(error_list, 1):
            highlighted_text = error.context.replace(error.matchedText, f"<u>{error.matchedText}</u>")
            examples.append(f"        <b>Example {i}:</b> \"{highlighted_text}\" (Comment: \"{error.message}\")\n")
        return examples

    @staticmethod
    def format_grammar_errors(grammar_errors: T.List, lexical_errors: T.List, punctuation_errors: T.List) -> str:
        output = [
            "<b>Grammar and lexical errors:</b>\n\n",
            f"During the review of your text, we identified a total of <b>{len(grammar_errors)} grammar mistakes, "
            f"{len(lexical_errors)} lexical mistakes </b> and <b>{len(punctuation_errors)} punctuation mistakes</b>. "
        ]
        if len(grammar_errors + lexical_errors + punctuation_errors) > 0:
            output.append("Below are some examples of each type of error:\n\n")
            output.extend(ResultService.format_error_examples(grammar_errors, "Grammar"))
            output.append("\n")
            output.extend(ResultService.format_error_examples(lexical_errors, "Lexical"))
            output.append("\n")
            output.extend(ResultService.format_error_examples(punctuation_errors, "Punctuation"))
            output.append("\nIt is important to address these mistakes to enhance the clarity "
                          "and professionalism of your writing.\n")
        final_output = "".join(output)
        return final_output
