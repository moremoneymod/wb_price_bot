import asyncio

from price_parser import parse_price
import db

from price_change_alert import price_change_alert


async def is_price_change(new_price, old_price):
    if new_price == old_price:
        return False
    return True


async def change_price_check(article):  # функция возвращает список сообщений об изменении цены товара по артикулу
    product_data = await db.get_all_data_by_article(article)    # получаем всех пользователей по артикулу
    parsed_data = await parse_price(article)    # парсим товар по артикулу

    if parsed_data is None:
        return []
    new_price = parsed_data['product_price']

    print(product_data)
    print(parsed_data)

    alerts = []

    for data in product_data:
        old_price = data['old_price']

        if await is_price_change(new_price, old_price):
            if new_price > old_price:
                price_data = ['дороже', new_price, (new_price / old_price) * 100 - 100]
            else:
                price_data = ['дешевле', new_price, (old_price / new_price) * 100 - 100]

            alerts.append(await price_change_alert(data, price_data))
            await db.change_product_price_in_db(article, new_price) # если цена изменилась, то изменяем цену в бд

        else:
            return []
    return alerts
