from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from filters import IsPrivate
from loader import dp
from states import Game
from utils.misc import rate_limit


@rate_limit(limit=1)
@dp.message_handler(CommandHelp(), IsPrivate())
async def bot_help(message: types.Message):
    """
    Хендлер куда попадает команда '/help' и выводит список доступных команд
    """
    text = ("Список команд: ",
            "/start - Начать диалог",
            "/stop - Останавливает игру",
            "/help - Получить справку")

    await message.answer("\n".join(text))


@rate_limit(limit=1)
@dp.message_handler(CommandHelp(), IsPrivate(), state=Game.game)
@dp.message_handler(CommandHelp(), IsPrivate(), state=Game.pay)
@dp.message_handler(CommandHelp(), IsPrivate(), state=Game.withdraw)
@dp.message_handler(CommandHelp(), IsPrivate(), state=Game.not_started)
async def bot_help(message: types.Message):
    """
    Хендлер куда попадает команда '/help' и выводит список доступных команд
    """
    text = ("Список команд: ",
            "/start - Начать диалог",
            "/stop - Останавливает игру",
            "/help - Получить справку")

    await message.answer("\n".join(text))