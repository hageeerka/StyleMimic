import json


path_messages1 = 'messages.json'
path_train = 'example_train.json'


with open(path_messages1, 'r', encoding='utf-8') as file:
    messages_data = json.load(file)


formatted_data = []
for user, conversations in messages_data.items():
    for conversation in conversations:

        if "output" in conversation and conversation["output"].strip():
            formatted_data.append({
                "instruction": conversation["input"],
                "input": "",
                "output": conversation["output"]
            })


with open(path_train, 'w', encoding='utf-8') as file:
    json.dump(formatted_data, file, ensure_ascii=False, indent=4)

print(f"Data successfully transformed and saved to {path_train}")
