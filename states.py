from aiogram.fsm.state import StatesGroup, State

class States(StatesGroup):
    waiting_article = State()
    finish_adding_article = State()
    waiting_article_for_delete = State()
    viewing_product_card = State()