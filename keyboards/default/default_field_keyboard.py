from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

default_field = ReplyKeyboardMarkup(row_width=10, resize_keyboard=True)

alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

for letter in alphabet:
    btn0 = KeyboardButton(text="{0}0".format(letter))
    btn1 = KeyboardButton(text="{0}1".format(letter))
    btn2 = KeyboardButton(text="{0}2".format(letter))
    btn3 = KeyboardButton(text="{0}3".format(letter))
    btn4 = KeyboardButton(text="{0}4".format(letter))
    btn5 = KeyboardButton(text="{0}5".format(letter))
    btn6 = KeyboardButton(text="{0}6".format(letter))
    btn7 = KeyboardButton(text="{0}7".format(letter))
    btn8 = KeyboardButton(text="{0}8".format(letter))
    btn9 = KeyboardButton(text="{0}9".format(letter))
    default_field.add(btn0, btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
