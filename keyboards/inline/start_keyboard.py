from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
inline_start_keyboard = InlineKeyboardMarkup(row_width=2)


free = InlineKeyboardButton(text="Бесплатная", callback_data="free")
paid = InlineKeyboardButton(text="Платная", callback_data="paid")

inline_start_keyboard.add(free, paid)
