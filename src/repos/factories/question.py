import typing as T  # noqa

from sqlalchemy import select, not_, and_
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.enums import CompetenceEnum
from src.postgres.models.question import Question
from src.postgres.models.tg_user_question import TgUserQuestion
from src.repos.factory import RepoFactory


class QuestionRepo(RepoFactory):
    def __init__(self, model: T.Type[Question], session: async_sessionmaker):
        super().__init__(model, session)  # noqa

    async def link_user_with_question(
        self,
        user_id: int,
        question_id: int,
        user_answer_json: T.Optional[dict] = None,
        user_result_json: T.Optional[dict] = None,
        already_complete: bool = False
    ):
        instance = await self.insert_one(
            model=TgUserQuestion,
            user_id=user_id,
            question_id=question_id,
            user_answer_json=user_answer_json,
            user_result_json=user_result_json,
            status=already_complete
        )
        return instance

    async def get_or_create_user_link_question(
        self,
        user_id: int,
        question_id: int,
        user_answer_json: T.Optional[dict] = None,
        user_result_json: T.Optional[dict] = None,
        already_complete: bool = False
    ):
        stmt = select(TgUserQuestion).where(and_(
            TgUserQuestion.user_id == user_id, TgUserQuestion.question_id == question_id))
        async with self.session() as session:
            result = await session.execute(stmt)
            instance = result.scalar_one_or_none()
            if instance is None:
                instance = await self.link_user_with_question(
                    user_id=user_id,
                    question_id=question_id,
                    user_answer_json=user_answer_json,
                    user_result_json=user_result_json,
                    already_complete=already_complete
                )
            return instance

    async def get_question_for_user(self, user_id: int, competence: CompetenceEnum) -> Question:
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
        stmt = select(Question).where(
            not_(Question.id.in_(subq)),
            and_(Question.competence == competence, Question.is_active.is_(True))
        ).outerjoin(
            TgUserQuestion,
            and_(TgUserQuestion.user_id == user_id, TgUserQuestion.question_id == Question.id)
        ).order_by(TgUserQuestion.status)

        async with self.session() as session:
            result = await session.execute(stmt)
            return result.scalars().first()
