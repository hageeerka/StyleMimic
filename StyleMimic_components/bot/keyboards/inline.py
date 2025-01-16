from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard(flag=None) -> InlineKeyboardMarkup:
    if flag:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Загрузить файл с диалогами", callback_data="upload_new_image")],
                [InlineKeyboardButton(text="Начать диалог со своей моделью", callback_data="start_dialog")]
                [InlineKeyboardButton(text="Начать диалог с тестовой моделью", callback_data="start_test_dialog")]
            ]
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Загрузить файл с диалогами", callback_data="upload_new_image")],
                [InlineKeyboardButton(text="Начать диалог с тестовой моделью", callback_data="start_test_dialog")]
            ]
        )
    return keyboard