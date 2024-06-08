from aiogram.fsm.state import State, StatesGroup


class SpeakingState(StatesGroup):
    first_step = State()
    second_step = State()
    third_step = State()


class WritingState(StatesGroup):
    get_user_answer = State()
