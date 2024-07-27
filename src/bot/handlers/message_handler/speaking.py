import asyncio
import os.path
import typing as T  # noqa
import json

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.core.filters.voicemail_filter import VoicemailFilter
from src.bot.core.states import SpeakingState
from src.bot.injector import INJECTOR
from src.postgres.enums import CompetenceEnum, PartEnum
from src.rabbitmq.producer.factories.apihost import ApiHostProducer
from src.services.factories.answer_process import AnswerProcessService
from src.services.factories.question import QuestionService
from src.services.factories.status_service import StatusService
from src.services.factories.tg_user import TgUserService
from src.services.factories.user_question import UserQuestionService
from src.services.factories.voice import VoiceService

from src.bot.constants import SpeakingMessages as Messages, DefaultMessages

router = Router(name=__name__)


@router.callback_query(
    F.data.startswith('speaking'),
    INJECTOR.inject_tg_user,
    INJECTOR.inject_question,
    INJECTOR.inject_uq,
    INJECTOR.inject_answer_process,
)
async def speaking_start(
    callback: types.CallbackQuery,
    state: FSMContext,
    tg_user_service: TgUserService,
    question_service: QuestionService,
    uq_service: UserQuestionService,
):
    await tg_user_service.mark_user_activity(callback.from_user.id, 'start speaking')
    await callback.answer()

    await callback.message.edit_text(text=Messages.DEFAULT_MESSAGE)

    question = await question_service.get_or_generate_question_for_user(callback.from_user.id, CompetenceEnum.speaking)
    uq_instance, spent_pts = await uq_service.get_or_create_user_question(callback.from_user.id, question.id)
    if spent_pts:
        await tg_user_service.mark_user_activity(callback.from_user.id, 'spent point')
        await tg_user_service.mark_user_pts(callback.from_user.id, 'spent', -1)
    question_json: T.Dict = json.loads(question.question_json)

    await state.set_state(SpeakingState.first_part)
    await state.set_data({
        'part_1_questions': question_json['part_1'],
        'part_2_question': question_json['part_2'],
        'part_3_questions': question_json['part_3'],
        'part_1_current_question': 0,
        'uq_id': uq_instance.id,
        'premium_queue': uq_instance.premium_queue,
    })

    await asyncio.sleep(2)
    await callback.message.answer(Messages.FIRST_PART_MESSAGE_1, disable_web_page_preview=True)
    await asyncio.sleep(2)
    if not uq_instance.premium_queue:
        await callback.message.answer(text=DefaultMessages.DONT_HAVE_POINTS)
        await asyncio.sleep(1)

    builder = InlineKeyboardBuilder([[InlineKeyboardButton(text='🔙 Back', callback_data='ielts_menu')]])

    await callback.message.answer(
        question_json['part_1'][0], disable_web_page_preview=True, reply_markup=builder.as_markup())


@router.message(
    SpeakingState.first_part,
    VoicemailFilter(),
    INJECTOR.inject_voice,
    INJECTOR.inject_answer_process
)
async def speaking_first_part(
    message: types.Message,
    state: FSMContext,
    voice_service: VoiceService,
    answer_process: AnswerProcessService
):
    state_data = await state.get_data()
    filename = os.path.basename(await voice_service.save_user_voicemail(message.voice, message.bot))
    question_text = state_data['part_1_questions'][state_data['part_1_current_question']]
    await answer_process.insert_temp_data(state_data['uq_id'], PartEnum.first, question_text, filename)

    next_question_pk = int(state_data['part_1_current_question']) + 1

    if next_question_pk < len(state_data['part_1_questions']):
        next_question = state_data['part_1_questions'][next_question_pk]
        await state.update_data({
            'part_1_current_question': next_question_pk,
            f'part_1_q_{next_question_pk}': next_question
        })
        await message.answer(text=next_question)
    else:
        part_2_question = state_data['part_2_question']
        await state.update_data({'part_2_q_0': part_2_question})
        text = Messages.SECOND_PART_MESSAGE.format(question=part_2_question)
        await state.set_state(SpeakingState.second_part)
        await message.answer(text=text)


@router.message(
    SpeakingState.second_part,
    VoicemailFilter(),
    INJECTOR.inject_voice,
    INJECTOR.inject_answer_process
)
async def speaking_second_part(
    message: types.Message,
    state: FSMContext,
    voice_service: VoiceService,
    answer_process: AnswerProcessService
):
    state_data = await state.get_data()
    filename = os.path.basename(await voice_service.save_user_voicemail(message.voice, message.bot))
    question_text = state_data['part_2_question']
    await answer_process.insert_temp_data(state_data['uq_id'], PartEnum.second, question_text, filename)

    current_question = (await state.get_data())['part_3_questions'][0]
    await state.update_data({
        'part_3_current_question': 0,
        'part_3_q_0': current_question
    })

    await state.set_state(SpeakingState.third_part)
    await message.answer(text=Messages.THIRD_PART_MESSAGE)
    await message.answer(text=current_question)

    await asyncio.sleep(60)
    # TODO: Check if user already sent voicemail
    await message.answer(text='Your time is out. Please start your speech.')


@router.message(
    SpeakingState.third_part,
    VoicemailFilter(),
    INJECTOR.inject_tg_user,
    INJECTOR.inject_voice,
    INJECTOR.inject_apihost_producer,
    INJECTOR.inject_answer_process,
    INJECTOR.inject_status
)
async def speaking_third_part(
    message: types.Message,
    state: FSMContext,
    tg_user_service: TgUserService,
    voice_service: VoiceService,
    apihost_producer: ApiHostProducer,
    answer_process: AnswerProcessService,
    status_service: StatusService,

):
    state_data = await state.get_data()
    filename = os.path.basename(await voice_service.save_user_voicemail(message.voice, message.bot))
    question_text = state_data['part_3_questions'][state_data['part_3_current_question']]
    await answer_process.insert_temp_data(state_data['uq_id'], PartEnum.third, question_text, filename)

    next_question_pk = int(state_data['part_3_current_question']) + 1

    if next_question_pk < len(state_data['part_3_questions']):
        next_question = state_data['part_3_questions'][next_question_pk]
        await state.update_data({
            'part_3_current_question': next_question_pk,
            f'part_3_q_{next_question_pk}': next_question
        })
        await message.answer(text=next_question)
    else:
        await tg_user_service.mark_user_activity(message.from_user.id, 'end speaking')
        await answer_process.update_user_qa_premium_queue(state_data['uq_id'], state_data['premium_queue'])
        filepaths = await answer_process.get_temp_data_filepaths(answer_process.session, state_data['uq_id'])
        await apihost_producer.create_task_send_to_transcription(filepaths, premium_queue=state_data['premium_queue'])
        await status_service.change_qa_status(state_data['uq_id'], status='Sent for transcription.')
        await state.clear()
        builder = InlineKeyboardBuilder([
            [InlineKeyboardButton(text='Result status', callback_data=f'result_status {state_data["uq_id"]}')]
        ])
        await message.answer(text=DefaultMessages.CALCULATING_RESULT, reply_markup=builder.as_markup())
