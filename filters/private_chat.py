from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsPrivate(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        """
        Фильтр проверяет на приватный чат, без групп и каналов
        """
        return message.chat.type == types.ChatType.PRIVATE
