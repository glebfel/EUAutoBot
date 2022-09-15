from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from telegram_bot.credentials import settings
from loguru import logger

bot = Bot(token=settings.API_KEY)
dp = Dispatcher(bot)

logger.info("Bot successfully initialized!")

