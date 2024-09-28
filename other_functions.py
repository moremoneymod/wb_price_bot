import asyncio
from price_parser import parse_price
import db
from aiogram import types

WB_PRODUCT_URL = 'https://www.wildberries.ru/catalog/'
messages_to_delete = []


async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    await message.delete()


async def delete_messages():
    for message in messages_to_delete:
        await delete_message(message, sleep_time=1)
    messages_to_delete.clear()


async def is_valid_article(article):
    if article.isdigit() is False:
        return False

    if 10000000 <= int(article) <= 999999999999:
        data = await parse_price(int(article))
        if data is None:
            return False
        return True
    else:
        return False


async def create_product_card(article, user_id):
    product_data = await db.get_data_by_article(article, user_id)
    message = (f'{product_data['product_name']}\n\nТекущая цена: {product_data['new_price']} ₽\n'
               f'Цена на момент добавления товара: {product_data['first_price']} ₽\n\n\n{WB_PRODUCT_URL + article + "/detail.aspx"}')
    return message
