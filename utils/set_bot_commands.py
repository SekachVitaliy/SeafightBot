from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("stop", "Останавливает игру"),
            types.BotCommand("help", "Вывести справку"),
        ]
    )
