import asyncio
import json
import typing as T  # noqa
import uuid

import requests
from aiogram.types import CallbackQuery
from sqlalchemy import update, and_
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.postgres.enums import CompetenceEnum
from src.repos.factories.question import QuestionRepo
from src.services.factories.S3 import S3Service
from src.services.factory import ServiceFactory
from src.settings import Settings
from src.libs.factories.gpt.models.question import Question as QuestionModel
from src.postgres.models.question import Question


class QuestionService(ServiceFactory):
    def __init__(
        self,
        s3_service: S3Service,
        repo: QuestionRepo,
        adapter: Adapter,
        session: async_sessionmaker,
        settings: Settings
    ) -> None:
        super().__init__(repo, adapter, session, settings)
        self.repo = repo
        self.s3_service = s3_service

    async def get_or_generate_question_for_user(
        self,
        user_id: int,
        competence: CompetenceEnum,
        callback: CallbackQuery = None
    ) -> Question:
        question = await self.repo.get_question_for_user(user_id, competence)
        if not question:
            if callback:
                await callback.answer(text='Question is generating...')
            new_questions = await self.generate_and_save_questions(competence, 5)
            question = new_questions[0]
        return question

    async def generate_and_save_questions(self, competence, questions_number) -> T.List[Question]:
        questions = await self.adapter.gpt_client.generate_questions(competence, question_number=questions_number)
        question_objs = await self.repo.insert_many(await self.serialize_questions(questions, competence))
        return question_objs

    async def get_question_audio_filename(self, question_id: int) -> T.Optional[str]:
        question = await self.repo.get_question_by_id(question_id)
        if not question:
            return None

        audio_filename = question.question_audio_filename
        if not audio_filename:
            question_json = json.loads(question.question_json)
            response = await self.adapter.apihost_client.send_text_to_synthesize(question_json.get('part_1')[0])
            for i in range(30):
                await asyncio.sleep(1)
                url = await self.adapter.apihost_client.get_synthesize(response.process)
                if url:
                    audio_response = requests.get(url, stream=True)
                    if audio_response.status_code == 200:
                        with audio_response.raw as file:
                            audio_filename = uuid.uuid4().hex + '.mp3'
                            self.s3_service.upload_file_obj(file, filename=audio_filename)
                            async with self.session() as session:
                                stmt = update(Question).where(
                                    and_(Question.id == question.id)
                                ).values(question_audio_filename=audio_filename)
                                await session.execute(stmt)
                                await session.commit()
                            break

        return audio_filename

    @staticmethod
    async def serialize_questions(questions: T.List[QuestionModel], competence: CompetenceEnum) -> T.List[T.Dict]:
        return [{'competence': competence, 'question_json': question.model_dump_json()} for question in questions]
