from fastapi import APIRouter, Depends, HTTPException, Response
from starlette import status
from starlette.status import HTTP_201_CREATED

from src.api.depends import get_question_service
from src.api.question.schemas import QuestionObjectSchema, UpdateObjectSchema, QuestionObjectResponseSchema, \
    MessageResponse
from src.services.factories.question import QuestionService

router = APIRouter(prefix='/questions')


@router.post(
    "/create",
    response_model=QuestionObjectResponseSchema,
    status_code=HTTP_201_CREATED
)
async def create_question(
    data: QuestionObjectSchema,
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
    data: UpdateObjectSchema,
    question_service=Depends(get_question_service)
):
    try:
        result = await question_service.update_question(**data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if result is []:
        raise HTTPException(status_code=404, detail='Question not found')

    return Response(content='Question updated', status_code=status.HTTP_200_OK)
