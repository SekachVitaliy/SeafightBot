import base64
import hashlib
import logging
import random

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import CallbackQuery, InputFile
from asyncpg.exceptions import UniqueViolationError
from PIL import Image, ImageDraw

from data.config import ADMINS, LIQPAY_TOKEN
from filters.private_chat import IsPrivate
from keyboards.default.default_field_keyboard import get_default_keyboard
from keyboards.inline.paid_keyboard import inline_paid_keyboard
from keyboards.inline.start_keyboard import inline_start_keyboard
from loader import db, dp, bot
from states import Game
from utils.misc import rate_limit


@rate_limit(limit=1)
@dp.message_handler(CommandStart(deep_link="reklama"))
@dp.message_handler(CommandStart(deep_link="reklama"), IsPrivate(), state=Game.not_started)
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
            balance=50
        )
        logging.info(f"Добавлен новый пользователь: Fullname={user[1]}, username={user[2]}, telegram_id={user[3]}, "
                     f"balance={user[4]}, количество:{await db.count_users()}")
    except UniqueViolationError:
        # Если пользователь уже есть в БД
        user = await db.select_user(telegram_id=message.from_user.id)
    text = f"Привет, {message.from_user.full_name}!\nТы перешел по реферальной ссылке и тебе начислено 50 грн и ты " \
           f"можешь испытать удачу в платной версии игры.\n" \
           f"Есть бесплатная и платная версии, платная версия стоит 10," \
           f"\nкогда выигрываешь получишь 20)" \
           f"\nНо у тебя есть ограниченое количество ходов - 40 \nДавай сыграем ?) "
    await Game.not_started.set()
    await message.answer(text, reply_markup=inline_start_keyboard)


@rate_limit(limit=1)
@dp.message_handler(CommandStart(), IsPrivate())
@dp.message_handler(CommandStart(), IsPrivate(), state=Game.not_started)
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
           f"\nкогда выигрываешь получишь 20)" \
           f"\nНо у тебя есть ограниченое количество ходов - 40 \nДавай сыграем ?) "
    await Game.not_started.set()
    await message.answer(text, reply_markup=inline_start_keyboard)


@rate_limit(limit=1)
@dp.callback_query_handler(text="paid", state=Game.not_started)
async def paid_game(call: CallbackQuery):
    # убираем часиви возле кнопки
    await call.answer(cache_time=60)
    # удаляем клавиатуру
    await call.message.edit_reply_markup(None)
    balance = await db.get_balance(telegram_id=call.message.chat.id)
    await call.message.answer(f"Твой баланс: {balance}. Игра стоит 10 грн, сыграем?", reply_markup=inline_paid_keyboard)


@rate_limit(limit=1)
@dp.callback_query_handler(text="back_from_paid", state=Game.not_started)
async def back_from_paid(call: CallbackQuery):
    # убираем часиви возле кнопки
    await call.answer(cache_time=60)
    # удаляем клавиатуру
    await call.message.edit_reply_markup(None)
    text = f"Есть бесплатная и платная версии, платная версия стоит 10," \
           f"\nкогда выигрываешь получишь 20)" \
           f"\nНо у тебя есть ограниченое количество ходов - 40 \nДавай сыграем ?) "
    await call.message.answer(text, reply_markup=inline_start_keyboard)


@rate_limit(limit=1)
@dp.callback_query_handler(text="paid_game", state=Game.not_started)
async def back_from_paid(call: CallbackQuery):
    # убираем часиви возле кнопки
    await call.answer(cache_time=60)
    # удаляем клавиатуру
    await call.message.edit_reply_markup(None)
    balance = await db.get_balance(call.message.chat.id)
    if balance >= 10:
        await db.set_paid_game(call.message.chat.id)
        await db.update_balance(balance - 10, call.message.chat.id)
        await call.message.answer("Игра началась! Подожди немного)")
        # устаналиваем состояние
        await Game.game.set()
        ships = generate_enemy_ships()
        # записываем сгенерируемый массив кораблей в базу данных
        await db.fill_ships_arr(ships, telegram_id=call.message.chat.id)
        click = 40
        # записываю количество выстрелов в базу данных
        await db.fill_click(click, telegram_id=call.message.chat.id)
        masiv_ship = [0, 0, 0, 0, 0, 0]
        # записываю массив для точных выстрелов по кораблю в базу данных
        await db.fill_ship_masiv(masiv_ship, telegram_id=call.message.chat.id)
        shots = [[-1 for _ in range(11)] for _ in range(11)]
        # генерируем массив выстрелов в базе данных( -1 для всех, что значит что мы еще не стреляли туда)
        await db.fill_shots_arr(shots, telegram_id=call.message.chat.id)
        # рисуем изображение поля
        draw_field(call.message.chat.id)
        await call.message.answer_photo(InputFile(f'{call.message.chat.id}.png'),
                                        reply_markup=get_default_keyboard(shots))
    else:
        text = f"Для начала пополни свой баланс! \nТвой баланс: {balance}. Игра стоит 10 грн, сыграем?"
        await call.message.answer(text, reply_markup=inline_paid_keyboard)


@rate_limit(limit=1)
@dp.callback_query_handler(text="deposit", state=Game.not_started)
async def back_from_paid(call: CallbackQuery):
    # убираем часиви возле кнопки
    await call.answer(cache_time=60)
    # удаляем клавиатуру
    await call.message.edit_reply_markup(None)
    # text = f"Депозит скоро будет работать!\nПока можешь сыграть "
    # await call.message.answer(text, reply_markup=inline_start_keyboard)
    await bot.send_invoice(chat_id=call.from_user.id, title="Пополнение", description="Пополнение счета",
                           payload="payload", provider_token=LIQPAY_TOKEN, currency='UAH',
                           prices=[{"label": "UAH", "amount": 1000}])


@dp.message_handler(content_types=types.ContentTypes.SUCCESSFUL_PAYMENT)
async def process_pay(message: types.Message):
    if message.successful_payment.invoice_payload == "payload":
        await message.answer('Оплатил')


@dp.pre_checkout_query_handler()
async def pre_checkout_query_handler(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@rate_limit(limit=1)
@dp.callback_query_handler(text="withdraw", state=Game.not_started)
async def withdraw(call: CallbackQuery):
    # убираем часиви возле кнопки
    await call.answer(cache_time=60)
    # удаляем клавиатуру
    await call.message.edit_reply_markup(None)
    balance = await db.get_balance(call.message.chat.id)
    if balance > 0:
        text = f"Твой баланс: {balance}.\nВведи сумму которую хочешь вывести:"
        await Game.withdraw.set()
        await call.message.answer(text)
    else:
        text = f"Твой баланс: {balance}.\nПопробуй пополить и выиграть)"
        await call.message.answer(text, reply_markup=inline_paid_keyboard)


@rate_limit(limit=1)
@dp.message_handler(state=Game.withdraw)
async def check_withdraw(message: types.Message):
    try:
        balance = await db.get_balance(message.chat.id)
        if balance < int(message.text):
            await message.answer(
                f"Ваш баланс: {balance}, менше чем сумма которую вы хотите вывести.\nВведите другую сумму.")
        else:
            await db.update_balance(balance - int(message.text), message.chat.id)
            await db.reset_paid_game(message.chat.id)
            await message.answer("Ваш вывод принят, ждите связи с администратором)")
            await message.answer("Можете поиграть еще)", reply_markup=inline_start_keyboard)
            await Game.not_started.set()
            for admin in ADMINS:
                try:
                    # Отправляем админам сообщение
                    text = f"Пользователь {message.from_user.username} с id:{message.from_user.id} хочет вывести сумму {int(message.text)} "
                    await dp.bot.send_message(admin, text)

                except Exception as err:
                    logging.exception(err)
    except TypeError:
        logging.info("Не удалось преобразовать значения пользователя в число")
        await message.answer("Попробуйте ввести сумму без валюты в формате: 50")


@rate_limit(limit=1)
@dp.callback_query_handler(text="free", state=Game.not_started)
async def paid_game(call: CallbackQuery):
    # убираем часики
    await call.answer(cache_time=60)
    # удаляем клавиатуру
    await call.message.edit_reply_markup(None)
    await call.message.answer("Игра началась! Подожди немного)")
    # устаналиваем состояние
    await Game.game.set()
    ships = generate_enemy_ships()
    # записываем сгенерируемый массив кораблей в базу данных
    await db.fill_ships_arr(ships, telegram_id=call.message.chat.id)
    click = 40
    # записываю количество выстрелов в базу данных
    await db.fill_click(click, telegram_id=call.message.chat.id)
    masiv_ship = [0, 0, 0, 0, 0, 0]
    # записываю массив для точных выстрелов по кораблю в базу данных
    await db.fill_ship_masiv(masiv_ship, telegram_id=call.message.chat.id)
    shots = [[-1 for _ in range(11)] for _ in range(11)]
    # генерируем массив выстрелов в базе данных( -1 для всех, что значит что мы еще не стреляли туда)
    await db.fill_shots_arr(shots, telegram_id=call.message.chat.id)
    # рисуем изображение поля
    draw_field(call.message.chat.id)
    await call.message.answer_photo(InputFile(f'{call.message.chat.id}.png'), reply_markup=get_default_keyboard(shots))


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


def draw_field(chat_id):
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
        # рисуем поле черными линиями
        draw.line((step * i, 0, step * i, photo_height), fill='black', width=2)
        draw.line((0, step * i, photo_width, step * i), fill='black', width=2)
    # сохраняем изображние по имени id в телеграм
    img.save(f'{chat_id}.png', quality=95)


def change_image(i, j, ships, masiv_ship, shot_field, click, chat_id):
    """
    Функция закрашивает клеточку куда стреляли
    """
    step = 50
    img = Image.open(f'{chat_id}.png')
    draw = ImageDraw.Draw(img)

    click = click - 1
    masiv_ship = accurate_shots(i, j, ships, masiv_ship)
    if ships[i][j] > 0:
        color = "red"
        draw.rectangle((j * step + 2, i * step + 2, j * step + step - 1, i * step + step - 1), fill=color)
        if ships[i][j] == 1 or ships[i][j] == 2 or ships[i][j] == 3 or ships[i][j] == 4:
            shot_field[i + 1][j - 1] = 1
            shot_field[i + 1][j] = 1
            shot_field[i + 1][j + 1] = 1
            shot_field[i][j - 1] = 1
            shot_field[i][j + 1] = 1
            shot_field[i - 1][j - 1] = 1
            shot_field[i - 1][j] = 1
            shot_field[i - 1][j + 1] = 1
            draw.rectangle((j * step + 2, i * step + 2, j * step + step - 1, i * step + step - 1), fill="green")
            color = "blue"
            if j < 9:
                draw.rectangle((j * step + 2 - step, i * step + 2 - step, j * step - 1 - step + step,
                                i * step - 1 - step + step), fill=color)
                draw.rectangle((j * step + 2 - step, i * step + 2, j * step - 1 - step + step,
                                i * step - 1 + step), fill=color)
                draw.rectangle((j * step + 2 - step, i * step + 2 + step, j * step - 1 - step + step,
                                i * step - 1 + step + step), fill=color)
                draw.rectangle((j * step + 2, i * step + 2 - step, j * step - 1 + step,
                                i * step - 1 - step + step), fill=color)
                draw.rectangle((j * step + 2, i * step + 2 + step, j * step - 1 + step,
                                i * step - 1 + step + step), fill=color)
                draw.rectangle((j * step + 2 + step, i * step + 2 - step, j * step - 1 + step + step,
                                i * step - 1 - step + step), fill=color)
                draw.rectangle((j * step + 2 + step, i * step + 2, j * step - 1 + step + step,
                                i * step - 1 + step), fill=color)
                draw.rectangle((j * step + 2 + step, i * step + 2 + step, j * step - 1 + step + step,
                                i * step - 1 + step + step), fill=color)
            else:
                draw.rectangle((j * step + 2 - step, i * step + 2 - step, j * step - 1 - step + step,
                                i * step - 1 - step + step), fill=color)
                draw.rectangle((j * step + 2 - step, i * step + 2, j * step - 1 - step + step,
                                i * step - 1 + step), fill=color)
                draw.rectangle((j * step + 2 - step, i * step + 2 + step, j * step - 1 - step + step,
                                i * step - 1 + step + step), fill=color)
                draw.rectangle((j * step + 2, i * step + 2 - step, j * step - 1 + step,
                                i * step - 1 - step + step), fill=color)
                draw.rectangle((j * step + 2, i * step + 2 + step, j * step - 1 + step,
                                i * step - 1 + step + step), fill=color)
    # сохраняем изображние по имени id в телеграм
    img.save(f'{chat_id}.png', quality=95)
    masiv_ship, shot_field = ship_kill(ships, masiv_ship, shot_field, chat_id)
    if ships[i][j] == 0:
        color = "blue"
        draw.rectangle((j * step + 2, i * step + 2, j * step + step - 1, i * step + step - 1), fill=color)
        img.save(f'{chat_id}.png', quality=95)
    return click, masiv_ship, shot_field


def accurate_shots(i, j, ships, masiv_ship):
    if ships[i][j] == 5:
        masiv_ship[0] = masiv_ship[0] + 1
    elif ships[i][j] == 6:
        masiv_ship[1] = masiv_ship[1] + 1
    elif ships[i][j] == 7:
        masiv_ship[2] = masiv_ship[2] + 1
    elif ships[i][j] == 8:
        masiv_ship[3] = masiv_ship[3] + 1
    elif ships[i][j] == 9:
        masiv_ship[4] = masiv_ship[4] + 1
    elif ships[i][j] == 10:
        masiv_ship[5] = masiv_ship[5] + 1
    return masiv_ship


def miss(x, y, ships, shot_field, draw):
    """
    Функция закрашует точки вокруг корабля, если он полностю уничтожен
    """
    step = 50
    color = "blue"
    if ships[x][y + 1] > 4 and ships[x][y - 1] > 4 and ships[x][y] != 0:  # по горизонтале
        shot_field[x + 1][y] = 1
        shot_field[x - 1][y] = 1
        draw.rectangle((y * step + 2, x * step + 2 - step, y * step - 1 + step,
                        x * step - 1 - step + step), fill=color)
        draw.rectangle((y * step + 2, x * step + 2 + step, y * step - 1 + step,
                        x * step - 1 + step + step), fill=color)
    else:
        if ships[x][y] > 4 and ships[x][y + 1] > 4 and ships[x][y - 1] == 0:
            shot_field[x + 1][y - 1] = 1
            shot_field[x + 1][y] = 1
            shot_field[x][y - 1] = 1
            shot_field[x - 1][y - 1] = 1
            shot_field[x - 1][y] = 1
            draw.rectangle((y * step + 2 - step, x * step + 2 - step, y * step - 1 - step + step,
                            x * step - 1 - step + step), fill=color)
            draw.rectangle((y * step + 2 - step, x * step + 2, y * step - 1 - step + step,
                            x * step - 1 + step), fill=color)
            draw.rectangle((y * step + 2 - step, x * step + 2 + step, y * step - 1 - step + step,
                            x * step - 1 + step + step), fill=color)
            draw.rectangle((y * step + 2, x * step + 2 - step, y * step - 1 + step,
                            x * step - 1 - step + step), fill=color)
            draw.rectangle((y * step + 2, x * step + 2 + step, y * step - 1 + step,
                            x * step - 1 + step + step), fill=color)
        else:
            if y < 9:
                if ships[x][y] > 4 and ships[x][y - 1] > 4 and ships[x][y + 1] == 0:
                    shot_field[x + 1][y] = 1
                    shot_field[x + 1][y + 1] = 1
                    shot_field[x][y + 1] = 1
                    shot_field[x - 1][y] = 1
                    shot_field[x - 1][y + 1] = 1
                    draw.rectangle((y * step + 2, x * step + 2 - step, y * step - 1 + step,
                                    x * step - 1 - step + step), fill=color)
                    draw.rectangle((y * step + 2, x * step + 2 + step, y * step - 1 + step,
                                    x * step - 1 + step + step), fill=color)
                    draw.rectangle((y * step + 2 + step, x * step + 2 - step, y * step - 1 + step + step,
                                    x * step - 1 - step + step), fill=color)
                    draw.rectangle((y * step + 2 + step, x * step + 2, y * step - 1 + step + step,
                                    x * step - 1 + step), fill=color)
                    draw.rectangle((y * step + 2 + step, x * step + 2 + step, y * step - 1 + step + step,
                                    x * step - 1 + step + step), fill=color)
            else:
                if ships[x][y] > 4:
                    shot_field[x + 1][y] = 1
                    shot_field[x - 1][y] = 1
                    draw.rectangle((y * step + 2, x * step + 2 - step, y * step - 1 + step,
                                    x * step - 1 - step + step), fill=color)
                    draw.rectangle((y * step + 2, x * step + 2 + step, y * step - 1 + step,
                                    x * step - 1 + step + step), fill=color)
    if y < 9:
        if ships[x + 1][y] > 4 and ships[x - 1][y] > 4 and ships[x][y] != 0:  # по вертикали
            shot_field[x][y - 1] = 1
            shot_field[x][y + 1] = 1
            draw.rectangle((y * step + 2 - step, x * step + 2, y * step - 1 - step + step,
                            x * step - 1 + step), fill=color)
            draw.rectangle((y * step + 2 + step, x * step + 2, y * step - 1 + step + step,
                            x * step - 1 + step), fill=color)
        else:
            if ships[x][y] > 4 and ships[x + 1][y] > 4 and ships[x - 1][y] == 0:
                shot_field[x][y - 1] = 1
                shot_field[x][y + 1] = 1
                shot_field[x - 1][y - 1] = 1
                shot_field[x - 1][y] = 1
                shot_field[x - 1][y + 1] = 1
                draw.rectangle((y * step + 2 - step, x * step + 2 - step, y * step - 1 - step + step,
                                x * step - 1 - step + step), fill=color)
                draw.rectangle((y * step + 2 - step, x * step + 2, y * step - 1 - step + step,
                                x * step - 1 + step), fill=color)
                draw.rectangle((y * step + 2, x * step + 2 - step, y * step - 1 + step,
                                x * step - 1 - step + step), fill=color)
                draw.rectangle((y * step + 2 + step, x * step + 2 - step, y * step - 1 + step + step,
                                x * step - 1 - step + step), fill=color)
                draw.rectangle((y * step + 2 + step, x * step + 2, y * step - 1 + step + step,
                                x * step - 1 + step), fill=color)
            else:
                if ships[x][y] > 4 and ships[x - 1][y] > 4 and ships[x + 1][y] == 0:
                    shot_field[x + 1][y - 1] = 1
                    shot_field[x + 1][y] = 1
                    shot_field[x + 1][y + 1] = 1
                    shot_field[x][y - 1] = 1
                    shot_field[x][y + 1] = 1
                    draw.rectangle((y * step + 2 - step, x * step + 2, y * step - 1 - step + step,
                                    x * step - 1 + step), fill=color)
                    draw.rectangle((y * step + 2 - step, x * step + 2 + step, y * step - 1 - step + step,
                                    x * step - 1 + step + step), fill=color)
                    draw.rectangle((y * step + 2, x * step + 2 + step, y * step - 1 + step,
                                    x * step - 1 + step + step), fill=color)
                    draw.rectangle((y * step + 2 + step, x * step + 2, y * step - 1 + step + step,
                                    x * step - 1 + step), fill=color)
                    draw.rectangle((y * step + 2 + step, x * step + 2 + step, y * step - 1 + step + step,
                                    x * step - 1 + step + step), fill=color)
    else:
        if ships[x + 1][y] > 4 and ships[x - 1][y] > 4 and ships[x][y] != 0:
            shot_field[x][y - 1] = 1
            draw.rectangle((y * step + 2 - step, x * step + 2, y * step - 1 - step + step,
                            x * step - 1 + step), fill=color)
        else:
            if ships[x][y] > 4 and ships[x + 1][y] > 4 and ships[x - 1][y] == 0:
                shot_field[x][y - 1] = 1
                shot_field[x - 1][y - 1] = 1
                shot_field[x - 1][y] = 1
                draw.rectangle((y * step + 2 - step, x * step + 2 - step, y * step - 1 - step + step,
                                x * step - 1 - step + step), fill=color)
                draw.rectangle((y * step + 2 - step, x * step + 2, y * step - 1 - step + step,
                                x * step - 1 + step), fill=color)
                draw.rectangle((y * step + 2, x * step + 2 - step, y * step - 1 + step,
                                x * step - 1 - step + step), fill=color)
            else:
                if ships[x][y] > 4 and ships[x - 1][y] > 4 and ships[x + 1][y] == 0:
                    shot_field[x + 1][y - 1] = 1
                    shot_field[x + 1][y] = 1
                    shot_field[x][y - 1] = 1
                    draw.rectangle((y * step + 2 - step, x * step + 2, y * step - 1 - step + step,
                                    x * step - 1 + step), fill=color)
                    draw.rectangle((y * step + 2 - step, x * step + 2 + step, y * step - 1 - step + step,
                                    x * step - 1 + step + step), fill=color)
                    draw.rectangle((y * step + 2, x * step + 2 + step, y * step - 1 + step,
                                    x * step - 1 + step + step), fill=color)
    return draw, shot_field


def ship_kill(ships, masiv_ship, shot_field, chat_id):
    """
    Функция меняет цвет корабля, если он полностю уничтожен
    """
    step = 50
    img = Image.open(f'{chat_id}.png')
    draw = ImageDraw.Draw(img)
    color = "green"
    if masiv_ship[0] == 2:
        for i in range(0, 10):
            for j in range(0, 10):
                if ships[i][j] == 5:
                    draw.rectangle((j * step + 2, i * step + 2, j * step - 1 + step,
                                    i * step - 1 + step), fill=color)
                    draw, shot_field = miss(i, j, ships, shot_field, draw)
                    masiv_ship[0] = 0
    elif masiv_ship[1] == 2:
        for i in range(0, 10):
            for j in range(0, 10):
                if ships[i][j] == 6:
                    draw.rectangle((j * step + 2, i * step + 2, j * step - 1 + step,
                                    i * step - 1 + step), fill=color)
                    draw, shot_field = miss(i, j, ships, shot_field, draw)
                    masiv_ship[1] = 0
    elif masiv_ship[2] == 2:
        for i in range(0, 10):
            for j in range(0, 10):
                if ships[i][j] == 7:
                    draw.rectangle((j * step + 2, i * step + 2, j * step - 1 + step,
                                    i * step - 1 + step), fill=color)
                    draw, shot_field = miss(i, j, ships, shot_field, draw)
                    masiv_ship[2] = 0
    elif masiv_ship[3] == 3:
        for i in range(0, 10):
            for j in range(0, 10):
                if ships[i][j] == 8:
                    draw.rectangle((j * step + 2, i * step + 2, j * step - 1 + step,
                                    i * step - 1 + step), fill=color)
                    draw, shot_field = miss(i, j, ships, shot_field, draw)
                    masiv_ship[3] = 0
    elif masiv_ship[4] == 3:
        for i in range(0, 10):
            for j in range(0, 10):
                if ships[i][j] == 9:
                    draw.rectangle((j * step + 2, i * step + 2, j * step - 1 + step,
                                    i * step - 1 + step), fill=color)
                    draw, shot_field = miss(i, j, ships, shot_field, draw)
                    masiv_ship[4] = 0
    elif masiv_ship[5] == 4:
        for i in range(0, 10):
            for j in range(0, 10):
                if ships[i][j] == 10:
                    draw.rectangle((j * step + 2, i * step + 2, j * step - 1 + step,
                                    i * step - 1 + step), fill=color)
                    draw, shot_field = miss(i, j, ships, shot_field, draw)
                    masiv_ship[5] = 0
    img.save(f'{chat_id}.png', quality=95)
    return masiv_ship, shot_field
