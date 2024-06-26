import typing as T  # noqa

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.libs.factories.gpt.models.result import Result
from src.neural_network.models.local_models import ScoreGeneratorNNModel
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

    def _generate_result_local_model(self, text: str) -> T.List[str]:
        self.check_or_load_models()
        results = self.nn_service.predict_all(text=text, model_names=NeuralNetworkConstants.predict_params)
        advice_dict = self.nn_service.select_random_advice(results)
        return self.format_advice(advice_dict, results)

    async def generate_result(
        self, text: str,
        competence: CompetenceEnum,
        local_model: bool = False
    ) -> T.Union[Result, T.List]:
        if local_model:
            return self._generate_result_local_model(text)
        return await self.adapter.gpt_client.generate_result(text=text, competence=competence)

    @staticmethod
    def format_advice(advice_dict, results):
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
            average_score = sum(all_category_min_scores) / len(all_category_min_scores)
            output_texts.insert(0, f"\nYour <b>IELTS</b> writing <b>score</b> is <b>{average_score:.1f}</b>")
        return output_texts
