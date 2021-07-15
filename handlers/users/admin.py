from aiogram import types

from data.config import ADMINS
from filters import IsPrivate
from utils.misc import rate_limit
from loader import dp


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), user_id=ADMINS, text="admin")
async def admin_chat(message: types.Message):
    await message.answer(f"Ты вызвал админку!")
