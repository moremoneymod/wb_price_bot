from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import States
from price_parser import parse_price
from aiogram.utils.keyboard import InlineKeyboardBuilder

import db
from other_functions import is_valid_article, delete_message, delete_messages, messages_to_delete

router = Router()


@router.message(Command('start'))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        'Данный бот отслеживает изменение стоимости товаров, артикулы которых вы сюда добавите\n\n'
        'Чтобы начать работу с ботом, используйте команду ! /menu !')


@router.message(Command('help'))
async def command_help(message: Message) -> None:
    await message.answer(
        'Данный бот отслеживает изменение стоимости товаров, артикулы которых вы сюда добавите\n\n'
        'Чтобы начать работу с ботом, используйте команду ! /menu !\n\n'
        'Чтобы удалить товар, нужно перейти в пункт "Показать мои товары" -> Выбрать товар, который вы хотите удалить -> '
        'Нажать кнопку "Удалить"')


@router.message(Command('menu'))
async def command_articles(message: Message) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Показать мои товары', callback_data=f'show_all_articles')
    builder.button(text=f'Добавить товар для отслеживания', callback_data=f'add')
    await message.answer(f'Что делаем?', reply_markup=builder.as_markup())


@router.message(StateFilter(States.waiting_article, States.waiting_article_for_delete), Command('cancel'))
async def cancel_registration(message: Message, state: FSMContext) -> None:
    msg = await message.answer('Процесс регистрации товара отменен')
    await delete_message(message)
    await delete_message(msg, 2)
    await delete_messages()
    await state.clear()


@router.message(StateFilter(States.waiting_article))
async def add_product_to_db(message: Message, state: FSMContext) -> None:
    product_article = message.text
    if await is_valid_article(product_article) is False:
        msg = await message.answer(
            'Вы прислали неверный артикул либо товара нет в наличии\n\nЕсли вы хотите прервать процесс регистрации товара, отправьте команду ! /cancel !')
        await state.set_state(States.waiting_article)
        await delete_message(message, 1)
        await delete_message(msg, 3)
    else:
        user_id = message.from_user.id
        product_article = int(message.text)

        if await db.check_article_in_db_by_user_id(product_article, user_id):
            msg = await message.answer('Товар уже зарегистрирован для отслеживания стоимости')
            await delete_message(message, 1)
            await delete_message(msg, 3)
            return

        product_data = await parse_price(product_article)

        product_name = product_data['product_name']
        old_price = product_data['product_price']
        new_price = product_data['product_price']
        first_price = product_data['product_price']

        msg = await message.answer('Товар зарегистрирован для отслеживания стоимости')
        messages_to_delete.append(msg)
        messages_to_delete.append(message)
        await db.add_product_to_db(product_article, user_id, product_name, new_price, old_price, first_price)
        await state.clear()
        await delete_messages()


@router.message()
async def echo_handler(message: Message) -> None:
    await message.delete()
