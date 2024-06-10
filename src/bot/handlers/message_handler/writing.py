import typing as T  # noqa
import asyncio
import json

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from src.bot.core.states import WritingState
from src.bot.handlers.utils import answer_to_message_parts
from src.bot.injector import INJECTOR
from src.postgres.enums import CompetenceEnum
from src.services.factories.gpt import GPTService
from src.services.factories.tg_bot import TgBotService

router = Router(name=__name__)


@router.callback_query(F.data == 'writing', INJECTOR.inject_tg_bot, INJECTOR.inject_gpt)
async def writing_start(
    callback: types.CallbackQuery,
    state: FSMContext,
    tg_bot_service: TgBotService,
    gpt_service: GPTService,
):
    user = await tg_bot_service.get_or_create_tg_user(tg_id=callback.from_user.id)
    question = await gpt_service.get_question_for_user(user_id=user.id, competence=CompetenceEnum.writing)

    question_json = json.loads(question.question_json)

    await state.set_state(WritingState.get_user_answer)
    await state.set_data({'question_id': question.id, 'card_body': question_json['card_body']})

    text = (f'<b>Card title:</b> {question_json["card_title"]}\n\n'
            f'<b>Card body:</b> {question_json["card_body"]}')
    await callback.message.edit_text(text=text)


@router.message(WritingState.get_user_answer, INJECTOR.inject_tg_bot, INJECTOR.inject_gpt)
async def writing_get_user_answer(
    message: types.Message,
    state: FSMContext,
    tg_bot_service: TgBotService,
    gpt_service: GPTService
):
    user = await tg_bot_service.get_or_create_tg_user(tg_id=message.from_user.id)
    user_answer = message.text
    if len(user_answer.split()) < 150:
        await message.answer(text='Your input text is too short. Please enter at least 150 words.')
        return

    state_data = await state.get_data()
    question_id = state_data['question_id']
    card_body = state_data['card_body']

    user_answer_text = f"Card text: {card_body}, user's text: {user_answer}"
    user_answer_json = {
        'card_text': card_body,
        'user_answer': user_answer
    }

    try:
        user_result = await gpt_service.get_answer(text=user_answer_text, competence=CompetenceEnum.writing)
    except TypeError:
        await message.answer(text='GPT Service validation error. Please try again.')
        await state.clear()
        return

    user_result_json = user_result.model_dump()

    await gpt_service.associate_user_and_question(
        user_id=user.id,
        question_id=int(question_id),
        user_answer_json=user_answer_json,
        user_result_json=user_result_json,
        already_complete=True
    )

    message_parts = await answer_to_message_parts(user_result)
    for msg in message_parts:
        await message.answer(text=msg)
        await asyncio.sleep(3)
