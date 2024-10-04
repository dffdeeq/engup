import asyncio
import hashlib
import logging
import os.path
import typing as T  # noqa
import uuid

import pandas as pd
from redis import asyncio as aioredis
import requests
from aiogram.types import CallbackQuery, BufferedInputFile
from pydantic import ValidationError
from sqlalchemy import insert, select, and_, cast, String
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.api.question.schemas.test import TestSchema
from src.libs.adapter import Adapter
from src.postgres.enums import CompetenceEnum
from src.repos.factories.question import QuestionRepo
from src.services.factories.S3 import S3Service
from src.services.factory import ServiceFactory
from src.settings import Settings
from src.libs.factories.gpt.models.question import Question as QuestionModel
from src.postgres.models.question import Question, QuestionAudioFile
from src.settings.static import OTHER_DATA_DIR


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
        self.redis = aioredis.from_url(settings.redis.dsn, decode_responses=True)

    async def create_question(
        self,
        competence: CompetenceEnum,
        question_json: T.Dict,
        is_active: bool = True,
        question_audio_json: T.Dict = None
    ) -> T.Optional[Question]:
        async with self.session() as session:
            query = select(Question).where(
                and_(cast(Question.question_json['unique_id'], String) == str(question_json['unique_id']))
            )
            result = await session.execute(query)
            obj = result.scalar()

            if obj:
                return None
            else:
                if competence == CompetenceEnum.reading:
                    try:
                        _ = TestSchema(**question_json)
                    except ValidationError as e:
                        logging.exception(f"Json does not validate {question_json} --> {e}")
                        raise e
                return await self.repo.create_question(competence, question_json, is_active, question_audio_json)

    async def update_question(
        self,
        question_id: int,
        competence: CompetenceEnum = None,
        question_json: T.Dict = None,
        is_active: bool = True,
        question_audio_json: T.Dict = None
    ):
        if competence == CompetenceEnum.reading and question_json is not None:
            try:
                _ = TestSchema(**question_json)
            except ValidationError as e:
                logging.exception(f"Json does not validate {question_json} --> {e}")
                raise e

        return await self.repo.update_question(question_id, competence, question_json, is_active, question_audio_json)

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

    async def synthesize_question_text(self, question_text: str, text_hash: str) -> T.Optional[str]:
        response = await self.adapter.apihost_client.send_text_to_synthesize(question_text)
        for i in range(15):
            await asyncio.sleep(2)
            url = await self.adapter.apihost_client.get_synthesize(response.process)
            if url:
                audio_response = requests.get(url, stream=True)
                if audio_response.status_code == 200:
                    with audio_response.raw as file:
                        audio_filename = uuid.uuid4().hex + '.mp3'
                        self.s3_service.upload_file_obj(file, filename=audio_filename)
                        async with self.session() as session:
                            stmt = insert(QuestionAudioFile).values(text_hash=text_hash, filename=audio_filename)
                            await session.execute(stmt)
                            await session.commit()
                        break

        return audio_filename

    async def get_question_audio_filename(self, question_text: str):
        text_hash = hashlib.md5(question_text.encode('utf-8')).hexdigest()
        lock_key = f'synthesize_lock:{text_hash}'
        not_locked = await self.redis.set(lock_key, "locked", ex=30, nx=True)
        if not_locked:
            filename = await self.repo.get_question_filename(text_hash)
            if not filename:
                filename = await self.synthesize_question_text(question_text, text_hash)
        else:
            for i in range(15):
                filename = await self.repo.get_question_filename(text_hash)
                if filename:
                    break
                await asyncio.sleep(2)
            else:
                filename = await self.synthesize_question_text(question_text, text_hash)

        return filename

    async def get_buffered_input_file_for_question_text(self, question_text: str) -> BufferedInputFile:
        question_audio_filename = await self.get_question_audio_filename(question_text)
        audio_stream = self.s3_service.get_file_obj(question_audio_filename)
        input_file = BufferedInputFile(audio_stream.read(), filename=question_audio_filename)
        return input_file

    @staticmethod
    async def get_question_essay_parts(essay_type: str) -> T.Tuple[str, T.List[str]]:
        df = pd.read_excel(os.path.join(OTHER_DATA_DIR, 'essay_types.xlsx'), sheet_name='Sheet1')
        filtered_df = df[df['name'] == essay_type]
        if filtered_df.empty:
            filtered_df = df[df['name'] == 'Opinion Essay']
        description = filtered_df['description'].values[0]
        p_values = filtered_df[['p1_desc', 'p2_desc', 'p3_desc', 'p4_desc']].values.flatten().tolist()
        return description, p_values

    @staticmethod
    async def serialize_questions(questions: T.List[QuestionModel], competence: CompetenceEnum) -> T.List[T.Dict]:
        return [{'competence': competence, 'question_json': question.model_dump_json()} for question in questions]

    @staticmethod
    def number_to_text(n):
        words = ["first", "second", "third", "fourth"]
        if 1 <= n <= len(words):
            return words[n - 1]
        return "Number out of range"
