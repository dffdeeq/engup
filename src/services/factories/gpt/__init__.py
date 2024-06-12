from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.repos.factories.question import QuestionRepo
from src.services.factories.gpt.mixins.result import ResultMixin
from src.services.factories.gpt.mixins.question_generation import QuestionGenerationMixin
from src.services.factories.gpt.mixins.user_question import UserQuestionMixin
from src.services.factory import ServiceFactory
from src.settings import Settings


class GPTService(
    ServiceFactory,
    QuestionGenerationMixin,
    ResultMixin,
    UserQuestionMixin,
):
    def __init__(self, repo: QuestionRepo, adapter: Adapter, session: async_sessionmaker, settings: Settings):
        ServiceFactory.__init__(self, repo, adapter, session, settings)
        QuestionGenerationMixin.__init__(self, adapter, repo)
        ResultMixin.__init__(self, adapter)
        UserQuestionMixin.__init__(self, repo)
