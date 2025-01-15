import logging
import os
from aiogram import Bot
from bot.algorithm.function_json import take_messages
from bot.algorithm.highlighting_a_style import load_dataset
from aiogram.types import Document
from bot.keyboards.inline import get_keyboard


async def save_file_for_user(user_id: int, file: Document, bot: Bot) -> None:
    """
    Processes files up to 50 mb and receives style keywords
    """
    user_folder_path = os.path.join("results", str(user_id))

    logging.info("Начало сохранения файла.", extra={"user_id": user_id})

    try:
        if not os.path.exists(user_folder_path):
            os.makedirs(user_folder_path)
            logging.info("Создана папка для пользователя.", extra={"user_id": user_id})

        file_path = os.path.join(user_folder_path, "result.json")

        file_info = await bot.get_file(file.file_id)

        await bot.download_file(file_info.file_path, file_path)
        logging.info(f"Файл сохранен по пути: {file_path}", extra={"user_id": user_id})

        await take_messages(user_id, file_path)
        logging.info("Файл передан для обработки.", extra={"user_id": user_id})

        style_keywords = load_dataset(user_id)
        if style_keywords:
            await bot.send_message(
                chat_id=user_id,
                text="Теперь вы можете начать диалог"
            )
            logging.info("Обработка данных завершена успешно.", extra={"user_id": user_id})
        else:
            logging.warning("Ключевые слова не были найдены.", extra={"user_id": user_id})

        if style_keywords:
            keyboard = get_keyboard(True)

            await bot.send_message(
                chat_id=user_id,
                text="Теперь вы можете начать диалог",
                reply_markup=keyboard
            )
    except Exception as e:
        logging.error(f"Ошибка: {e}", extra={"user_id": user_id})