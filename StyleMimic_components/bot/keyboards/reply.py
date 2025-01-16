from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_reply_keyboard():
    upload_button = KeyboardButton(text="Загрузить файл с диалогами")
    start_dialog_button = KeyboardButton(text="Начать диалог со своей моделью")
    start_test_dialog_button = KeyboardButton(text="Начать диалог с тестовой моделью")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[upload_button], [start_dialog_button], [start_test_dialog_button]],
        resize_keyboard=True
    )

    return keyboard