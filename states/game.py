from aiogram.dispatcher.filters.state import StatesGroup, State


class Game(StatesGroup):
    game = State()
    pay = State()

