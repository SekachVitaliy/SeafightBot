from aiogram import types

from filters import IsPrivate, InField
from keyboards.default.default_field_keyboard import get_default_keyboard
from loader import dp, db
from .start import change_image
from states.game import Game


@dp.message_handler(IsPrivate(), InField(), state=Game.game)
async def parsing_the_keyboard(message: types.Message):
    """
    Хендлер срабатвает по кнопке с клавиатуры. Фильтр InField пропускает только кнопки с клавиатуры.
    Отрисовывает поле куда стреляли и отправляет изображение обратно с клавиатурой
    """
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    i = int(alphabet.index(message.text[0]))
    j = int(message.text[1])
    # Зарисовуем поле, куда стреляли
    change_image(i, j, message.from_user.id)
    # Записываем  данные в ячейку БД, куда стреляли
    await db.fill_shots_cell(i, j, 1, message.from_user.id)
    # Получаем массив выстрелов, что бы передать в клавиатуру
    arr = await db.get_shots_arr(message.from_user.id)
    await message.answer_photo(types.InputFile(f'{message.chat.id}.jpg'), reply_markup=get_default_keyboard(arr))
