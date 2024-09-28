from aiogram import Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram import Bot, Dispatcher, html
from aiogram.fsm.context import FSMContext
from states import States
from price_parser import parse_price
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder

import db
from other_functions import is_valid_article

router = Router()


@router.message(StateFilter(States.waiting_article, States.waiting_article_for_delete), Command('cancel'))
async def cancel_registration(message: Message, state: FSMContext) -> None:
    await message.answer('Процесс регистрации товара отменен')
    print(F.text)
    await state.clear()


@router.message(StateFilter(States.waiting_article))
async def add_product_to_db(message: Message, state: FSMContext) -> None:
    product_article = message.text

    if await is_valid_article(product_article) is False:
        await message.answer(
            'Вы прислали неверный артикул\n\nЕсли вы хотите прервать процесс регистрации товара, отправьте команду ! /cancel !')
        await state.set_state(States.waiting_article)

    else:
        user_id = message.from_user.id
        product_article = int(message.text)

        if await db.check_article_in_db_by_user_id(product_article, user_id):
            await message.answer('Товар уже зарегистрирован для отслеживания стоимости')
            return

        product_data = await parse_price(product_article)

        product_name = product_data['product_name']
        old_price = product_data['product_price']
        new_price = product_data['product_price']
        first_price = product_data['product_price']

        print(user_id, product_article, product_name, product_article, old_price, new_price)

        await message.answer('Товар зарегистрирован для отслеживания стоимости')

        await db.add_product_to_db(product_article, user_id, product_name, new_price, old_price, first_price)
        await state.clear()
