import json
import emoji

def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_data(data, filename='messages.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def remove_emojis(text):
    # Используем библиотеку emoji для удаления всех эмодзи
    return emoji.replace_emoji(text, replace='')  # Заменяем все эмодзи на пустую строку

def extract_text_content(message):
    """
    Extracts text content only, ignoring other data like links, stickers, or custom emojis.
    """
    if isinstance(message['text'], str):
        return remove_emojis(message['text'].strip())
    elif isinstance(message['text'], list):
        # Collect only text parts, ignore stickers, images, etc.
        text_parts = ''.join(part for part in message['text'] if isinstance(part, str))
        return remove_emojis(text_parts.strip()) if text_parts.strip() else None  # Return None if text is empty
    return None  # Return None for messages with photos, stickers, etc.

def process_messages(list_messages, from_user, response_key, reply_key):
    chat = []  # общий список для всех сообщений
    i = 0

    while i < len(list_messages):
        message = list_messages[i]

        # Проверяем, что сообщение не от нужного нам пользователя и содержит текст
        if message.get('from') != from_user and 'text' in message:
            text_content = extract_text_content(message)

            if text_content is None:  # Пропускаем стикеры и другие не-текстовые сообщения
                i += 1
                continue

            response = {response_key: text_content}
            # Добавляем пустую строку input перед output
            response["input"] = ""  # Добавлено здесь
            i += 1

            # Сбор ответов, если они следуют подряд
            replies = []
            while i < len(list_messages) and list_messages[i].get('from') == from_user:
                reply_text = extract_text_content(list_messages[i])
                if reply_text:
                    replies.append(reply_text.strip())
                i += 1

            if replies:
                response[reply_key] = '. '.join(replies).strip()
                chat.append(response)  # Добавляем ответ в общий список
        else:
            i += 1

    return chat

def path_to_messages(data):
    return [
        response
        for chat in data.get('chats', {}).get('list', [])
        if chat['type'] != 'saved_messages'
        for response in process_messages(chat['messages'], from_user="Ihor", response_key='instruction', reply_key='output')
    ]

def take_messages(filename='result.json'):
    data = load_data(filename)
    json_data_messages = path_to_messages(data)
    if json_data_messages:
        save_data(json_data_messages)

if __name__ == "__main__":
    take_messages()
