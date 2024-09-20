import asyncio
import typing as T  # noqa
import json

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.core.filters.essay_filter import EssayFilter
from src.bot.core.states import WritingState
from src.bot.constants import DefaultMessages
from src.bot.injector import INJECTOR
from src.postgres.enums import CompetenceEnum
from src.rabbitmq.producer.factories.gpt import GPTProducer
from src.services.factories.question import QuestionService
from src.services.factories.status_service import StatusService
from src.services.factories.tg_user import TgUserService
from src.services.factories.user_question import UserQuestionService

router = Router(name=__name__)


@router.callback_query(
    F.data.startswith('writing'),
    INJECTOR.inject_tg_user,
    INJECTOR.inject_question,
    INJECTOR.inject_uq
)
async def writing_start(
    callback: types.CallbackQuery,
    state: FSMContext,
    tg_user_service: TgUserService,
    question_service: QuestionService,
    uq_service: UserQuestionService,
):
    if len(callback.data.split()) == 1:
        await tg_user_service.mark_user_activity(callback.from_user.id, 'go to writing')
        question = await question_service.get_or_generate_question_for_user(
            callback.from_user.id, CompetenceEnum.writing)
        question_json: T.Dict = json.loads(question.question_json)
        card_title, card_body = question_json.get('card_title'), question_json.get('card_body')
        essay_description, paragraphs = await question_service.get_question_essay_parts(card_title)

        await state.set_state(WritingState.get_user_answer)
        uq_instance = await uq_service.get_or_create_user_question(
            user_id=callback.from_user.id, question_id=question.id)
        await state.set_data({
            'question_id': question.id,
            'essay_description': essay_description,
            'paragraphs': paragraphs,
            'user_paragraphs': [],
            'current_paragraph': 0,
            'card_title': card_title,
            'card_body': card_body,
            'uq_id': uq_instance.id,
        })
        builder = InlineKeyboardBuilder([
            [InlineKeyboardButton(text='🚀 Start', callback_data='writing start')],
            [InlineKeyboardButton(text='🔙 Back', callback_data='ielts_menu')]
        ])
        await callback.message.edit_text(text=DefaultMessages.DEFAULT_TEXT, reply_markup=builder.as_markup())
    else:
        await callback.answer()
        await tg_user_service.mark_user_activity(callback.from_user.id, 'button start writing')
        state_data = await state.get_data()
        for text in [
            DefaultMessages.WRITING_FIRST_PARAGRAPH_1.format(card_text=state_data['card_body']),
            DefaultMessages.WRITING_FIRST_PARAGRAPH_2.format(
                essay_type=state_data['card_title'], essay_description=state_data['essay_description']
            ),
            DefaultMessages.WRITING_FIRST_PARAGRAPH_3.format(first_paragraph_info=state_data['paragraphs'][0])
        ]:
            await asyncio.sleep(2)
            await callback.message.answer(text=text)


@router.message(
    WritingState.get_user_answer,
    EssayFilter(),
    INJECTOR.inject_question,
    INJECTOR.inject_tg_user,
    INJECTOR.inject_uq,
)
async def writing_get_paragraphs(
    message: types.Message,
    state: FSMContext,
    question_service: QuestionService,
    uq_service: UserQuestionService,
    tg_user_service: TgUserService,
):
    paragraph_text = message.text
    state_data = await state.get_data()
    current_paragraph = state_data['current_paragraph']
    user_paragraphs = state_data['user_paragraphs']
    paragraphs = state_data['paragraphs']
    next_paragraph = current_paragraph + 1

    await tg_user_service.mark_user_activity(message.from_user.id, f'start part {next_paragraph} writing')

    user_paragraphs.append(paragraph_text)
    if next_paragraph < len(paragraphs):
        await state.update_data({'current_paragraph': next_paragraph, 'user_paragraphs': user_paragraphs})

        text = DefaultMessages.WRITING_PARAGRAPH_DEFAULT.format(
            paragraph=question_service.number_to_text(next_paragraph+1),
            paragraph_info=paragraphs[next_paragraph]
        )
        await message.answer(text=text)
        return

    await state.update_data({'user_paragraphs': user_paragraphs})
    user = await tg_user_service.get_or_create_tg_user(message.from_user.id)
    await tg_user_service.mark_user_activity(message.from_user.id, 'end writing')
    await state.set_state(WritingState.ending)

    user_essay = '\n'.join(user_paragraphs)
    user_answer_json = await uq_service.format_question_answer_to_dict(state_data['card_body'], user_essay)
    await state.update_data({'user_answer_json': user_answer_json, 'task_ready_to_proceed': 'writing'})

    if user.pts >= 1:
        text = ('Thank you for completing all the questions! To confirm your response, '
                'please choose one of the following options:\n\n'
                '1. Use 1 Premium Test to receive a detailed analysis\n')
        builder = InlineKeyboardBuilder([
            [InlineKeyboardButton(text='1', callback_data='confirm_task_writing premium')],
        ])

    else:
        text = ('You do not have any Premium Tests (PTs) left in your account.\n\n'
                'If you would like to spend 1 Premium Test and receive a detailed analysis and '
                'personalized recommendations based on your answers, please purchase some PTs, then go back and'
                'continue')
        builder = InlineKeyboardBuilder([
            [InlineKeyboardButton(text='Buy PTs', callback_data='pricing')],
        ])
    await message.answer(text, reply_markup=builder.as_markup())


@router.callback_query(
    F.data.startswith('confirm_task_writing'),
    INJECTOR.inject_tg_user,
    INJECTOR.inject_uq,
    INJECTOR.inject_gpt_producer,
    INJECTOR.inject_status
)
async def writing_confirm_task(
    callback: types.CallbackQuery,
    state: FSMContext,
    tg_user_service: TgUserService,
    uq_service: UserQuestionService,
    gpt_producer: GPTProducer,
    status_service: StatusService,
):
    param = callback.data.split()[1]
    premium = True if param == 'premium' else False

    state_data = await state.get_data()
    if premium is True:
        await tg_user_service.repo.deduct_point(callback.from_user.id)
        await tg_user_service.mark_user_activity(callback.from_user.id, 'spent pt writing')
        await tg_user_service.mark_user_pts(callback.from_user.id, 'spent', -1)

    user_answer_json = state_data['user_answer_json']
    await uq_service.simple_update_uq(state_data['uq_id'], user_answer_json)
    await gpt_producer.create_task_generate_result(state_data['uq_id'], premium)

    await status_service.change_qa_status(state_data['uq_id'], status='In Queue.')
    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='Result status', callback_data=f'result_status {state_data["uq_id"]}')]
    ])
    await callback.message.edit_text(text=DefaultMessages.CALCULATING_RESULT, reply_markup=builder.as_markup())
    await state.clear()
