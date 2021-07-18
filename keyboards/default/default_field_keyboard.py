from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_default_keyboard(arr):
    """
    Получаем массив выстрелов и проверяем (попали, не попали, убили)
    и в зависимости от этого ставим разные кнопки.
    """
    default_field = ReplyKeyboardMarkup(row_width=10)

    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

    for letter in alphabet:
        if arr[alphabet.index(letter)][0] == -1:
            btn0 = KeyboardButton(text="{0}0".format(letter))
        elif arr[alphabet.index(letter)][0] == 1:
            btn0 = KeyboardButton(text="❌")
        else:
            btn0 = KeyboardButton(text="🔴")

        if arr[alphabet.index(letter)][1] == -1:
            btn1 = KeyboardButton(text="{0}1".format(letter))
        elif arr[alphabet.index(letter)][1] == 1:
            btn1 = KeyboardButton(text="❌")
        else:
            btn1 = KeyboardButton(text="🔴")

        if arr[alphabet.index(letter)][2] == -1:
            btn2 = KeyboardButton(text="{0}2".format(letter))
        elif arr[alphabet.index(letter)][2] == 1:
            btn2 = KeyboardButton(text="❌")
        else:
            btn2 = KeyboardButton(text="🔴")

        if arr[alphabet.index(letter)][3] == -1:
            btn3 = KeyboardButton(text="{0}3".format(letter))
        elif arr[alphabet.index(letter)][3] == 1:
            btn3 = KeyboardButton(text="❌")
        else:
            btn3 = KeyboardButton(text="🔴")

        if arr[alphabet.index(letter)][4] == -1:
            btn4 = KeyboardButton(text="{0}4".format(letter))
        elif arr[alphabet.index(letter)][4] == 1:
            btn4 = KeyboardButton(text="❌")
        else:
            btn4 = KeyboardButton(text="🔴")

        if arr[alphabet.index(letter)][5] == -1:
            btn5 = KeyboardButton(text="{0}5".format(letter))
        elif arr[alphabet.index(letter)][5] == 1:
            btn5 = KeyboardButton(text="❌")
        else:
            btn5 = KeyboardButton(text="🔴")

        if arr[alphabet.index(letter)][6] == -1:
            btn6 = KeyboardButton(text="{0}6".format(letter))
        elif arr[alphabet.index(letter)][6] == 1:
            btn6 = KeyboardButton(text="❌")
        else:
            btn6 = KeyboardButton(text="🔴")

        if arr[alphabet.index(letter)][7] == -1:
            btn7 = KeyboardButton(text="{0}7".format(letter))
        elif arr[alphabet.index(letter)][7] == 1:
            btn7 = KeyboardButton(text="❌")
        else:
            btn7 = KeyboardButton(text="🔴")

        if arr[alphabet.index(letter)][8] == -1:
            btn8 = KeyboardButton(text="{0}8".format(letter))
        elif arr[alphabet.index(letter)][8] == 1:
            btn8 = KeyboardButton(text="❌")
        else:
            btn8 = KeyboardButton(text="🔴")

        if arr[alphabet.index(letter)][9] == -1:
            btn9 = KeyboardButton(text="{0}9".format(letter))
        elif arr[alphabet.index(letter)][9] == 1:
            btn9 = KeyboardButton(text="❌")
        else:
            btn9 = KeyboardButton(text="🔴")

        default_field.add(btn0, btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
    return default_field
