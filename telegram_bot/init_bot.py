from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from telegram_bot.credentials import settings
from loguru import logger

storage = MemoryStorage()
bot = Bot(token=settings.API_KEY)
dp = Dispatcher(bot, storage=storage)

logger.info("Bot successfully initialized!")

