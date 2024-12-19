from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from accelerate import infer_auto_device_map
from peft import prepare_model_for_kbit_training
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# загрузка токенайзера
model_name = "IlyaGusev/saiga_nemo_12b"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# загрузка модели с 8-битным квантованием
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",          # автоматическое распределение по устройствам
    torch_dtype=torch.float16,
    load_in_8bit=True
)

model = prepare_model_for_kbit_training(model)

print("Model loaded with 8-bit quantization.")

# истории диалогов для каждого пользователя
user_dialogs = {}

# генерация ответа
def generate_response(user_id: int, input_text: str) -> str:
    global user_dialogs

    if user_id not in user_dialogs:
        user_dialogs[user_id] = []

    # с системным промптом нужно будет погиграться + прикрепить скрипт с выделе
    system_prompt = "Ты — бот, который отвечает на вопросы четко и информативно. Вот ваш диалог:"

    user_dialogs[user_id].append(f"Пользователь: {input_text}")
    context = f"{system_prompt}\n" + "\n".join(user_dialogs[user_id][-10:]) + "\nБот:"
    inputs = tokenizer(context, return_tensors="pt", truncation=True, max_length=512).to(model.device)
    if "token_type_ids" in inputs:
        del inputs["token_type_ids"]

    outputs = model.generate(
        **inputs,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.6,  # креативность ответа [0,1]
        top_p=0.95,  # разнообразие генерируемых токенов [0,1]
        eos_token_id=tokenizer.eos_token_id
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Удаляем системный промпт и добавляем ответ в историю
    response_cleaned = response.replace(system_prompt, "").split("\nБот:")[-1].strip()

    # ограничение на длину ответа до 512 символов
    response_cleaned = response_cleaned[:512]

    user_dialogs[user_id].append(f"Бот: {response_cleaned}")

    # ограничение на длину диалога: 20 сообщений
    if len(user_dialogs[user_id]) > 20:
        user_dialogs[user_id] = user_dialogs[user_id][-20:]

    return response_cleaned


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я бот на базе модели Saiga. Задайте мне вопрос!")


# обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    user_id = update.message.from_user.id  # получение айди пользователя
    print(f"Received user input: {user_input} from user {user_id}")
    try:
        response = generate_response(user_id, user_input)
        print(f"Generated response: {response}")
        await update.message.reply_text(response)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте еще раз.")


def main():
    TOKEN = "7648104021:AAHM5l-EY-lVdTzlPZBbAJo0_LhuIctUwPE"

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == "__main__":
    main()
