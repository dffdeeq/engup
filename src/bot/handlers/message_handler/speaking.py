import os.path
import typing as T  # noqa
import json

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from src.bot.core.states import SpeakingState
from src.bot.handlers.constants import SpeakingMessages
from src.bot.injector import INJECTOR
from src.postgres.enums import CompetenceEnum
from src.rabbitmq.producer.factories.apihost import ApiHostProducer
from src.services.factories.gpt import GPTService
from src.services.factories.voice import VoiceService

router = Router(name=__name__)


@router.callback_query(F.data == 'speaking', INJECTOR.inject_gpt)
async def speaking_start(callback: types.CallbackQuery, state: FSMContext, gpt_service: GPTService):
    await callback.answer()
    question = await gpt_service.get_or_generate_question_for_user(callback.from_user.id, CompetenceEnum.speaking)
    linked_instance = await gpt_service.link_user_with_question(callback.from_user.id, question.id)
    question_json: T.Dict = json.loads(question.question_json)
    await state.set_state(SpeakingState.first_part)
    await state.set_data({
        'part_1_questions': question_json['part_1'],
        'part_2_question': question_json['part_2'],
        'part_3_questions': question_json['part_3'],
        'part_1_current_question': 0,
        'part_1_q_0': question_json['part_1'][0],
        'linked_id': linked_instance.id,
    })

    await callback.message.answer(text=SpeakingMessages.FIRST_PART_MESSAGE_1)
    await callback.message.answer(text=SpeakingMessages.FIRST_PART_MESSAGE_2)
    await callback.message.answer(text=question_json['part_1'][0])


@router.message(SpeakingState.first_part, INJECTOR.inject_voice)
async def speaking_first_part(message: types.Message, state: FSMContext, voice_service: VoiceService):
    voice = message.voice
    if voice is None:
        await message.answer(text=SpeakingMessages.COULDNT_FIND_AUDIO)
        return

    state_data = await state.get_data()
    current_question_pk = int(state_data['part_1_current_question'])

    filepath = await voice_service.save_user_voicemail(voice, message.bot)
    await state.update_data({f'part_1_q_{current_question_pk}_file': filepath})

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
        text = SpeakingMessages.SECOND_PART_MESSAGE.format(question=part_2_question)
        await state.set_state(SpeakingState.second_part)
        await message.answer(text=text)


@router.message(SpeakingState.second_part, INJECTOR.inject_voice)
async def speaking_second_part(message: types.Message, state: FSMContext, voice_service: VoiceService):
    voice = message.voice
    if voice is None:
        await message.answer(text=SpeakingMessages.COULDNT_FIND_AUDIO)
        return

    filename = await voice_service.save_user_voicemail(voice, message.bot)
    current_question = (await state.get_data())['part_3_questions'][0]
    await state.update_data({
        'part_2_q_0_file': filename,
        'part_3_current_question': 0,
        'part_3_q_0': current_question
    })

    await state.set_state(SpeakingState.third_part)
    await message.answer(text=SpeakingMessages.THIRD_PART_MESSAGE)
    await message.answer(text=current_question)


@router.message(SpeakingState.third_part, INJECTOR.inject_voice, INJECTOR.inject_apihost_producer)
async def speaking_third_part(
    message: types.Message,
    state: FSMContext,
    voice_service: VoiceService,
    apihost_producer: ApiHostProducer
):
    voice = message.voice
    if voice is None:
        await message.answer(text=SpeakingMessages.COULDNT_FIND_AUDIO)
        return

    state_data = await state.get_data()
    current_question_pk = int(state_data['part_3_current_question'])

    filepath = await voice_service.save_user_voicemail(voice, message.bot)
    await state.update_data({f'part_3_q_{current_question_pk}_file': filepath})

    next_question_pk = int(state_data['part_3_current_question']) + 1

    if next_question_pk < len(state_data['part_3_questions']):
        next_question = state_data['part_3_questions'][next_question_pk]
        await state.update_data({
            'part_3_current_question': next_question_pk,
            f'part_3_q_{next_question_pk}': next_question
        })
        await message.answer(text=next_question)
    else:
        state_data[f'part_3_q_{current_question_pk}_file'] = filepath
        filepaths = []
        for i in range(len(state_data['part_1_questions'])):
            filepaths.append(state_data[f'part_1_q_{i}_file'])
        filepaths.append(str(state_data['part_2_q_0_file']))
        for i in range(len(state_data['part_3_questions'])):
            filepaths.append(state_data[f'part_3_q_{i}_file'])

        await voice_service.insert_into_temp_data(
            tg_user_question_id=state_data['linked_id'],
            first_file_name=os.path.basename(state_data['part_1_q_0']),
            first_part_questions=state_data['part_1_questions'],
            second_part_question=state_data['part_2_question'],
            third_part_questions=state_data['part_3_questions'],
        )
        await apihost_producer.send_to_transcription(filepaths)
        await state.clear()
        await message.answer(text=SpeakingMessages.CALCULATING_RESULT)
