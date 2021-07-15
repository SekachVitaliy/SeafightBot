from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from filters import IsPrivate
from utils.misc import rate_limit
from loader import dp


@rate_limit(limit=1)
@dp.message_handler(CommandHelp(), IsPrivate())
async def bot_help(message: types.Message):
    text = ("Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку")

    await message.answer("\n".join(text))
