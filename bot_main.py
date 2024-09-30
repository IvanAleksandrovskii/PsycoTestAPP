# bot_main.py

# import asyncio
from aiogram import Bot, Dispatcher

from core import logger, settings
from handlers import router as main_router


BOT_TOKEN = settings.bot.token

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


# if __name__ == "__main__":
#     asyncio.run(main())
