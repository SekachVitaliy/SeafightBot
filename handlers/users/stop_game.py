from aiogram import types
from aiogram.dispatcher.filters.builtin import Command
from aiogram.dispatcher.storage import FSMContext


from keyboards.inline.start_keyboard import inline_start_keyboard
from filters.private_chat import IsPrivate
from utils.misc import rate_limit
from states.game import Game
from loader import dp, db


@rate_limit(limit=1)
@dp.message_handler(Command("stop"), IsPrivate())
async def bot_start(message: types.Message):
    """
        Хендлер куда попадает команда  stop '/stop'
    """
    await message.answer("У тебя нет активной игры!\nДавай сыграем ?)", reply_markup=inline_start_keyboard)


@rate_limit(limit=1)
@dp.message_handler(Command("stop"), IsPrivate(), state=Game.game)
async def bot_start(message: types.Message, state: FSMContext):
    """
        Хендлер куда попадает команда  stop '/stop'
    """
    await message.answer("Игра остановлена, сыграем еще ?", reply_markup=inline_start_keyboard)
    await state.reset_state()
