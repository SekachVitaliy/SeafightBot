from aiogram import types
from aiogram.dispatcher.filters.builtin import Command

from filters.private_chat import IsPrivate
from utils.misc import rate_limit

from loader import dp, db


@rate_limit(limit=1)
@dp.message_handler(Command("stop"), IsPrivate())
async def bot_start(message: types.Message):
    """
        Хендлер куда попадает команда  stop '/stop'
    """
    await message.answer("Игра остановлена, начните заного")
