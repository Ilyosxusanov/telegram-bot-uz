from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_reply = State()
    target_user_id = State()

class AddMovieStates(StatesGroup):
    title = State()
    description = State()
    photo = State()
    link = State()
    code = State()
    imdb = State()

class EditMovieStates(StatesGroup):
    waiting_for_code = State()
    choosing_field = State()
    updating_value = State()

class AIStates(StatesGroup):
    chatting = State()
