import logging
from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters.builtin import CommandStart

from filters.private_chat import IsPrivate
from keyboards.inline.start_keyboard import inline_start_keyboard
from keyboards.default.default_field_keyboard import get_default_keyboard
from states import Game
from utils.misc import rate_limit
from asyncpg.exceptions import UniqueViolationError

import random
from PIL import Image, ImageDraw
from aiogram.types import InputFile

from loader import dp, db

click = 35
ship_5 = 0
ship_6 = 0
ship_7 = 0
ship_8 = 0
ship_9 = 0
ship_10 = 0


@rate_limit(limit=1)
@dp.message_handler(CommandStart(deep_link="reklama"), IsPrivate())
async def bot_start_deeplink(message: types.Message):
    """
    Хендлер куда попадает команда  start с диплинком  '/start  reklama'
    """
    try:
        # Добавляем пользователя в БД
        user = await db.add_user_with_balance(
            full_name=message.from_user.full_name,
            username=message.from_user.username,
            telegram_id=message.from_user.id,
            balance=100
        )
        logging.info(f"Добавлен новый пользователь: Fullname={user[1]}, username={user[2]}, telegram_id={user[3]}, "
                     f"balance={user[4]}, количество:{await db.count_users()}")
    except UniqueViolationError:
        # Если пользователь уже есть в БД
        user = await db.select_user(telegram_id=message.from_user.id)
    await message.answer(f"Привет, {message.from_user.full_name}, ты перешел по реферальной ссылке)")


@rate_limit(limit=1)
@dp.message_handler(CommandStart(), IsPrivate())
async def bot_start(message: types.Message):
    """
        Хендлер куда попадает команда  start '/start'
    """
    try:
        # Добавляем пользователя в БД
        user = await db.add_user(
            full_name=message.from_user.full_name,
            username=message.from_user.username,
            telegram_id=message.from_user.id
        )
        logging.info(f"Добавлен новый пользователь: Fullname={user[1]}, username={user[2]}, telegram_id={user[3]}, "
                     f"balance={user[4]}, количество:{await db.count_users()}")
    except UniqueViolationError:
        # Если пользователь уже есть в БД
        user = await db.select_user(telegram_id=message.from_user.id)
    text = f"Привет, {message.from_user.full_name}!\nЕсть бесплатная и платная версии, платная версия стоит 10," \
           f"\nкогда выигрываешь получаешь 20)\nДавай сыграем ?) "
    await message.answer(text, reply_markup=inline_start_keyboard)


@rate_limit(limit=1)
@dp.callback_query_handler(text="paid")
async def paid_game(call: CallbackQuery):
    # убираем часиви возле кнопки
    await call.answer(cache_time=60)
    # удаляем клавиатуру
    await call.message.edit_reply_markup(None)
    await call.message.answer("Игра началась! Подожди немного)")
    # устаналиваем состояние
    await Game.game.set()
    ships = generate_enemy_ships()
    # записываем сгенерируемый массив кораблей в базу данных
    await db.fill_ships_arr(ships, telegram_id=call.message.chat.id)
    shots = [[-1 for _ in range(10)] for _ in range(10)]
    # генерируем массив выстрелов в базе данных( -1 для всех, что значит что мы еще не стреляли туда)
    await db.fill_shots_arr(shots, telegram_id=call.message.chat.id)
    # рисуем изображение поля
    draw_field(ships, call.message.chat.id)
    await call.message.answer_photo(InputFile(f'{call.message.chat.id}.jpg'), reply_markup=get_default_keyboard(shots))


@rate_limit(limit=1)
@dp.callback_query_handler(text="free")
async def paid_game(call: CallbackQuery):
    # убираем часиви
    await call.answer(cache_time=60)
    # удаляем клавиатуру
    await call.message.edit_reply_markup(None)
    await call.message.answer("Игра началась! Подожди немного)")
    # устаналиваем состояние
    await Game.game.set()
    ships = generate_enemy_ships()
    # записываем сгенерируемый массив кораблей в базу данных
    await db.fill_ships_arr(ships, telegram_id=call.message.chat.id)
    shots = [[-1 for _ in range(11)] for _ in range(11)]
    # генерируем массив выстрелов в базе данных( -1 для всех, что значит что мы еще не стреляли туда)
    await db.fill_shots_arr(shots, telegram_id=call.message.chat.id)
    # рисуем изображение поля
    draw_field(ships, call.message.chat.id)
    await call.message.answer_photo(InputFile(f'{call.message.chat.id}.jpg'), reply_markup=get_default_keyboard(shots))


def generate_enemy_ships():
    """
    Функция генерации массива кораблей, возращает массив кораблей [10][10]
    """
    quantity_x = quantity_y = 10  # кількість клітинок по вертикалі і горизонталі
    enemy_ships = [[0 for _ in range(quantity_x + 1)] for _ in range(quantity_y + 1)]
    ships_list = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
    sum_all_ships = sum(ships_list)
    sum_all_enemy = 0

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
    return enemy_ships[:11][:11]


def draw_field(ships, chat_id):
    """
    Эта функция генерирует изображения поля 500х500
    """
    photo_height = 500
    photo_width = 500
    quantity = 10
    step = photo_height // quantity
    img = Image.new('RGB', (photo_width, photo_height), 'white')
    draw = ImageDraw.Draw(img)
    for i in range(0, quantity):
        for j in range(0, quantity):
            if ships[j][i] > 0:
                # зарисовуем клеточки, где находятся корабли
                draw.rectangle((i * step + 2, j * step + 2, i * step + step, j * step + step), fill='violet')
    for i in range(0, quantity):
        # рисуем поле черными линиями
        draw.line((step * i, 0, step * i, photo_height), fill='black', width=2)
        draw.line((0, step * i, photo_width, step * i), fill='black', width=2)
    # сохраняем изображние по имени id в телеграм
    img.save(f'{chat_id}.jpg', quality=95)


def draw_lines(chat_id):
    photo_height = 500
    photo_width = 500
    quantity = 10
    step = photo_height // quantity
    img = Image.open(f'{chat_id}.jpg')
    draw = ImageDraw.Draw(img)
    for i in range(0, 10):
        # рисуем поле черными линиями
        draw.line((50 * i, 0, step * i, photo_height), fill='black', width=2)
        draw.line((0, 50 * i, photo_width, step * i), fill='black', width=2)
    img.save(f'{chat_id}.jpg', quality=95)


def change_image(i, j, ships, shot_field, chat_id):
    """
    Функция закрашивает клеточку куда стреляли
    """
    step = 50
    img = Image.open(f'{chat_id}.jpg')
    draw = ImageDraw.Draw(img)
    # 48 потому что бы не залазило на черные линии
    global click
    global ship_5
    global ship_6
    global ship_7
    global ship_8
    global ship_9
    global ship_10
    click = click - 1
    if ships[i][j] > 0:
        color = "red"
        draw.rectangle((j * step, i * step, j * step + step, i * step + step), fill=color)
        if ships[i][j] == 1 or ships[i][j] == 2 or ships[i][j] == 3 or ships[i][j] == 4:
            shot_field[i + 1][j - 1] = 1
            shot_field[i + 1][j] = 1
            shot_field[i + 1][j + 1] = 1
            shot_field[i][j - 1] = 1
            shot_field[i][j + 1] = 1
            shot_field[i - 1][j - 1] = 1
            shot_field[i - 1][j] = 1
            shot_field[i - 1][j + 1] = 1
            draw.rectangle((j * step, i * step, j * step + step, i * step + step), fill="green")
            color = "blue"
            if j < 9:
                draw.rectangle((j * step - step, i * step - step, j * step - step + step,
                                i * step - step + step), fill=color)
                draw.rectangle((j * step - step, i * step, j * step - step + step,
                                i * step + step), fill=color)
                draw.rectangle((j * step - step, i * step + step, j * step - step + step,
                                i * step + step + step), fill=color)
                draw.rectangle((j * step, i * step - step, j * step + step,
                                i * step - step + step), fill=color)
                draw.rectangle((j * step, i * step + step, j * step + step,
                                i * step + step + step), fill=color)
                draw.rectangle((j * step + step, i * step - step, j * step + step + step,
                                i * step - step + step), fill=color)
                draw.rectangle((j * step + step, i * step, j * step + step + step,
                                i * step + step), fill=color)
                draw.rectangle((j * step + step, i * step + step, j * step + step + step,
                                i * step + step + step), fill=color)
            else:
                draw.rectangle((j * step - step, i * step - step, j * step - step + step,
                                i * step - step + step), fill=color)
                draw.rectangle((j * step - step, i * step, j * step - step + step,
                                i * step + step), fill=color)
                draw.rectangle((j * step - step, i * step + step, j * step - step + step,
                                i * step + step + step), fill=color)
                draw.rectangle((j * step, i * step - step, j * step + step,
                                i * step - step + step), fill=color)
                draw.rectangle((j * step, i * step + step, j * step + step,
                                i * step + step + step), fill=color)
        if ships[i][j] == 5:
            ship_5 = ship_5 + 1
        elif ships[i][j] == 6:
            ship_6 = ship_6 + 1
        elif ships[i][j] == 7:
            ship_7 = ship_7 + 1
        elif ships[i][j] == 8:
            ship_8 = ship_8 + 1
        elif ships[i][j] == 9:
            ship_9 = ship_9 + 1
        elif ships[i][j] == 10:
            ship_10 = ship_10 + 1
    # сохраняем изображние по имени id в телеграм
    img.save(f'{chat_id}.jpg', quality=95)
    shot_field = ship_kill(i, j, ships, shot_field, chat_id)
    if ships[i][j] == 0:
        color = "blue"
        draw.rectangle((j * step, i * step, j * step + step, i * step + step), fill=color)
        img.save(f'{chat_id}.jpg', quality=95)
    return shot_field


def miss(x, y, ships, shot_field, draw):
    """
    Функция закрашует точки вокруг корабля, если он полностю уничтожен
    """
    step = 50
    color = "blue"
    if ships[x][y + 1] > 4 and ships[x][y - 1] > 4 and ships[x][y] != 0:  # по горизонтале
        shot_field[x + 1][y] = 1
        shot_field[x - 1][y] = 1
        draw.rectangle((y * step, x * step - step, y * step + step,
                        x * step - step + step), fill=color)
        draw.rectangle((y * step, x * step + step, y * step + step,
                        x * step + step + step), fill=color)
    else:
        if ships[x][y] > 4 and ships[x][y + 1] > 4 and ships[x][y - 1] == 0:
            shot_field[x + 1][y - 1] = 1
            shot_field[x + 1][y] = 1
            shot_field[x][y - 1] = 1
            shot_field[x - 1][y - 1] = 1
            shot_field[x - 1][y] = 1
            draw.rectangle((y * step - step, x * step - step, y * step - step + step,
                            x * step - step + step), fill=color)
            draw.rectangle((y * step - step, x * step, y * step - step + step,
                            x * step + step), fill=color)
            draw.rectangle((y * step - step, x * step + step, y * step - step + step,
                            x * step + step + step), fill=color)
            draw.rectangle((y * step, x * step - step, y * step + step,
                            x * step - step + step), fill=color)
            draw.rectangle((y * step, x * step + step, y * step + step,
                            x * step + step + step), fill=color)
        else:
            if y < 9:
                if ships[x][y] > 4 and ships[x][y - 1] > 4 and ships[x][y + 1] == 0:
                    shot_field[x + 1][y] = 1
                    shot_field[x + 1][y + 1] = 1
                    shot_field[x][y + 1] = 1
                    shot_field[x - 1][y] = 1
                    shot_field[x - 1][y + 1] = 1
                    draw.rectangle((y * step, x * step - step, y * step + step,
                                    x * step - step + step), fill=color)
                    draw.rectangle((y * step, x * step + step, y * step + step,
                                    x * step + step + step), fill=color)
                    draw.rectangle((y * step + step, x * step - step, y * step + step + step,
                                    x * step - step + step), fill=color)
                    draw.rectangle((y * step + step, x * step, y * step + step + step,
                                    x * step + step), fill=color)
                    draw.rectangle((y * step + step, x * step + step, y * step + step + step,
                                    x * step + step + step), fill=color)
            else:
                if ships[x][y] > 4:
                    shot_field[x + 1][y] = 1
                    shot_field[x - 1][y] = 1
                    draw.rectangle((y * step, x * step - step, y * step + step,
                                    x * step - step + step), fill=color)
                    draw.rectangle((y * step, x * step + step, y * step + step,
                                    x * step + step + step), fill=color)
    if y < 9:
        if ships[x + 1][y] > 4 and ships[x - 1][y] > 4 and ships[x][y] != 0:  # по вертикали
            shot_field[x][y - 1] = 1
            shot_field[x][y + 1] = 1
            draw.rectangle((y * step - step, x * step, y * step - step + step,
                            x * step + step), fill=color)
            draw.rectangle((y * step + step, x * step, y * step + step + step,
                            x * step + step), fill=color)
        else:
            if ships[x][y] > 4 and ships[x + 1][y] > 4 and ships[x - 1][y] == 0:
                shot_field[x][y - 1] = 1
                shot_field[x][y + 1] = 1
                shot_field[x - 1][y - 1] = 1
                shot_field[x - 1][y] = 1
                shot_field[x - 1][y + 1] = 1
                draw.rectangle((y * step - step, x * step - step, y * step - step + step,
                                x * step - step + step), fill=color)
                draw.rectangle((y * step - step, x * step, y * step - step + step,
                                x * step + step), fill=color)
                draw.rectangle((y * step, x * step - step, y * step + step,
                                x * step - step + step), fill=color)
                draw.rectangle((y * step + step, x * step - step, y * step + step + step,
                                x * step - step + step), fill=color)
                draw.rectangle((y * step + step, x * step, y * step + step + step,
                                x * step + step), fill=color)
            else:
                if ships[x][y] > 4 and ships[x - 1][y] > 4 and ships[x + 1][y] == 0:
                    shot_field[x + 1][y - 1] = 1
                    shot_field[x + 1][y] = 1
                    shot_field[x + 1][y + 1] = 1
                    shot_field[x][y - 1] = 1
                    shot_field[x][y + 1] = 1
                    draw.rectangle((y * step - step, x * step, y * step - step + step,
                                    x * step + step), fill=color)
                    draw.rectangle((y * step - step, x * step + step, y * step - step + step,
                                    x * step + step + step), fill=color)
                    draw.rectangle((y * step, x * step + step, y * step + step,
                                    x * step + step + step), fill=color)
                    draw.rectangle((y * step + step, x * step, y * step + step + step,
                                    x * step + step), fill=color)
                    draw.rectangle((y * step + step, x * step + step, y * step + step + step,
                                    x * step + step + step), fill=color)
    else:
        if ships[x + 1][y] > 4 and ships[x - 1][y] > 4 and ships[x][y] != 0:
            shot_field[x][y - 1] = 1
            draw.rectangle((y * step - step, x * step, y * step - step + step,
                            x * step + step), fill=color)
        else:
            if ships[x][y] > 4 and ships[x + 1][y] > 4 and ships[x - 1][y] == 0:
                shot_field[x][y - 1] = 1
                shot_field[x - 1][y - 1] = 1
                shot_field[x - 1][y] = 1
                draw.rectangle((y * step - step, x * step - step, y * step - step + step,
                                x * step - step + step), fill=color)
                draw.rectangle((y * step - step, x * step, y * step - step + step,
                                x * step + step), fill=color)
                draw.rectangle((y * step, x * step - step, y * step + step,
                                x * step - step + step), fill=color)
            else:
                if ships[x][y] > 4 and ships[x - 1][y] > 4 and ships[x + 1][y] == 0:
                    shot_field[x + 1][y - 1] = 1
                    shot_field[x + 1][y] = 1
                    shot_field[x][y - 1] = 1
                    draw.rectangle((y * step - step, x * step, y * step - step + step,
                                    x * step + step), fill=color)
                    draw.rectangle((y * step - step, x * step + step, y * step - step + step,
                                    x * step + step + step), fill=color)
                    draw.rectangle((y * step, x * step + step, y * step + step,
                                    x * step + step + step), fill=color)
    return draw, shot_field


def ship_kill(i, j, ships, shot_field, chat_id):
    """
    Функция меняет цвет корабля, если он полностю уничтожен
    """
    step = 50
    img = Image.open(f'{chat_id}.jpg')
    draw = ImageDraw.Draw(img)
    global ship_5
    global ship_6
    global ship_7
    global ship_8
    global ship_9
    global ship_10
    color = "green"
    if ship_5 == 2:
        for i in range(0, 10):
            for j in range(0, 10):
                if ships[i][j] == 5:
                    draw.rectangle((j * step, i * step, j * step + step,
                                    i * step + step), fill=color)
                    ship_5 = 0
                    draw, shot_field = miss(i, j, ships, shot_field, draw)
    elif ship_6 == 2:
        for i in range(0, 10):
            for j in range(0, 10):
                if ships[i][j] == 6:
                    draw.rectangle((j * step, i * step, j * step + step,
                                    i * step + step), fill=color)
                    ship_6 = 0
                    draw, shot_field = miss(i, j, ships, shot_field, draw)
    elif ship_7 == 2:
        for i in range(0, 10):
            for j in range(0, 10):
                if ships[i][j] == 7:
                    draw.rectangle((j * step, i * step, j * step + step,
                                    i * step + step), fill=color)
                    ship_7 = 0
                    draw, shot_field = miss(i, j, ships, shot_field, draw)
    elif ship_8 == 3:
        for i in range(0, 10):
            for j in range(0, 10):
                if ships[i][j] == 8:
                    draw.rectangle((j * step, i * step, j * step + step,
                                    i * step + step), fill=color)
                    ship_8 = 0
                    draw, shot_field = miss(i, j, ships, shot_field, draw)
    elif ship_9 == 3:
        for i in range(0, 10):
            for j in range(0, 10):
                if ships[i][j] == 9:
                    draw.rectangle((j * step, i * step, j * step + step,
                                    i * step + step), fill=color)
                    ship_9 = 0
                    draw, shot_field = miss(i, j, ships, shot_field, draw)
    elif ship_10 == 4:
        for i in range(0, 10):
            for j in range(0, 10):
                if ships[i][j] == 10:
                    draw.rectangle((j * step, i * step, j * step + step,
                                    i * step + step), fill=color)
                    ship_10 = 0
                    draw, shot_field = miss(i, j, ships, shot_field, draw)
    img.save(f'{chat_id}.jpg', quality=95)
    return shot_field
