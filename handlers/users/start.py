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
        logging.info(f"Добавлен новый пользователь: Fullname={user[1]}, username={user[2]}, telegram_id={user[3]}"
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
        logging.info(f"Добавлен новый пользователь: Fullname={user[1]}, username={user[2]}, telegram_id={user[3]}"
                     f"balance={user[4]}, количество:{await db.count_users()}")
    except UniqueViolationError:
        # Если пользователь уже есть в БД
        user = await db.select_user(telegram_id=message.from_user.id)
    text = f"Привет, {message.from_user.full_name}!\nЕсть бесплатная и платная версии, платная версия стоит 10," \
           f"\nкогда выигрываешь получаешь 20)\nДавай сыграем ?) "
    await message.answer(text, reply_markup=inline_start_keyboard)


@dp.callback_query_handler(text="paid")
async def paid_game(call: CallbackQuery):
    # убираем часиви возле кнопки
    await call.answer(cache_time=60)
    # удаляем клавиатуру
    await call.message.edit_reply_markup(None)
    await call.message.answer("Игра началась! Подожди немного)")
    # устаналиваем состояние
    await Game.game.set()
    arr = generate_enemy_ships()
    # записываем сгенерируемый массив кораблей в базу данных
    await db.fill_ships_arr(arr, telegram_id=call.message.chat.id)
    # генерируем массив выстрелов в базе данных( -1 для всех, что значит что мы еще не стреляли туда)
    await db.fill_shots_arr(telegram_id=call.message.chat.id)
    # рисуем изображение поля
    draw_field(arr, call.message.chat.id)
    # получаем массив выстрелов и передаем его в клавиатуру
    shots = await db.get_shots_arr(call.message.chat.id)
    await call.message.answer_photo(InputFile(f'{call.message.chat.id}.jpg'), reply_markup=get_default_keyboard(shots))


@dp.callback_query_handler(text="free")
async def paid_game(call: CallbackQuery):
    # убираем часиви
    await call.answer(cache_time=60)
    # удаляем клавиатуру
    await call.message.edit_reply_markup(None)
    await call.message.answer("Игра началась! Подожди немного)")
    # устаналиваем состояние
    await Game.game.set()
    arr = generate_enemy_ships()
    # записываем сгенерируемый массив кораблей в базу данных
    await db.fill_ships_arr(arr, telegram_id=call.message.chat.id)
    # генерируем массив выстрелов в базе данных( -1 для всех, что значит что мы еще не стреляли туда)
    await db.fill_shots_arr(telegram_id=call.message.chat.id)
    # рисуем изображение поля
    draw_field(arr, call.message.chat.id)
    # получаем массив выстрелов и передаем его в клавиатуру
    shots = await db.get_shots_arr(call.message.chat.id)
    await call.message.answer_photo(InputFile(f'{call.message.chat.id}.jpg'), reply_markup=get_default_keyboard(shots))


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
