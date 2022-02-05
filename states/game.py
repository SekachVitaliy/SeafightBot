from aiogram.dispatcher.filters.state import State, StatesGroup


class Game(StatesGroup):
    game = State()
    pay = State()
    withdraw = State()
    not_started = State()
