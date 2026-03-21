import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    exit("Error: BOT_TOKEN not found in .env file")

router = Dispatcher()


@router.message(Command("start"))
async def cmd_start(message: types.Message, bot: Bot):
    me = await bot.get_me()
    await message.answer(
        f"Salom, {message.from_user.full_name}!\n\n"
        f"Sizning Telegram ID: {message.from_user.id}\n"
        f"Username: @{message.from_user.username or 'yoq'}\n\n"
        f"Bot nomi: @{me.username}\n"
        f"Bot ID: {me.id}"
    )


@router.message(Command("myid"))
async def cmd_myid(message: types.Message):
    await message.answer(
        f"Sizning Telegram ID: {message.from_user.id}"
    )


@router.message(Command("botname"))
async def cmd_botname(message: types.Message, bot: Bot):
    me = await bot.get_me()
    await message.answer(
        f"Bot nomi: @{me.username}\n"
        f"Bot ID: {me.id}"
    )


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)

    me = await bot.get_me()
    print(f"Bot @{me.username} muvaffaqiyatli ulandi!")

    await bot.set_my_commands([
        types.BotCommand(command="start", description="Boshlash - ID va Bot nomini ko'rish"),
        types.BotCommand(command="myid", description="Telegram ID ni olish"),
        types.BotCommand(command="botname", description="Bot nomini olish"),
    ])

    print("Bot ishga tushdi...")
    await router.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
