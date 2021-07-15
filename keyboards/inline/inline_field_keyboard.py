from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

inline_field = InlineKeyboardMarkup(row_width=10)

alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
for letter in alphabet:
    btn0 = InlineKeyboardButton(text="{0}0".format(letter), callback_data="{0}0".format(letter))
    btn1 = InlineKeyboardButton(text="{0}1".format(letter), callback_data="{0}1".format(letter))
    btn2 = InlineKeyboardButton(text="{0}2".format(letter), callback_data="{0}2".format(letter))
    btn3 = InlineKeyboardButton(text="{0}3".format(letter), callback_data="{0}3".format(letter))
    btn4 = InlineKeyboardButton(text="{0}4".format(letter), callback_data="{0}4".format(letter))
    btn5 = InlineKeyboardButton(text="{0}5".format(letter), callback_data="{0}5".format(letter))
    btn6 = InlineKeyboardButton(text="{0}6".format(letter), callback_data="{0}6".format(letter))
    btn7 = InlineKeyboardButton(text="{0}7".format(letter), callback_data="{0}7".format(letter))
    btn8 = InlineKeyboardButton(text="{0}8".format(letter), callback_data="{0}8".format(letter))
    btn9 = InlineKeyboardButton(text="{0}9".format(letter), callback_data="{0}9".format(letter))

    inline_field.add(btn0, btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
