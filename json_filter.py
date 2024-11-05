import json

# Открываем и читаем файл
with open("messages.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Результирующий список
result = []
accumulated_output = ""  # Переменная для накопления output

# Обработка элементов
for item in data:
    instruction = item["instruction"]
    output = item["output"]

    if instruction:  # Если instruction не пустой
        # Добавляем накопленный output к текущему элементу и сбрасываем накопитель
        item["output"] = accumulated_output + output if accumulated_output else output
        accumulated_output = ""
        result.append(item)  # Добавляем элемент в результат
    else:
        # Накопление output для пустых instruction
        accumulated_output += output if output else ""

# Запись обработанных данных в новый файл
with open("filtred_messages.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print("Обработка завершена. Данные сохранены в 'processed_messages.json'")