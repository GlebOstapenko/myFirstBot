import asyncio
import logging
from os import getenv
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.handlers.balance import register_handlers_balance
from app.handlers.currency import register_handlers_currency
from app.handlers.common import register_handlers_common
from app.handlers.adm_add_user import register_handlers_adduser

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="menu", description="Меню бота"),
        BotCommand(command="currency", description="Курсы обмена"),
        BotCommand(command="balance", description="Баланс кассы"),
        BotCommand(command="cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")



    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=getenv("BOT_TOKEN"))
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_handlers_common(dp)
    register_handlers_currency(dp)
    register_handlers_balance(dp)
    register_handlers_adduser(dp)

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
