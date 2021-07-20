from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_default_keyboard(arr):
    """
    Получаем массив выстрелов и проверяем (попали, не попали, убили)
    и в зависимости от этого ставим разные кнопки.
    """
    default_field = ReplyKeyboardMarkup(row_width=10)

    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    for letter in alphabet:
        buttons = []
        for number in range(0, 10):
            if arr[alphabet.index(letter)][number] == -1:
                buttons.append(KeyboardButton(text=f"{letter}{number}"))
            elif arr[alphabet.index(letter)][number] == 1:
                buttons.append(KeyboardButton(text="❌"))
            else:
                buttons.append(KeyboardButton(text="🔴"))
        default_field.add(buttons[1], buttons[2], buttons[3], buttons[4], buttons[5], buttons[6], buttons[7],
                          buttons[8], buttons[9])
    return default_field
