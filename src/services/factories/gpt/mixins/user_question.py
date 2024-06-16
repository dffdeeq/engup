import typing as T  # noqa

from src.repos.factories.question import QuestionRepo
from src.postgres.models.tg_user_question import TgUserQuestion


class UserQuestionMixin:
    def __init__(self, repo: QuestionRepo):
        self.repo = repo

    async def link_user_with_question(
        self,
        user_id: int,
        question_id: int,
        user_answer_json: T.Optional[dict] = None,
        user_result_json: T.Optional[dict] = None,
        already_complete: bool = False
    ) -> TgUserQuestion:
        instance = await self.repo.get_or_create_user_link_question(
            user_id=user_id,
            question_id=question_id,
            user_answer_json=user_answer_json,
            user_result_json=user_result_json,
            already_complete=already_complete
        )
        return instance

    async def update_user_question(
        self,
        user_id: int,
        question_id: int,
        user_answer_json: T.Optional[dict] = None,
        user_result_json: T.Optional[dict] = None,
        already_complete: bool = True
    ):
        await self.repo.update_many(
            conditions={'user_id': user_id, 'question_id': question_id},
            values={
                'user_answer_json': user_answer_json,
                'user_result_json': user_result_json,
                'status': already_complete
            },
            model=TgUserQuestion
        )
