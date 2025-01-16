from aiogram import Bot, Dispatcher


from bot.settings import TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)

dp = Dispatcher()
