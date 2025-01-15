"""
Bot configuration.

By default, will obtain required fields from environment variables,
but you can override that with modifying defaults.

RU: Используйте переменные окружения или поменяйте default полей
"""

import os

# Telegram token obtained from Bot Father
TELEGRAM_TOKEN = "BOT_TOKEN"

# First message that will be sent to model as it was user.
# If left blank or None will do not perform this operation.
START_USER_MESSAGE = ""

# Translator module, change from default `en` to something like `ru` to perform translation on user messages.
BASE_LANGUAGE = "ru"

# Ollama server configuration
OLLAMA_API_HOST = os.getenv("OLLAMA_API_HOST", default="http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_BOT_MODEL", default="ilyagusev/saiga_nemo_12b")
OLLAMA_MODEL_TEMPERATURE = 1
OLLAMA_KEEP_ALIVE = "5m"
# TODO: OLLAMA_INSTALL_MISSING_MODELS
