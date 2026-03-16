from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
        waiting_for_reply = State()
        target_user_id = State()

class AddMovieStates(StatesGroup):
        category = State()
        title = State()
        media = State()
        imdb = State()
        code = State()

class EditMovieStates(StatesGroup):
        waiting_for_code = State()
        choosing_field = State()
        updating_value = State()

class AIStates(StatesGroup):
        chatting = State()
    
