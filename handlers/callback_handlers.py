import aiogram.types
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from states import States
from aiogram import F
from other_functions import create_product_card, messages_to_delete
import db
import asyncio

router = Router()


@router.callback_query(F.data == 'show_all_articles')
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery, state: FSMContext) -> None:
    all_products = await db.get_all_data_by_user_id(callback_query.from_user.id)

    builder = InlineKeyboardBuilder()
    for product in all_products:
        builder.button(text=f'{product['product_name']}', callback_data=f'{product['product_article']}')
    builder.button(text=f'Назад', callback_data='back_to_menu')

    builder.adjust(1, 1)
    await callback_query.message.edit_text(f'Ваши товары: ', reply_markup=builder.as_markup())
    await state.set_state(States.viewing_product_card)


@router.callback_query(F.data == 'back')
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    data = await db.get_all_data_by_user_id(callback_query.from_user.id)

    builder = InlineKeyboardBuilder()
    for product in data:
        builder.button(text=f'{product['product_name']}', callback_data=f'{product['product_article']}')

    builder.adjust(1, 1)
    await callback_query.message.edit_text(f'Выберите артикул товара', reply_markup=builder.as_markup())


@router.callback_query(F.data == 'back_to_menu')
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Показать мои товары', callback_data=f'show_all_articles')
    builder.button(text=f'Добавить товар для отслеживания', callback_data=f'add')
    await callback_query.message.edit_text(f'Что делаем?', reply_markup=builder.as_markup())


@router.callback_query(F.data == 'add')
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery, state: FSMContext) -> None:
    msg = await callback_query.message.answer(
        'Чтобы зарегистрировать товар для отслеживания его стоимости, отправьте его артикул\n\n'
        'Если вы хотите прервать процесс регистрации товара, отправьте команду ! /cancel !')
    messages_to_delete.append(msg)
    await state.set_state(States.waiting_article)


@router.callback_query(F.data.startswith('delete_'))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery, state: FSMContext) -> None:
    product_article = callback_query.data.replace('delete_', '')
    user_id = callback_query.from_user.id
    await db.delete_data_by_article(product_article, user_id)
    await callback_query.message.edit_text(f'Товар удален из базы данных')
    await asyncio.sleep(2)
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Показать мои товары', callback_data=f'show_all_articles')
    builder.button(text=f'Добавить товар для отслеживания', callback_data=f'add')
    await callback_query.message.edit_text(f'Что делаем?', reply_markup=builder.as_markup())
    await state.clear()


@router.callback_query(StateFilter(States.waiting_article_for_delete, States.viewing_product_card))
async def show_product_card(callback_query: aiogram.types.CallbackQuery, state: FSMContext) -> None:
    product_article = callback_query.data
    user_id = callback_query.from_user.id
    message = await create_product_card(product_article, user_id)
    builder = InlineKeyboardBuilder()
    if await state.get_state() == States.viewing_product_card:
        callback_data = 'back_to_menu'
    else:
        callback_data = 'back'
    builder.button(text=f'Удалить', callback_data=f'delete_{product_article}')
    builder.button(text=f'Назад', callback_data=f'{callback_data}')

    await callback_query.message.edit_text(text=message, reply_markup=builder.as_markup())
