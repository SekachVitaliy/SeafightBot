from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
                return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username VARCHAR(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        balance INT NOT NULL DEFAULT 0,
        ships INT[][],
        shots INT[][],
        ship INT[],
<<<<<<< HEAD
        click INT,
        paid_game BOOLEAN DEFAULT FALSE
=======
        click INT
>>>>>>> 51e136b8a16e8faddbfa0f620d659741dcbf1bb9
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id):
        sql = "INSERT INTO Users (full_name, username, telegram_id) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, full_name, username, telegram_id, fetchrow=True)

    async def add_user_with_balance(self, full_name, username, telegram_id, balance):
        sql = "INSERT INTO Users (full_name, username, telegram_id, balance) VALUES($1, $2, $3, $4) returning *"
        return await self.execute(sql, full_name, username, telegram_id, balance, fetchrow=True)

    async def update_balance(self, balance, telegram_id):
        sql = "UPDATE Users SET balance=$1 WHERE telegram_id=$2"
        return await self.execute(sql, balance, telegram_id, execute=True)

    async def get_balance(self, telegram_id):
        sql = "SELECT balance FROM Users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchval=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_users(self):
        return await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_table_users(self):
        return await self.execute("DROP TABLE Users", execute=True)

    """
    Работа с массивом кораблей
    """

    async def fill_ships_arr(self, array, telegram_id):
        sql = f" UPDATE Users SET ships = ARRAY{array}WHERE telegram_id=$1;"
        return await self.execute(sql, telegram_id, execute=True)

    async def fill_ships_cell(self, i, j, value, telegram_id):
        return await self.execute(f"UPDATE Users SET ships[{i+1}][{j+1}] = {value} WHERE telegram_id={telegram_id};",
                                  execute=True)

    async def get_ships_arr(self, telegram_id):
        sql = "SELECT ships FROM Users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchval=True)

    """
    Работа с массивом выстрелов
    """

    async def fill_shots_arr(self, array, telegram_id):
        sql = f" UPDATE Users SET shots = ARRAY{array}WHERE telegram_id=$1;"
        return await self.execute(sql, telegram_id, execute=True)

    async def fill_shots_cell(self, i, j, value, telegram_id):
        return await self.execute(f"UPDATE Users SET shots[{i+1}][{j+1}] = {value} WHERE telegram_id={telegram_id};",
                                  execute=True)

    async def get_shots_arr(self, telegram_id):
        sql = "SELECT shots FROM Users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchval=True)

    """
    Работа с массивом точних выстрелов
    """

    async def fill_ship_masiv(self, array, telegram_id):
        sql = f" UPDATE Users SET ship = ARRAY{array}WHERE telegram_id=$1;"
        return await self.execute(sql, telegram_id, execute=True)

    async def fill_ship_cell(self, i, value, telegram_id):
        return await self.execute(f"UPDATE Users SET ship[{i+1}] = {value} WHERE telegram_id={telegram_id};",
                                  execute=True)

    async def get_ship_masiv(self, telegram_id):
        sql = "SELECT ship FROM Users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchval=True)

    """
    Работа с количеством выстрелов
    """

    async def fill_click(self, number, telegram_id):
        sql = f" UPDATE Users SET click = {number} WHERE telegram_id=$1;"
        return await self.execute(sql, telegram_id, execute=True)

    async def fill_click_cell(self, value, telegram_id):
        return await self.execute(f"UPDATE Users SET click = {value} WHERE telegram_id={telegram_id};",
                                  execute=True)

    async def get_click(self, telegram_id):
        sql = "SELECT click FROM Users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchval=True)
<<<<<<< HEAD

    async def get_paid_game(self, telegram_id):
        sql = "SELECT paid_game FROM Users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchval=True)

    async def set_paid_game(self, telegram_id):
        sql = f" UPDATE Users SET paid_game = {True} WHERE telegram_id=$1;"
        return await self.execute(sql, telegram_id, fetchval=True)

    async def reset_paid_game(self, telegram_id):
        sql = f" UPDATE Users SET paid_game = {False} WHERE telegram_id=$1;"
        return await self.execute(sql, telegram_id, fetchval=True)
=======
>>>>>>> 51e136b8a16e8faddbfa0f620d659741dcbf1bb9
