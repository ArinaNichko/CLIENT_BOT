from aiogram.dispatcher.filters.state import StatesGroup, State


class Test(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()
    post = State()
    pr_branch = State()
    pr_details = State()
    pr_price = State()
    pr_post = State()


class ChatMode(StatesGroup):
    ChatId = State()
    price = State()
    user = State()
    event = State()
