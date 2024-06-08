import asyncio
import typing as T # noqa

from src.libs.factories.gpt.base import BaseGPTClient
from src.libs.factories.gpt.mixins.generate_answer import GenerateAnswerMixin
from src.libs.factories.gpt.mixins.generate_questions import GenerateQuestionsMixin
from src.libs.factories.gpt.models.competence import Competence
from src.libs.http_client import HttpClient
from src.settings import GPTSettings, Settings


class GPTClient(
    GenerateAnswerMixin,
    GenerateQuestionsMixin,
    BaseGPTClient
):
    def __init__(self, http_client: HttpClient, settings: GPTSettings):
        super().__init__(http_client, settings)
