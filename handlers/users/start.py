from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from filters.private_chat import IsPrivate
from utils.misc import rate_limit

from loader import dp


@rate_limit(limit=1)
@dp.message_handler(CommandStart(deep_link="reklama"), IsPrivate())
async def bot_start_deeplink(message: types.Message):
    """
    Хендлер куда попадает команда  start с диплинком  '/start  123'
    """
    await message.answer(f"Привет, {message.from_user.full_name}, ты перешел по реферальной ссылке)")


@rate_limit(limit=1)
@dp.message_handler(CommandStart(), IsPrivate())
async def bot_start(message: types.Message):
    """
        Хендлер куда попадает команда  start '/start'
    """
    await message.answer(f"Привет, {message.from_user.full_name}!")
