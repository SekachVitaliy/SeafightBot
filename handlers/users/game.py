from aiogram import types

from filters import IsPrivate, InField
from keyboards.inline.start_keyboard import inline_start_keyboard
from keyboards.default.default_field_keyboard import get_default_keyboard
from loader import dp, db
from utils.misc import rate_limit
from .start import change_image, draw_lines
from states.game import Game


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), InField())
async def parsing_the_keyboard(message: types.Message):
    """
    Хендлер срабатвает по кнопке с клавиатуры. Фильтр InField пропускает только кнопки с клавиатуры, вне игры.
    Отрисовывает поле куда стреляли и отправляет изображение обратно с клавиатурой
    """
    await message.answer("У тебя нет активной игры!\nДавай сыграем ?)", reply_markup=inline_start_keyboard)


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), text='🔴', state=Game.game)
async def parsing_the_keyboard(message: types.Message):
    shots = await db.get_shots_arr(message.chat.id)
    await message.answer("Ты сюда уже стрелял, попробуй в другое место)", reply_markup=get_default_keyboard(shots))


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), text='❌', state=Game.game)
async def parsing_the_keyboard(message: types.Message):
    shots = await db.get_shots_arr(message.chat.id)
    await message.answer("Ты сюда уже стрелял, попробуй в другое место)", reply_markup=get_default_keyboard(shots))


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), InField(), state=Game.game)
async def parsing_the_keyboard(message: types.Message):
    """
    Хендлер срабатвает по кнопке с клавиатуры. Фильтр InField пропускает только кнопки с клавиатуры в игре.
    Отрисовывает поле куда стреляли и отправляет изображение обратно с клавиатурой
    """
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    i = int(alphabet.index(message.text[0]))
    j = int(message.text[1])
    # Получаем массив кораблей
    ships = await db.get_ships_arr(message.from_user.id)
    # Получаем массив выстрелов, что бы передать в клавиатуру
    shot_field = await db.get_shots_arr(message.from_user.id)
    if ships[i][j] > 0:
        shot_field[i][j] = 0
    else:
        shot_field[i][j] = 1
    shots = change_image(i, j, ships, shot_field, message.from_user.id)
    # Сохраняем выстрелы
    await db.fill_shots_arr(shots, message.chat.id)
    summa = 0
    for i in range(len(shots)):
        summa += shots[i].count(0)
    if summa != 20:
        draw_lines(message.chat.id)
        await message.answer_photo(types.InputFile(f'{message.chat.id}.jpg'), reply_markup=get_default_keyboard(shots))
    else:
        draw_lines(message.chat.id)
        await message.answer_photo(types.InputFile(f'{message.chat.id}.jpg'))
        await message.answer("Ты победил)) Прими мои поздравления!!!!")
        await message.answer("Давай сыграем еще разок ?)", reply_markup=inline_start_keyboard)
