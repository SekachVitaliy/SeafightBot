from aiogram import types

from filters import IsPrivate, InField
from keyboards.default.default_field_keyboard import default_field
from loader import dp
from utils.misc import rate_limit
from .map import change_image


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), InField())
async def parsing_the_keyboard(message: types.Message):
    """
    Хендлер срабатвает по кнопке с клавиатуры. Фильтр InField пропускает только кнопки с клавиатуры.
    Отрисовывает поле куда стреляли и отправляет изображение обратно с клавиатурой
    """
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    change_image(int(alphabet.index(message.text[0])), int(message.text[1]), message.chat.id)
    await message.answer_photo(types.InputFile(f'{message.chat.id}.jpg'), reply_markup=default_field)
