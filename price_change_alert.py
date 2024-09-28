WB_PRODUCT_URL = 'https://www.wildberries.ru/catalog/'


async def price_change_alert(product_data, price_data):
    product_name = product_data['product_name']
    new_price = price_data[1]
    old_price = product_data['old_price']
    price_change = price_data[0]
    change_percentage = price_data[2]
    article = str(product_data['product_article'])
    user_id = product_data['user_id']
    message = (
        f'!!! Цена на ваш товар изменилась !!!\nТовар "{product_name}" стал {price_change}\n\nНовая цена - {new_price} ₽ '
        f'(Изменение цены {round(change_percentage)}%)\nСтарая цена - {old_price} ₽\n\n\n{WB_PRODUCT_URL + article + "/detail.aspx"}')
    return [user_id, message]
