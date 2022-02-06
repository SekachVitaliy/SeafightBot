from aiogram import types
from aiogram.dispatcher import FSMContext

from filters import IsPrivate
from loader import dp
from states import Game
from utils.misc import rate_limit


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), state=Game.game)
async def bot_echo(message: types.Message):
    """
    Эхо хендлер, куда летят ВСЕ сообщения c игры, если не попало в другие хендлеры
    """
    await message.answer(text="Ты в игре! Используй команду"
                              " /stop что бы выйти", reply_markup=types.ReplyKeyboardRemove())


@rate_limit(limit=1)
@dp.message_handler(IsPrivate())
async def bot_echo_all(message: types.Message):
    """
    Эхо хендлер, куда летят ВСЕ сообщения с указанным состоянием
    Использовался для проверки
    """
    await message.answer(f"Выбери правильную команду).")
