import asyncio
import logging

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import db

import config
from handlers import handlers, callback_handlers
from change_price_checking import change_price_check

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(handlers.router)
dp.include_router(callback_handlers.router)


async def setup_bot_commands():
    bot_commands = [
        BotCommand(command='/help', description='Информация о боте'),
        BotCommand(command='/menu', description='Меню'),
        BotCommand(command='/cancel', description='Отмена добавления товара для отслеживания')
    ]
    await bot.set_my_commands(bot_commands)


async def main():
    await setup_bot_commands()
    print(type(scheduler.start()))
    ##await scheduler.start()
    await db.connect_to_db()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def check_price_change():
    articles = await db.get_all_articles()
    for article in articles:
        alerts = await change_price_check(article)  ## получаем список сообщений об изменении цены
        if len(alerts) == 0:
            continue
        for alert in alerts:
            chat_id = alert[0]
            text = alert[1]
            await bot.send_message(chat_id=chat_id, text=text)
        print(alerts)


if __name__ == "__main__":
    scheduler = AsyncIOScheduler(timezone='utc')
    scheduler.add_job(check_price_change, 'interval', seconds=3600)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
