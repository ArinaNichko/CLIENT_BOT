import asyncio

from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging
import os
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram import Bot, types


BOT_TOKEN = '5444500594:AAE92u7a7mT2fWDFhSXRA8qs7eDpVP0ovZM'
print(BOT_TOKEN)
service_bot = Bot(token='5493235478:AAHGDhBrc1JZE0S3fQoy0Vfpmz3np6Ejoa0')
print(service_bot)
client_bot = Bot(token='5444500594:AAE92u7a7mT2fWDFhSXRA8qs7eDpVP0ovZM')
dp = Dispatcher(client_bot)
dp.middleware.setup(LoggingMiddleware())



# webhook settings
WEBHOOK_HOST = 'https://bot-for-work-kyiv.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
WEBAPP_HOST = '0.0.0.0'
DEFAULT_PORT = 5000
# WEBAPP_PORT = int(os.getenv('PORT'), DEFAULT_PORT)
WEBAPP_PORT = os.getenv('PORT', default=8000)


if not BOT_TOKEN:
    print('You have forgot to set BOT_TOKEN')
    quit()


async def on_startup(dp):
    await client_bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await client_bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')

print(WEBHOOK_PATH)
if __name__ == '__main__':

    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )