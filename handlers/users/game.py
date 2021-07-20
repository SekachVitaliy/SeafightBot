from aiogram import types

from filters import IsPrivate, InField
from keyboards.inline.start_keyboard import inline_start_keyboard
from keyboards.default.default_field_keyboard import get_default_keyboard
from loader import dp, db
from utils.misc import rate_limit
from .start import change_image
from states.game import Game


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), InField())
async def parsing_the_keyboard(message: types.Message):
    """
    Хендлер срабатвает по кнопке с клавиатуры. Фильтр InField пропускает только кнопки с клавиатуры, вне игры.
    Отрисовывает поле куда стреляли и отправляет изображение обратно с клавиатурой
    """
    await message.answer("У тебя нет активной игры!\nДавай сыграем ?)", reply_markup=inline_start_keyboard)


@dp.message_handler(IsPrivate(), InField(), state=Game.game)
async def parsing_the_keyboard(message: types.Message):
    """
    Хендлер срабатвает по кнопке с клавиатуры. Фильтр InField пропускает только кнопки с клавиатуры в игре.
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
