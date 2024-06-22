import asyncio
import typing as T  # noqa

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.libs.factories.gpt.models.result import Result
from src.neural_networks.models.local_models import ScoreGeneratorNNModel
from src.postgres.enums import CompetenceEnum
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.question import Question
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

    def generate_result_local_model(self, text: str):
        self.check_or_load_models()
        result = self.nn_service.predict_all(text=text, model_names=NeuralNetworkConstants.predict_params)
        advice_dict = self.nn_service.select_random_advice(result)
        overall_score = self.nn_service.format_predict_to_scores(result)
        text = self.format_advice(advice_dict, result)
        print(text)

    @staticmethod
    def format_advice(advice_dict, results):
        output_text = ""
        sorted_categories = sorted(advice_dict.keys())
        for category in sorted_categories:
            output_text += f"{category}:\n"
            sorted_subcategories = sorted(advice_dict[category].keys())
            for subcategory in sorted_subcategories:
                result_key = next((key for key in results if subcategory in key), None)
                if result_key:
                    score = results[result_key]
                    advice = advice_dict[category][subcategory]
                    output_text += f"   - {subcategory}(score {score}) - {advice}\n"
        return output_text

    async def generate_result(self, text: str, competence: CompetenceEnum) -> Result:
        return await self.adapter.gpt_client.generate_result(text=text, competence=competence)

    @staticmethod
    async def format_question_answer_to_text(card_text: str, user_answer: str) -> str:
        return f"Card text: {card_text}, user's text: {user_answer}"

    @staticmethod
    async def format_question_answer_to_dict(card_text: str, user_answer: str) -> T.Dict:
        return {'card_text': card_text, 'user_answer': user_answer}


async def main():
    settings = Settings.new()
    session = initialize_postgres_pool(settings.postgres)
    service = ResultService(
        QuestionRepo(Question, session),
        Adapter(settings),
        session,
        settings,
        ScoreGeneratorNNModel()
    )
    text = """
Technology has undeniably transformed our lives, but its impact on sociability is a contentious issue. I disagree with the notion that technology is making people less sociable. While it may alter how we socialize, it does not necessarily reduce sociability.
Firstly, technology offers new avenues for social interaction. Social media platforms, messaging apps, and video calls enable people to maintain relationships regardless of geographical barriers. This connectivity can foster deeper, more frequent interactions with friends and family.
In conclusion, technology, when used mindfully, enhances sociability by expanding and enriching our social interactions, rather than diminishing them.
    """
    service.generate_result_local_model(text=text)


if __name__ == '__main__':
    asyncio.run(main())
