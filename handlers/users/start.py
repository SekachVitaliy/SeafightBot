import logging
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from filters.private_chat import IsPrivate
from utils.misc import rate_limit
from asyncpg.exceptions import UniqueViolationError

from loader import dp, db


@rate_limit(limit=1)
@dp.message_handler(CommandStart(deep_link="reklama"), IsPrivate())
async def bot_start_deeplink(message: types.Message):
    """
    Хендлер куда попадает команда  start с диплинком  '/start  reklama'
    """
    try:
        # Добавляем пользователя в БД
        user = await db.add_user_with_balance(
            full_name=message.from_user.full_name,
            username=message.from_user.username,
            telegram_id=message.from_user.id,
            balance=100
        )
        logging.info(f"Добавлен новый пользователь: Fullname={user[1]}, username={user[2]}, telegram_id={user[3]}"
                     f"balance={user[4]}, количество:{await db.count_users()}")
    except UniqueViolationError:
        # Если пользователь уже есть в БД
        user = await db.select_user(telegram_id=message.from_user.id)
    await message.answer(f"Привет, {message.from_user.full_name}, ты перешел по реферальной ссылке)")


@rate_limit(limit=1)
@dp.message_handler(CommandStart(), IsPrivate())
async def bot_start(message: types.Message):
    """
        Хендлер куда попадает команда  start '/start'
    """
    try:
        # Добавляем пользователя в БД
        user = await db.add_user(
            full_name=message.from_user.full_name,
            username=message.from_user.username,
            telegram_id=message.from_user.id
        )
        logging.info(f"Добавлен новый пользователь: Fullname={user[1]}, username={user[2]}, telegram_id={user[3]}"
                     f"balance={user[4]}, количество:{await db.count_users()}")
    except UniqueViolationError:
        # Если пользователь уже есть в БД
        user = await db.select_user(telegram_id=message.from_user.id)
    await message.answer(f"Привет, {message.from_user.full_name}!")
