import random
from aiogram import types
from PIL import Image, ImageDraw
from aiogram.types import InputFile

from filters import IsPrivate
from keyboards.default.default_field_keyboard import get_default_keyboard
from utils.misc import rate_limit
from loader import dp, db


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), text="map")
async def show_map(message: types.Message):
    """
    Ловит сообщение 'map' и генериурет поле и отссылает изображение поля и клавиатуру
    """
    """
    Стаарый вывод поля с кораблями
    red_circle = '🔴'
    blue_circle = '🔵'
    cross = '❌'
    n = 10
    out = 'Карта врага:\n'
    arr = generate_enemy_ships()
    for line in arr:
        for i in range(0, n):
            if line[i] >= 1:
                out += cross
            else:
                out += blue_circle
        out += '\n'
    """
    arr = generate_enemy_ships()
    # записываем сгенерируемый массив кораблей в базу данных
    await db.fill_ships_arr(arr, telegram_id=message.from_user.id)
    # генерируем массив выстрелов в базе данных( -1 для всех, что значит что мы еще не стреляли туда)
    await db.fill_shots_arr(telegram_id=message.from_user.id)
    # рисуем изображение поля
    draw_field(arr, message.from_user.id)
    # получаем массив выстрелов и передаем его в клавиатуру
    shots = await db.get_shots_arr(message.from_user.id)
    await message.answer_photo(InputFile(f'{message.chat.id}.jpg'), reply_markup=get_default_keyboard(shots))


def generate_enemy_ships():
    """
    Функция генерации массива кораблей, возращает массив кораблей [10][10]
    """
    enemy_ships = [[]]
    ships_list = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
    sum_all_ships = sum(ships_list)
    sum_all_enemy = 0
    quantity_x, quantity_y = 10, 10
    while sum_all_enemy != sum_all_ships:
        # обнуляю масив кораблів
        enemy_ships = [[0 for _ in range(quantity_x + 1)] for _ in
                       range(quantity_y + 1)]  # +1 для додаткової ліній справа і знизу,
        # щоб успішної перевірок генерації кораблів
        for i in range(0, 10):
            length = ships_list[i]
            horizont_vertikal = random.randrange(1, 3)  # 1- горизонтальне  2 - вертикальне

            coordinate_on_x = random.randrange(0, quantity_x)
            if coordinate_on_x + length > quantity_x:
                coordinate_on_x = coordinate_on_x - length

            coordinate_on_y = random.randrange(0, quantity_y)
            if coordinate_on_y + length > quantity_y:
                coordinate_on_y = coordinate_on_y - length

            if horizont_vertikal == 1:
                if coordinate_on_x + length <= quantity_x:
                    for j in range(0, length):
                        try:
                            check_near_ships = enemy_ships[coordinate_on_y][coordinate_on_x - 1] + \
                                               enemy_ships[coordinate_on_y][coordinate_on_x + j] + \
                                               enemy_ships[coordinate_on_y][coordinate_on_x + j + 1] + \
                                               enemy_ships[coordinate_on_y + 1][coordinate_on_x + j + 1] + \
                                               enemy_ships[coordinate_on_y - 1][coordinate_on_x + j + 1] + \
                                               enemy_ships[coordinate_on_y + 1][coordinate_on_x + j] + \
                                               enemy_ships[coordinate_on_y - 1][coordinate_on_x + j] + \
                                               enemy_ships[coordinate_on_y + 1][coordinate_on_x - j - 1] + \
                                               enemy_ships[coordinate_on_y - 1][coordinate_on_x - j - 1]
                            if check_near_ships == 0:  # записую в тому випадку, якщо немає нічого поряд
                                enemy_ships[coordinate_on_y][coordinate_on_x + j] = i + 1  # записую номер корабля
                        except Exception:
                            pass
            if horizont_vertikal == 2:
                if coordinate_on_y + length <= quantity_y:
                    for j in range(0, length):
                        try:
                            check_near_ships = enemy_ships[coordinate_on_y - 1][coordinate_on_x] + \
                                               enemy_ships[coordinate_on_y + j][coordinate_on_x] + \
                                               enemy_ships[coordinate_on_y + j + 1][coordinate_on_x] + \
                                               enemy_ships[coordinate_on_y + j + 1][coordinate_on_x + 1] + \
                                               enemy_ships[coordinate_on_y + j + 1][coordinate_on_x - 1] + \
                                               enemy_ships[coordinate_on_y - j - 1][coordinate_on_x + 1] + \
                                               enemy_ships[coordinate_on_y - j - 1][coordinate_on_x - 1] + \
                                               enemy_ships[coordinate_on_y + j][coordinate_on_x + 1] + \
                                               enemy_ships[coordinate_on_y + j][coordinate_on_x - 1]
                            if check_near_ships == 0:
                                enemy_ships[coordinate_on_y + j][coordinate_on_x] = i + 1
                        except Exception:
                            pass
        # делаем подсчет кораблей
        sum_all_enemy = 0
        for i in range(0, quantity_x):
            for j in range(0, quantity_y):
                if enemy_ships[j][i] > 0:
                    sum_all_enemy = sum_all_enemy + 1
    return enemy_ships[:10][:10]


def draw_field(arr, chat_id):
    """
    Эта функция генерирует изображения поля 500х500
    """
    photo_height = 500
    photo_width = 500
    quantity = 10
    step = photo_height // quantity
    img = Image.new('RGB', (photo_width, photo_height), 'blue')
    draw = ImageDraw.Draw(img)
    for i in range(0, quantity):
        for j in range(0, quantity):
            if arr[i][j] > 0:
                # зарисовуем клеточки, где находятся корабли
                draw.rectangle((j * step + 2, i * step + 2, j * step + 48, i * step + 48), fill='white')
    for i in range(0, quantity):
        # рисуем поле черными линиями
        draw.line((step * i, 0, step * i, photo_height), fill='black', width=2)
        draw.line((0, step * i, photo_width, step * i), fill='black', width=2)
    # сохраняем изображние по имени id в телеграм
    img.save(f'{chat_id}.jpg', quality=95)


def change_image(i, j, chat_id):
    """
    Функция закрашивает клеточку куда стреляли
    """
    step = 50
    img = Image.open(f'{chat_id}.jpg')
    draw = ImageDraw.Draw(img)
    # 48 потому что бы не залазило на черные линии
    draw.rectangle((j * step + 2, i * step + 2, j * step + 48, i * step + 48), fill='red')
    # сохраняем изображние по имени id в телеграм
    img.save(f'{chat_id}.jpg', quality=95)
