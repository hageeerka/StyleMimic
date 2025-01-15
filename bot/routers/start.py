from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards.state_buttons import UploadState, DialogState, DialogStateTest
from bot.json.load_json import save_file_for_user
from bot.system_prompt.prompt import create_prompt, user_messages, user_messages_test
from bot.keyboards.reply import get_reply_keyboard
from bot.routers.completion import handle_dialog_message_generic
import logging

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@router.message(CommandStart())
async def start_command(message: Message) -> None:
    await message.answer(
        "Привет! Я бот, который имитирует пользовательский стиль общения",
        reply_markup=get_reply_keyboard()
    )


@router.callback_query(lambda c: c.data in ["upload_new_image", "start_dialog", "start_test_dialog"])
async def button_callback(query: CallbackQuery):
    await query.answer()

    bot = query.bot

    if query.data == "upload_new_image":
        await bot.edit_message_text(
            text="Пожалуйста, загрузите файл в формате result.json.",
            chat_id=query.message.chat.id,
            message_id=query.message.message_id
        )
    elif query.data == "start_dialog":
        await bot.edit_message_text(
            text="Диалог начат. Напишите мне сообщение!",
            chat_id=query.message.chat.id,
            message_id=query.message.message_id
        )
    elif query.data == "start_test_dialog":
        await bot.edit_message_text(
            text="Тестовый диалог начат. Напишите мне сообщение!",
            chat_id=query.message.chat.id,
            message_id=query.message.message_id
        )


@router.message(lambda message: message.text in ["Загрузить файл с диалогами", "Начать диалог со своей моделью", "Начать диалог с тестовой моделью"])
async def handle_reply(message: Message, state: FSMContext):
    if message.text == "Загрузить файл с диалогами":
        await message.answer("Пожалуйста, загрузите файл в формате result.json.")
        await state.set_state(UploadState.waiting_for_file)
    elif message.text == "Начать диалог со своей моделью":
        await message.answer("Диалог со своей моделью начат. Напишите мне сообщение!")
        await state.set_state(DialogState.waiting_for_message)
    elif message.text == "Начать диалог с тестовой моделью":
        await message.answer("Диалог с тестовой моделью начат. Напишите мне сообщение!")
        await state.set_state(DialogStateTest.waiting_for_message)


@router.message(UploadState.waiting_for_file)
async def handle_document(message: Message, state: FSMContext):
    """
    Downloads the file and analyzes it
    """
    document = message.document
    if document and document.file_name == "result.json":
        await message.answer("Файл успешно загружен! Происходит обработка, пожалуйста, подождите.")
        user_id = message.from_user.id
        file = await message.bot.get_file(document.file_id)
        await save_file_for_user(user_id, file, message.bot)
        await state.clear()
    else:
        await message.answer("Файл не соответствует нужному типу данных. Попробуйте снова.")


# async def handle_dialog_message_generic(message: Message, user_messages_dict: dict, is_dialog_state: bool):
#     """
#     Generates a response to the user and saves the history of the dialog.
#     """
#     if message.from_user and message.text:
#         user_id = message.from_user.id
#
#         if user_id not in user_messages_dict:
#             user_messages_dict[user_id] = []
#
#         messages = user_messages_dict[user_id]
#         system_prompt = create_prompt(user_id, messages if messages else "", is_dialog_state)
#
#         initial_content = await generate(message, user_id, message.text, system_prompt)
#
#         user_messages_dict[user_id].extend([
#             f"user: {message.text}",
#             f"assistant: {initial_content}"
#         ])
#
#         if len(user_messages_dict[user_id]) > 30:
#             user_messages_dict[user_id] = user_messages_dict[user_id][-30:]

@router.message(DialogState.waiting_for_message)
async def handle_dialog_message(message: Message):
    """
    Dialogue with our model
    """
    await handle_dialog_message_generic(message, user_messages, True)

@router.message(DialogStateTest.waiting_for_message)
async def handle_dialog_message_test(message: Message):
    """
    Dialogue with the test model
    """
    await handle_dialog_message_generic(message, user_messages_test, False)