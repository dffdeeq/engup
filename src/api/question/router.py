from fastapi import APIRouter, Depends, HTTPException, Response
from starlette import status
from starlette.status import HTTP_201_CREATED

from src.api.depends import get_question_service
from src.api.question.schemas.message import MessageResponse
from src.api.question.schemas import question as q_schemas
from src.postgres.enums import CompetenceEnum
from src.services.factories.question import QuestionService

router = APIRouter(prefix='/questions')


@router.get(
    "/get",
    response_model=q_schemas.QuestionObjectResponseSchema,
)
async def get_question(user_id: int, question_service: QuestionService = Depends(get_question_service)):
    question = await question_service.get_or_generate_question_for_user(user_id, CompetenceEnum.reading)
    return question


@router.post(
    "/create",
    response_model=q_schemas.QuestionObjectResponseSchema,
    status_code=HTTP_201_CREATED
)
async def create_question(
    data: q_schemas.QuestionObjectSchema,
    question_service: QuestionService = Depends(get_question_service)
):
    try:
        obj = await question_service.create_question(**data.model_dump())
        if obj:
            return obj
        raise HTTPException(
            status_code=409, detail=f'Question with unique_id {data.question_json.unique_id} already exists')
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/update",
    response_model=MessageResponse
)
async def update_question(
    data: q_schemas.UpdateQuestionObjectSchema,
    question_service=Depends(get_question_service)
):
    try:
        result = await question_service.update_question(**data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if result is []:
        raise HTTPException(status_code=404, detail='Question not found')

    return Response(content='Question updated', status_code=status.HTTP_200_OK)


# @router.post(
#     '/complete',
#     response_model=
# )
# async def complete_question(
#     data:, user_question_service:UserQuestionService = Depends(get_user_question_service)
# ):
#     pass
