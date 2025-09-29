# Dotenv
import os
from dotenv import load_dotenv

# Aiogram
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

# Python files
from handlers import router
import database as db


# Loading .env file
load_dotenv()

# Connecting to telegram bot
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()


# Preparing for bot start
async def on_startup():
    pass
    """await db.delete_tables()
    await db.create_tables()
    await db.add_staff('admin1', '123', 'admin1', 'admin')
    await db.add_staff('admin2', '123', 'admin2', 'operator')
    await db.add_staff('admin3', '123', 'admin3', 'kitchen')"""


# Running bot
async def main():
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(on_startup())
    asyncio.run(main())
