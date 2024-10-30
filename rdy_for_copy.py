import json


def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)


def save_data(data, filename='messages.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def extract_text_content(message):
    """
    Extracts text content only, ignoring other data like links or custom emojis.
    """
    if isinstance(message['text'], str):
        return message['text']
    elif isinstance(message['text'], list):
        return ''.join(part for part in message['text'] if isinstance(part, str))


def edit_json_file(list_messages):
    chat, accumulated_input = [], []

    for i, message in enumerate(list_messages):
        if message.get('from') != "Ivan 🍅 Kostin" and 'text' in message:
            text_content = extract_text_content(message)
            if not text_content:
                continue

            response = {'input': text_content}
            next_message = list_messages[i + 1] if i + 1 < len(list_messages) else {}

            if next_message.get('from') == "Ivan 🍅 Kostin":
                reply_text = extract_text_content(next_message)
                if reply_text:
                    response['output'] = reply_text

            if 'output' in response:
                response['input'] = '.'.join(accumulated_input) + '.' + response['input'] if accumulated_input else \
                response['input']
                accumulated_input.clear()
                chat.append(response)
            else:
                accumulated_input.append(text_content)

    if accumulated_input:
        chat.append({'input': '.'.join(accumulated_input)})

    return chat


def path_to_messages(data):
    return {
        chat['name']: edit_json_file(chat['messages'])
        for chat in data.get('chats', {}).get('list', [])
        if chat['type'] != 'saved_messages'
    }


def take_messages(filename='result.json'):
    data = load_data(filename)
    json_data_messages = path_to_messages(data)
    if json_data_messages:
        save_data(json_data_messages)


if __name__ == "__main__":
    take_messages()
