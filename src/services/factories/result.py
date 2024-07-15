import math
import typing as T  # noqa

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import async_sessionmaker

from data.other.criteria_json import GRAMMAR_AND_LEXICAL_ERRORS_ADVICE
from src.libs.adapter import Adapter
from src.neural_network import ScoreGeneratorNNModel
from src.postgres.enums import CompetenceEnum
from src.postgres.models.tg_user import TgUser
from src.postgres.models.tg_user_question import TgUserQuestion
from src.repos.factories.question import QuestionRepo
from src.services.constants import NeuralNetworkConstants as NNConstants
from src.services.factory import ServiceFactory
from src.settings import Settings


class ResultService(ServiceFactory):
    def __init__(
        self,
        repo: QuestionRepo,
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
            self.nn_service.load_models(NNConstants.predict_params['to_load'])

    async def generate_result(
        self,
        text: str,
        competence: CompetenceEnum,
        premium: bool = False,
        **kwargs
    ) -> T.List:
        self.check_or_load_models()
        return self._generate_result_local_model(text, competence, premium, **kwargs)

    def _generate_result_local_model(
        self,
        text: str,
        competence: CompetenceEnum,
        premium: bool = False,
        **kwargs
    ) -> T.List[str]:
        predict_params = NNConstants.predict_params[competence]
        results = self.nn_service.predict_all(text=text, model_names=predict_params)
        if (filepaths := kwargs.get('voice_filepaths')) is not None:
            pronunciation_score = self.nn_service.get_pronunciation_score(filepaths)
            results['pr_Pronunciation general'] = pronunciation_score

        gr_score, gr_errors, lxc_errors, pnkt_errors = results.pop('clear_grammar_result')
        results['gr_Clear and correct grammar'] = gr_score
        advice_dict = self.nn_service.select_random_advice(results)
        if gr_score < 5:
            gr_score = 5
        advice_dict['Grammatical Range']['Clear and correct grammar'] = GRAMMAR_AND_LEXICAL_ERRORS_ADVICE[gr_score]
        temp_score = kwargs.get('temp_score', 5)
        result = self.format_advice(advice_dict, results, competence, temp_score)

        if competence == competence.writing and premium:
            grammar_errors = self.format_grammar_errors(gr_errors, lxc_errors, pnkt_errors)
            result.append(grammar_errors)
        return result

    async def update_uq(self, instance: TgUserQuestion, user_result_json):
        async with self.session() as session:
            instance.user_result_json = user_result_json
            instance.status = True
            session.add(instance)

            user_query = await session.execute(select(TgUser).where(and_(TgUser.id == instance.user_id)))
            user = user_query.scalar_one_or_none()
            user.completed_questions += 1
            session.add(user)
            if user.completed_questions == 3 and user.referrer_id:
                referrer_query = await session.execute(
                    select(TgUser).where(and_(TgUser.id == user.referrer_id))
                )
                referrer = referrer_query.scalar_one_or_none()
                if referrer:
                    referrer.pts += 5
                    session.add(referrer)
            await session.commit()

    @staticmethod
    def format_advice(advice_dict, results, competence: CompetenceEnum, temp_score: int):
        output_texts = []
        all_category_min_scores = [temp_score, ]
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
