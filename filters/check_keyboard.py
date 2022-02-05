import re

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class InField(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        """
        Фильтр пропускает только значения с клавиатуры A2, A7, J8 (состоит из 1 буквы и цифры)
        """
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        if len(message.text) == 2 and message.text[0] in alphabet and message.text[-1].isdigit():
            return True
        return False
