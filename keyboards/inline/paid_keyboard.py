from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
inline_paid_keyboard = InlineKeyboardMarkup(row_width=2)


paid_game = InlineKeyboardButton(text="Сыграть", callback_data="paid_game")
deposit = InlineKeyboardButton(text="Пополнить", callback_data="deposit")
withdraw = InlineKeyboardButton(text="Вывести", callback_data="withdraw")
back_from_paid = InlineKeyboardButton(text="Назад", callback_data="back_from_paid")

inline_paid_keyboard.add(deposit, withdraw, paid_game, back_from_paid)
