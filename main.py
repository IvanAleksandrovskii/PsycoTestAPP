# main.py

import asyncio
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os

from core import logger
from handlers import router as main_router


logging.basicConfig(level=logging.INFO)
load_dotenv(".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

dp.include_router(main_router)


async def main():

    logger.info("Starting the bot")
    bot = Bot(token=BOT_TOKEN)

    try:
        logger.info("Starting polling")
        await dp.start_polling(bot)

    finally:
        logger.info("Closing the bot")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
