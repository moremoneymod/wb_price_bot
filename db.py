import asyncio
import aiomysql
from config import HOST, PORT, USER, PASSWORD, DATABASE, TABLE


class Connection_to_db():
    def __init__(self):
        self.conn = None


connection = Connection_to_db()


async def connect_to_db():
    connection.conn = await aiomysql.create_pool(host=HOST, port=PORT, user=USER, password=PASSWORD,
                                                 db=DATABASE)


async def get_data_from_db(query):
    pool = connection.conn
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query)
            data = await cur.fetchall()
    return data


async def add_data_to_db(query):
    pool = connection.conn
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query)
        await conn.commit()


async def delete_data_from_db(query):
    pool = connection.conn
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query)
        await conn.commit()


async def check_article_in_db(article):
    data = await get_data_from_db(f'SELECT * FROM {TABLE} WHERE product_article={article};')
    if len(data) == 0:
        return False
    else:
        return True


async def check_article_in_db_by_user_id(article, user_id):
    data = await get_data_from_db(f'SELECT * FROM {TABLE} WHERE product_article={article} AND user_id={user_id};')
    if len(data) == 0:
        return False
    else:
        return True


async def check_products_in_db_by_user_id(user_id):
    data = await get_data_from_db(f'SELECT * FROM {TABLE} WHERE user_id={user_id};')
    if len(data) == 0:
        return False
    else:
        return True


async def add_product_to_db(product_article, user_id, product_name, new_price, old_price, first_price):
    await add_data_to_db(
        f'INSERT {TABLE} (product_article, user_id, product_name, new_price, old_price, first_price) '
        f'VALUES ({product_article}, {user_id}, "{product_name}", {new_price}, {old_price}, {first_price});')


async def delete_data_by_article(article, user_id):
    await delete_data_from_db(f'DELETE FROM {TABLE} WHERE product_article={article} AND user_id={user_id}')


async def get_all_data_by_article(article):
    if await check_article_in_db(article):
        data = await get_data_from_db(f'SELECT * FROM {TABLE} WHERE product_article={article};')
        users = []
        for entry in data:
            data_dict = {'product_article': entry[0], 'user_id': entry[1], 'product_name': entry[2],
                         'new_price': entry[3], 'old_price': entry[4], 'first_price': entry[5]}
            users.append(data_dict)
        return users
    else:
        return []


async def get_all_data_by_user_id(user_id):
    if await check_products_in_db_by_user_id(user_id):
        data = await get_data_from_db(f'SELECT * FROM {TABLE} WHERE user_id={user_id}')
        products = []
        for product in data:
            data_dict = {'product_article': product[0], 'user_id': product[1], 'product_name': product[2],
                         'new_price': product[3], 'old_price': product[4], 'first_price': product[5]}
            products.append(data_dict)
        return products
    else:
        return []


async def get_data_by_article(article, user_id):
    data = await get_data_from_db(
        f'SELECT * FROM {TABLE} WHERE product_article={article} AND user_id={user_id}')

    data_dict = {'product_article': data[0][0], 'user_id': data[0][1], 'product_name': data[0][2],
                 'new_price': data[0][3], 'old_price': data[0][4], 'first_price': data[0][5]}
    return data_dict


async def get_all_articles():
    data = await get_data_from_db(f'SELECT product_article FROM {TABLE};')
    articles = []
    for article in data:
        articles.append(article[0])
    return articles


async def get_user_ids_by_article(article):
    data = await get_data_from_db(f'SELECT user_id FROM {TABLE} WHERE product_article={article};')
    user_ids = []
    for user_id in data:
        user_ids.append(user_id[0])
    return user_ids


async def change_product_price_in_db(article, new_price):
    await add_data_to_db(f'UPDATE {TABLE} SET new_price = {new_price}, '
                         f'old_price = {new_price} WHERE product_article = {article};')


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(connect_to_db())
    print(loop.run_until_complete(get_user_ids_by_article(100000000)))
    print(loop.run_until_complete(get_all_articles()))
    loop.run_forever()
