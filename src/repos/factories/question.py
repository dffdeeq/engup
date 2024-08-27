import typing as T  # noqa

from sqlalchemy import select, not_, and_
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.postgres.enums import CompetenceEnum
from src.postgres.models.question import Question
from src.postgres.models.tg_user_question import TgUserQuestion
from src.repos.factory import RepoFactory


class QuestionRepo(RepoFactory):
    def __init__(self, model: T.Type[Question], session: async_sessionmaker):
        super().__init__(model, session)

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
        ).order_by(TgUserQuestion.status)

        async with self.session() as session:
            result = await session.execute(query)
            return result.scalars().first()
