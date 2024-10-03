import logging
import typing as T  # noqa

from sqlalchemy import select, not_, and_, func
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.enums import CompetenceEnum
from src.postgres.models.question import Question, QuestionAudioFile
from src.postgres.models.tg_user_question import TgUserQuestion
from src.repos.factory import RepoFactory


class QuestionRepo(RepoFactory):
    def __init__(self, model: T.Type[Question], session: async_sessionmaker):
        super().__init__(model, session)

    async def create_question(
        self,
        competence: CompetenceEnum,
        question_json: T.Dict,
        is_active: bool = True,
        question_audio_json: T.Dict = None
    ):
        return await self.insert_one(
            competence=competence,
            question_json=question_json,
            is_active=is_active,
            question_audio_json=question_audio_json
        )

    async def update_question(
        self,
        question_id: int,
        competence: CompetenceEnum = None,
        question_json: T.Dict = None,
        is_active: bool = None,
        question_audio_json: T.Dict = None
    ) -> bool:
        values = {
            "competence": competence,
            "question_json": question_json,
            "is_active": is_active,
            "question_audio_json": question_audio_json
        }
        values = {k: v for k, v in values.items() if v is not None}
        if not values:
            raise ValueError("At least one value must be provided")
        instance = await self.update({'id': question_id}, values)
        logging.info(instance)
        return instance

    async def get_question_by_id(self, question_id: int) -> T.Optional[Question]:
        async with self.session() as session:
            query = select(self.model).where(self.model.id == question_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_question_for_user(self, user_id: int, competence: CompetenceEnum) -> T.Optional[Question]:
        """
        Returns the question associated with the given user and competence if available.

        Checks if there's a question already started for the user. If found, returns it.
        If no started question exists, retrieves another question based on competence.

        If neither started nor available questions exist, returns None.

        :param user_id: The ID of the user for whom to retrieve the question.
        :param competence: The lesson section (competence) for which to retrieve the question, e.g., 'writing', etc.
        :return: A Question object if found, otherwise None.
        """
        subq = select(TgUserQuestion.question_id).where(
            and_(TgUserQuestion.user_id == user_id, TgUserQuestion.status.is_(True))
        )
        query = select(Question).where(
            not_(Question.id.in_(subq)),
            and_(Question.competence == competence, Question.is_active.is_(True))
        ).outerjoin(
            TgUserQuestion,
            and_(TgUserQuestion.user_id == user_id, TgUserQuestion.question_id == Question.id)
        ).order_by(func.random())

        async with self.session() as session:
            result = await session.execute(query)
            return result.scalars().first()

    async def get_question_filename(self, text_hash: str) -> T.Optional[str]:
        async with self.session() as session:
            query = select(QuestionAudioFile.filename).where(and_(QuestionAudioFile.text_hash == text_hash))
            result = await session.execute(query)
            return result.scalar()  # TODO: find the better way to avoid multiple filenames
