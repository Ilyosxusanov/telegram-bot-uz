import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import users, admin
from aiogram import types

async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="start", description="Boshlash"),
        types.BotCommand(command="help", description="Admin bilan bog'lanish"),
        types.BotCommand(command="ai", description="AI bilan suhbat"),
        types.BotCommand(command="stop", description="AI suhbatini to'xtatish"),
        types.BotCommand(command="donat", description="Qo'llab-quvvatlash")
    ]
    await bot.set_my_commands(commands)

async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        bot = Bot(token=BOT_TOKEN)
        # Tokenni tekshirish
        me = await bot.get_me()
        print(f"Bot @{me.username} muvaffaqiyatli ulahndi!")
        
        dp = Dispatcher()
        
        # Komandalarni o'rnatish
        await set_commands(bot)
        
        dp.include_router(admin.router)
        dp.include_router(users.router)

        print("Bot ishga tushdi...")
        await dp.start_polling(bot)
    except Exception as e:
        if "Unauthorized" in str(e):
            print("\n" + "!"*40)
            print("XATOLIK: Bot Tokeni noto'g'ri!")
            print("Iltimos, .env faylini oching va @BotFather dan olgan")
            print("to'liq tokenni BOT_TOKEN qatoriga yozing.")
            print("!"*40 + "\n")
        else:
            print(f"Xatolik yuz berdi: {e}")

if __name__ == "__main__":
    asyncio.run(main())
