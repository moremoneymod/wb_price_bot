import aiohttp
import asyncio

from config import WB_PARSE_URL

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}


async def get_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as data:
            return await data.json()


async def parse_price(article):
    json_url = WB_PARSE_URL + str(article)
    json_data = await get_json(json_url)

    try:
        product_data = json_data['data']['products'][0]
        product_price = product_data['sizes'][0]['price']
    except (IndexError, KeyError) as error:
        return None

    ##print(json_data)

    product_name = product_data['name']
    product_price_actual = product_price['total'] // 100
    parsed_data = {'product_article': article, 'product_name': product_name, 'product_price': product_price_actual}

    return parsed_data


if __name__ == "__main__":
    print(asyncio.run(parse_price(999999999)))
    print(asyncio.run(parse_price(100000001)))
    print(asyncio.run(parse_price(100000000)))
