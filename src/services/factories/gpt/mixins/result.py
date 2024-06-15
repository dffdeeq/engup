import logging
import typing as T  # noqa

from src.libs.adapter import Adapter
from src.libs.factories.gpt.models.result import Result
from pydantic import ValidationError
import asyncio
from src.postgres.enums import CompetenceEnum
from src.services.factories.gpt.constants import TextTemplates


class ResultMixin:
    def __init__(self, adapter: Adapter):
        self.adapter = adapter

    async def _generate_result(self, text: str, competence: CompetenceEnum) -> Result:
        answer = await self.adapter.gpt_client.generate_result(text=text, competence=competence)
        return answer

    async def try_generate_result(self, text: str, competence: CompetenceEnum, attempts: int = 3) -> T.Optional[Result]:
        for attempt in range(attempts):
            try:
                answer = await self._generate_result(text, competence)
                return answer
            except (TypeError, ValidationError) as e:
                logging.debug(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2)
        return None

    @staticmethod
    def format_user_voice_answer_to_text_request(
        questions_and_answers: T.Dict[str, T.Any],
        # questions_and_answers format = {'part_1': [...], 'part_2': {'q': q, 'a': a}, part_3: [...]}
    ) -> str:
        return TextTemplates.SPEECH_REQUEST_TEMPLATE.format(
            q_a_part_1='\n'.join([f'Q: {qa["q"]}\nA: {qa["a"]}' for qa in questions_and_answers['part_1']]),
            q_a_part_2=f'Q: {questions_and_answers["part_2"]["q"]}\nA: {questions_and_answers["part_2"]["a"]}',
            q_a_part_3='\n'.join([f'Q: {qa["q"]}\nA: {qa["a"]}' for qa in questions_and_answers['part_3']])
        )

    @staticmethod
    async def format_user_answer_to_text_request(card_text: str, user_answer: str) -> str:
        return f"Card text: {card_text}, user's text: {user_answer}"

    @staticmethod
    async def format_user_answer_to_dict(card_text: str, user_answer: str) -> T.Dict:
        return {'card_text': card_text, 'user_answer': user_answer}
