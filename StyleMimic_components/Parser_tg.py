import json
from pathlib import Path


def load_data(filename):
    path = Path(filename)
    data = json.loads(path.read_text(encoding='utf-8'))
    return data


def save_data(data):
    with open('messages.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def path_to_messages(data):
    chats = {}
    for teg in data:
        if teg == 'chats':
            for chat in data[teg]['list']:
                if chat['type'] != 'saved_messages':
                    small_data = edit_json_file(chat['messages'])
                    if small_data:
                        chats[chat['name']] = small_data
    return chats


def edit_json_file(list_messages):
    if len(list_messages) != 0:
        # need_keys = ['date', 'from', 'text']
        chat = []
        for message in list_messages:
            if 'date' in message and 'from' in message and 'text' in message:
                small_data = {'date': message['date'], 'from': message['from'], 'text': message['text']}
                if len(message['text']) != 0 and small_data not in chat and type(message['text']) == str:
                    chat.append(small_data)
        return chat


def take_messages():
    filename = 'result.json'

    data = load_data(filename)
    json_data_messages = path_to_messages(data)
    if json_data_messages:
        save_data(json_data_messages)


if __name__ == "__main__":
    take_messages()
