import random
from aiogram import types
from PIL import Image, ImageDraw
from aiogram.types import InputFile

from filters import IsPrivate
from keyboards.default.default_field_keyboard import default_field
from utils.misc import rate_limit
from loader import dp


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), text="map")
async def show_map(message: types.Message):
    # red_circle = '🔴'
    # blue_circle = '🔵'
    # cross = '❌'
    # n = 10
    # out = 'Карта врага:\n'
    # arr = generate_enemy_ships()
    # for line in arr:
    #     for i in range(0, n):
    #         if line[i] >= 1:
    #             out += cross
    #         else:
    #             out += blue_circle
    #     out += '\n'
    paint_image(message.chat.id)
    await message.answer_photo(InputFile(f'{message.chat.id}.jpg'), reply_markup=default_field)


def generate_enemy_ships():
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
    return enemy_ships


def paint_image(chat_id):
    photo_height = 500
    photo_width = 500
    quantity = 10  # кількість клітинок по вертикалі і горизонталі
    step = photo_height // quantity  # крок по горизонталі
    img = Image.new('RGB', (photo_width, photo_height), 'blue')
    draw = ImageDraw.Draw(img)
    arr = generate_enemy_ships()
    for i in range(0, quantity):
        for j in range(0, quantity):
            if arr[i][j] > 0:
                draw.rectangle((j * step + 2, i * step + 2, j * step + 48, i * step + 48), fill='white')
    for i in range(0, quantity):
        draw.line((step * i, 0, step * i, photo_height), fill='black', width=2)
        draw.line((0, step * i, photo_width, step * i), fill='black', width=2)
    img.save(f'{chat_id}.jpg', quality=95)


def change_image(i, j, chat_id):
    step = 50
    img = Image.open(f'{chat_id}.jpg')
    draw = ImageDraw.Draw(img)
    draw.rectangle((j * step + 2, i * step + 2, j * step + 48, i * step + 48), fill='red')
    img.save(f'{chat_id}.jpg', quality=95)
