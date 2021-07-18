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
    Эхо хендлер, куда летят ВСЕ сообщения без состояния
    Использовался для проверки
    """
    await message.answer(text="Ты в игре! Используй команду"
                              " /stop что бы выйти", reply_markup=types.ReplyKeyboardRemove())


# @rate_limit(limit=1)
# @dp.message_handler(IsPrivate(), state="*", content_types=types.ContentTypes.ANY)
# async def bot_echo_all(message: types.Message, state: FSMContext):
#     """
#     Эхо хендлер, куда летят ВСЕ сообщения с указанным состоянием
#     Использовался для проверки
#     """
#     state = await state.get_state()
#     await message.answer(f"Эхо в состоянии <code>{state}</code>.\n"
#                          f"\nСодержание сообщения:\n"
#                          f"<code>{message}</code>")
