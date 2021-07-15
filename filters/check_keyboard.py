from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
import re


class InField(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        if len(message.text) == 2 and message.text[0] in alphabet and message.text[-1].isdigit():
            return True
        return False
