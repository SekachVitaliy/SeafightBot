import logging
import time

from aiogram import executor

import filters
import handlers
import middlewares
from loader import db, dp
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Подключаем базу данных
    logging.info("Создаем подключение к базе данных")
    while True:
        try:
            await db.create_pool()
            break
        except ConnectionRefusedError:
            logging.info('database connection refused, retrying in 5 seconds...')
            time.sleep(5)
    await db.drop_table_users()
    logging.info("Создаем таблицу пользователей")
    while True:
        try:
            await db.create_table_users()
            break
        except ConnectionRefusedError:
            logging.info('database connection refused, retrying in 5 seconds...')
            time.sleep(5)
    logging.info("Готово")

    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляет про запуск
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
