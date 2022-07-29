import asyncio

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging
import os
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram import Bot, types

TOKEN = os.getenv('BOT_TOKEN')
print(TOKEN)
service_bot = Bot(token='5493235478:AAHGDhBrc1JZE0S3fQoy0Vfpmz3np6Ejoa0')
print(service_bot)
client_bot = Bot(token='5444500594:AAE92u7a7mT2fWDFhSXRA8qs7eDpVP0ovZM')
dp = Dispatcher(client_bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
WEBAPP_HOST = '0.0.0.0'
DEFAULT_PORT = 5000
# WEBAPP_PORT = int(os.getenv('PORT'), DEFAULT_PORT)
WEBAPP_PORT = os.getenv('PORT', default=8000)


if not TOKEN:
    print('You have forgot to set BOT_TOKEN')
    quit()

