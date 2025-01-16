from aiogram.fsm.state import State, StatesGroup


# Define the state for waiting
class UploadState(StatesGroup):
    waiting_for_file = State()

class DialogState(StatesGroup):
    waiting_for_message = State()

class DialogStateTest(StatesGroup):
    waiting_for_message = State()