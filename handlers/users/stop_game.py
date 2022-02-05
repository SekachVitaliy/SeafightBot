from aiogram import types
from aiogram.dispatcher.filters.builtin import Command
from aiogram.dispatcher.storage import FSMContext

from filters.private_chat import IsPrivate
from keyboards.inline.start_keyboard import inline_start_keyboard
from loader import db, dp
from states.game import Game
from utils.misc import rate_limit


@rate_limit(limit=1)
@dp.message_handler(Command("stop"), IsPrivate())
@dp.message_handler(Command("stop"), IsPrivate(), state=Game.not_started)
@dp.message_handler(Command("stop"), IsPrivate(), state=Game.withdraw)
@dp.message_handler(Command("stop"), IsPrivate(), state=Game.pay)
async def bot_start(message: types.Message):
    """
        Хендлер куда попадает команда  stop '/stop'
    """
    await Game.not_started.set()
    await message.answer("У тебя нет активной игры!\nДавай сыграем ?)", reply_markup=inline_start_keyboard)


@rate_limit(limit=1)
@dp.message_handler(Command("stop"), IsPrivate(), state=Game.game)
async def bot_start(message: types.Message, state: FSMContext):
    """
        Хендлер куда попадает команда  stop '/stop'
    """
    await Game.not_started.set()
    await message.answer("Игра остановлена, сыграем еще ?", reply_markup=inline_start_keyboard)
