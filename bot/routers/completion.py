from typing import Optional

from aiogram import  Router
from aiogram.types import Message
from pydantic import BaseModel

from bot.ollama import OllamaChat, OllamaChatMessage, generate_chat_completion
from bot.ollama.dto import OllamaErrorChunk
from bot.settings import BASE_LANGUAGE, OLLAMA_MODEL, OLLAMA_MODEL_TEMPERATURE

from bot.translator import translate
from bot.system_prompt.prompt import create_prompt

router = Router()

class UserChat(BaseModel):
    ollama_chat: OllamaChat
    selected_model: str = OLLAMA_MODEL
    linked_last_messages: Optional[int] = None
    do_translate: bool = True
    previous_prompt: Optional[str] = None

chats: dict[int, UserChat] = {}


def wrap(s: str, w: int) -> list[str]:
    """
    Splits it into several messages if the response does not fit into one telegram message.
    """
    return [s[i : i + w] for i in range(0, len(s), w)]


async def generate(message: Message, user_id: int, text: str, system_prompt: str) -> list:
    """
    Generates a response from the model and returns the received message.
    """
    global initial_content
    _create_chat(user_id)

    chat = chats[user_id]

    # if text == "/translate_on":
    #     chats[user_id].do_translate = True
    #     return
    # if text == "/translate_off":
    #     chats[user_id].do_translate = False
    #     return

    chat.linked_last_messages = None

    msg = await message.answer("... генерация ...")

    if chat.do_translate:
        prompt = await translate(text, BASE_LANGUAGE, "ru")
    else:
        prompt = text
    chat.previous_prompt = prompt
    chat.ollama_chat.messages.append(OllamaChatMessage(role="user", content=prompt))
    print(f"[{user_id}]: {prompt}")

    assistant_content = ""
    async for is_done, chunk in generate_chat_completion(
        system_prompt,
        chat.ollama_chat.messages,
        chat.selected_model,
        temperature=OLLAMA_MODEL_TEMPERATURE,
    ):
        if is_done:
            wrapped_response = wrap(assistant_content, 4096)
            initial_content = wrapped_response.pop(0)
            try:
                await msg.edit_text(
                    (
                        (await translate(initial_content, "ru", BASE_LANGUAGE))
                        if chat.do_translate
                        else initial_content
                    ),
                )
            except Exception:
                print("Error to set")
            if wrapped_response:
                for text in wrapped_response:
                    msg = await msg.answer(text)
                    if chat.do_translate:
                        await msg.edit_text(
                            (
                                (await translate(text, "ru", BASE_LANGUAGE))
                                if chat.do_translate
                                else text
                            ),
                        )
            print(f"[{user_id}]: Finished!")
        else:
            if isinstance(chunk, OllamaErrorChunk):
                await message.answer(f"error: {chunk.error}")
                break
            assistant_content += chunk.message.content
    chat.linked_last_messages = msg.message_id

    chat.ollama_chat.messages.append(
        OllamaChatMessage(role="assistant", content=assistant_content)
    )
    return initial_content


async def handle_dialog_message_generic(message: Message, user_messages_dict: dict, is_dialog_state: bool):
    """
    Generates a response to the user and saves the history of the dialog.
    """
    if message.from_user and message.text:
        user_id = message.from_user.id

        if user_id not in user_messages_dict:
            user_messages_dict[user_id] = []

        messages = user_messages_dict[user_id]
        system_prompt = create_prompt(user_id, messages if messages else "", is_dialog_state)

        initial_content = await generate(message, user_id, message.text, system_prompt)

        user_messages_dict[user_id].extend([
            f"user: {message.text}",
            f"assistant: {initial_content}"
        ])

        if len(user_messages_dict[user_id]) > 30:
            user_messages_dict[user_id] = user_messages_dict[user_id][-30:]


def _create_chat(user_id: int) -> bool:
    """
    Creates a new chat for the user with the specified user_id
    """
    if user_id in chats:
        return False

    chats[user_id] = UserChat(
        selected_model=OLLAMA_MODEL,
        ollama_chat=OllamaChat(messages=[]),
    )
    return True