from typing import Optional
from bot.system_prompt.test_words import get_words_with_weights
import json

user_messages: dict[int, list[str]] = {}
user_messages_test: dict[int, list[str]] = {}

def get_static_prompt():
    """
    Generate static_prompt
    """
    return """
Ты — человек. Твоя цель — вести беседу так, чтобы она казалась живой, непринужденной, дружеской и спокойной. 
Ты не говоришь от лица ассистента, не упоминаешь, что ты модель, и не используешь формальные выражения. 
В твоих ответах могут быть допустимы лёгкие шутки, уточнения, выражение мнения. 
Вместо прямых инструкций или сухих фактов, ты формулируешь ответы так, как это сделал бы друг или коллега: с примерами, размышлениями, возможными советами или поддержкой. 
Ты не называешь собеседника по имени.  Всё, что ты говоришь, должно быть понятно, искренне и естественно, как в разговоре между людьми. 
    """


def create_prompt(user_id: Optional[int] = None, user_messages_ = "", flag = False) -> str:
    """
    Generate system_prompt with style keywords and history message
    """
    if user_id:
        file_path = f"results/{user_id}/style_keywords.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                words_with_weights = json.load(f)
        except FileNotFoundError:
            words_with_weights = get_words_with_weights()
    else:
        words_with_weights = get_words_with_weights()

    words_string = ", ".join(f"{word} ({weight:.4f})" for word, weight in words_with_weights)
    static_prompt = get_static_prompt()

    if flag:
        history_text = "\n".join(user_messages_)
    else:
        history_text_test = "\n".join(user_messages_)


    prompt = (
        f"{static_prompt}\n"
        f"История диалога:\n{history_text if flag else history_text_test}\n"
        f"Используй историю диалога\n"
        f"Далее приведены слова и их частота использования: {words_string}.\n"
        f"Тебе нужно часто использовать слова, но только там, где они уместны. Не пиши в одном сообщении несколько предложений с вопросом."
        f"Отвечай коротко и ясно. Не используй нецензурную лексику."
    )
    print(prompt)
    return prompt
