from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.core.states import SpeakingState

router = Router(name=__name__)


first_step_answers = {
    'answers': ['What do you do for living?', 'What is your hobby?']
}


@router.callback_query(F.data == 'speaking')
async def speaking_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SpeakingState.first_step)
    await state.set_data({'answers': first_step_answers['answers'], 'current_answer': 0})

    await callback.message.answer(text='Great! I will ask you some questions. Please record audio to answer them')
    await callback.message.answer(text="Let's start with part 1")
    await callback.message.answer(text=first_step_answers['answers'][0])


@router.message(SpeakingState.first_step)
async def speaking_first_step(message: types.Message, state: FSMContext):
    voice = message.voice
    if voice is None:
        await message.answer(text='Sorry, I couldn\'t find the audio.\n\nPlease, send me an voice message')
        return

    state_data = await state.get_data()
    next_answer_pk = int(state_data['current_answer']) + 1

    if next_answer_pk < len(state_data['answers']):
        next_answer = state_data['answers'][next_answer_pk]
        await state.update_data({'current_answer': next_answer_pk})
        await message.answer(text=next_answer)
    else:
        text = ("Ok! Let's proceed to part 2. Here is your card:\nDescribe an item that someone else lost."
                "You should say:\n-What the item was.\n-When and where you found it.\n-What you did after you found it"
                "And explain have you felt about the situation.\n\nYou have 1 minute to prepare. Then record an audio "
                "up to 2 minutes")
        await state.set_state(SpeakingState.second_step)
        await message.answer(
            text=text)


@router.message(SpeakingState.second_step)
async def speaking_second_step(message: types.Message, state: FSMContext):
    voice = message.voice
    if voice is None:
        await message.answer(text='Sorry, I couldn\'t find the audio.\n\nPlease, send me an voice message')
        return

    await state.set_state(SpeakingState.third_step)
    await message.answer(text="Great! Let's continue to the part 3")
    await message.answer(text="What's kind of people tend to lose things more often than others?")


@router.message(SpeakingState.third_step)
async def speaking_third_step(message: types.Message, state: FSMContext):
    voice = message.voice
    if voice is None:
        await message.answer(text='Sorry, I couldn\'t find the audio.\n\nPlease, send me an voice message')
        return

    await state.clear()

    builder = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='Another test', callback_data='speaking'),
         InlineKeyboardButton(text='Main menu', callback_data='menu')],
    ])

    await message.answer(
        text="Ok! We've finished!\n\nYou result is amazing: you scored 7 in IELTS\n\nThere are some enhancements "
             "that you can apply in the future:\n - 1. ...\n - 2. ...\n\n...", reply_markup=builder.as_markup()
    )
