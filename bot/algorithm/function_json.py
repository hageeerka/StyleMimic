import json
import emoji
import os
from bot.algorithm.highlighting_a_style import analyze_style


def load_data(filename):
    """
    Downloading data from a file
    """
    print(f"Loading data from {filename}")
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    print(f"Loaded data successfully")
    return data


def save_data(data, filename='messages.json'):
    """
    Saving data to a file
    """
    print(f"Saving data to {filename}")
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, ensure_ascii=False, indent=4, fp=file)
    print(f"Data saved successfully to {filename}")


def remove_emojis(text):
    """
    Removing emojis from text
    """
    return emoji.replace_emoji(text, replace='')


def extract_text_content(message):
    """
    Extract text content from a message, cleaned of emojis, extra spaces and media files
    """
    if 'text' in message:
        if isinstance(message['text'], str):
            return remove_emojis(message['text'].strip())
        elif isinstance(message['text'], list):
            text_parts = ''.join(part for part in message['text'] if isinstance(part, str))
            return remove_emojis(text_parts.strip()) if text_parts.strip() else None

    elif 'media_type' in message and message['media_type'] == 'sticker':
        return '[стикер]'

    elif 'media_type' in message:
        return f'[{message["media_type"]}]'
    return None


def process_messages(list_messages, from_user_id, response_key, reply_key):
    """
    Retrieves user messages by user_id
    """
    chat = []
    i = 0
    from_user_id_prefixed = f"user{from_user_id}"

    while i < len(list_messages):
        message = list_messages[i]

        if message.get('from_id') != from_user_id_prefixed and 'text' in message:
            text_content = extract_text_content(message)
            if text_content is None:
                i += 1
                continue

            response = {response_key: text_content, "input": ""}
            i += 1

            replies = []
            while i < len(list_messages) and list_messages[i].get('from_id') == from_user_id_prefixed:
                reply_text = extract_text_content(list_messages[i])
                if reply_text:
                    replies.append(reply_text.strip())
                i += 1

            if replies:
                response[reply_key] = '. '.join(replies).strip()
                chat.append(response)
        else:
            i += 1

    return chat


def path_to_messages(data, from_user_id):
    """
    Retrieves user's messages from all necessary chats
    """
    print(f"Extracting messages for user {from_user_id}")

    messages = []
    for chat in data.get('chats', {}).get('list', []):
        if chat['type'] != 'saved_messages':
            chat_messages = process_messages(
                chat['messages'],
                from_user_id=from_user_id,
                response_key='instruction',
                reply_key='output'
            )
            messages.extend(chat_messages)

    print(f"Found {len(messages)} messages")
    return messages


async def take_messages(user_id, file_path):
    """
    Analyzes communication style and saves keywords
    """
    data = load_data(file_path)
    print(f"Processing messages for user_id: {user_id}")

    json_data_messages = path_to_messages(data, from_user_id=user_id)
    print('обработаны')

    if json_data_messages:
        messages_file_path = os.path.join(os.path.dirname(file_path), 'messages.json')
        save_data(json_data_messages, messages_file_path)
        print(f"messages.json сохранен по пути: {messages_file_path}")
        print(f"Сохранено {len(json_data_messages)} пар сообщений")

        process_messages_file(user_id)

        filtered_file_path = os.path.join("results", str(user_id), "filtered_messages.json")
        style_keywords = analyze_style(filtered_file_path, top_n=200)

        if style_keywords:
            style_keywords_file = os.path.join("results", str(user_id), "style_keywords.json")
            with open(style_keywords_file, "w", encoding="utf-8") as f:
                json.dump(style_keywords, f, ensure_ascii=False, indent=4)
            print(f"Анализ стиля завершен. Ключевые слова сохранены в файл: {style_keywords_file}")
        else:
            print("Анализ стиля не дал результатов")
    else:
        print("No messages to save")


def process_messages_file(user_id):
    """
    Combines empty messages from the messages.json file
    """
    user_folder = os.path.join("results", str(user_id))
    input_file = os.path.join(user_folder, "messages.json")
    output_file = os.path.join(user_folder, "filtered_messages.json")

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = []
    accumulated_output = ""

    for item in data:
        instruction = item["instruction"]
        output = item["output"]

        if instruction:
            item["output"] = accumulated_output + output if accumulated_output else output
            accumulated_output = ""
            result.append(item)
        else:
            accumulated_output += output if output else ""

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"Обработка завершена. Данные сохранены в '{output_file}'")