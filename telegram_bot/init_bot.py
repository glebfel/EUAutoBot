from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from core import settings
from core import custom_logger

storage = MemoryStorage()
bot = Bot(token=settings.API_KEY)
dp = Dispatcher(bot, storage=storage)

custom_logger.info("Bot successfully initialized!")

