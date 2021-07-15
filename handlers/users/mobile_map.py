from aiogram import types

from filters import IsPrivate
from keyboards.inline.inline_field_keyboard import inline_field
from utils.misc import rate_limit
from loader import dp


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), text="Map")
async def show_map(message: types.Message):
    """
    Хендлер работает по слову 'Map', для проверки вывода без смайликов и без изображенгие
    Инлайн клавиатура чисто для проверки, использовать будем дефолтную 
    """
    red_circle = '▓'
    blue_circle = '▒'
    cross = 'X'
    n = 10
    # out = 'Карта врага:\n'
    out = ''
    arr = [[0 for i in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i < j:
                arr[i][j] = -1
            elif i > j:
                arr[i][j] = 1
            else:
                arr[i][j] = 0
    for line in arr:
        for i in range(0, n):
            if line[i] == -1:
                out += blue_circle
            elif line[i] == 1:
                out += cross
            elif line[i] == 0:
                out += red_circle
        out += '\n'
    await message.answer(out, reply_markup=inline_field)
