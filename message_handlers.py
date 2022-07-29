import logging
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.executor import start_webhook
from database import session as db
from models import Event
from client_bot import states
from config import client_bot, dp, service_bot, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL
# Инициализируем бота
from client_bot.payments import Payment
from client_bot.resource import mess_info, mess_start, mess_usually_post, mess_for_em, mess_for_complete, m1
from client_bot.states import ChatMode

id_channel = '@fortestingworkforkyiv'
channel_for_work = '@RobochiyKyiv'
admin = '5529025977'


@dp.message_handler(commands="start", state=None)
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    newpost = types.KeyboardButton("Новий пост")
    markup.add(newpost)
    await message.answer(mess_start, reply_markup=markup, parse_mode='html')


@dp.message_handler(commands="info", state=None)
async def command_info(message: types.Message):
    await message.answer(mess_info, parse_mode='html')


@dp.message_handler(content_types=['text'], state=None)
async def bot_message(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if message.chat.type == 'private':
        if message.text == 'Новий пост':
            item1 = types.KeyboardButton("Захищений")
            item2 = types.KeyboardButton("Звичайний")
            back = types.KeyboardButton("Назад")
            markup.add(item1, item2, back)
            mess = 'У Вас є можливість створити <b>Захищений поcт</b> або <b>Звичайний</b>'
            await message.answer(mess, parse_mode='html', reply_markup=markup)
        if message.text == 'Захищений':

            item = types.KeyboardButton("Назад")
            markup.add(item)
            mess = 'Оберіть, будь ласка, <b>галузь</b> роботи'
            await message.answer(mess, parse_mode='html', reply_markup=markup)
            await states.Test.Q1.set()

        elif message.text == "Назад":

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            newpost = types.KeyboardButton("Новий пост")
            markup.add(newpost)
            await message.answer('Назад', parse_mode='html', reply_markup=markup)
        elif message.text == 'Опублікувати звичайний пост':

            await message.answer(m1, parse_mode='html', reply_markup=markup)

        elif message.text == 'Звичайний':

            item1 = types.KeyboardButton("Назад")
            item = types.KeyboardButton("Я готовий ризикнути")
            markup.add(item, item1)
            await message.answer(mess_usually_post, parse_mode='html', reply_markup=markup)

        elif message.text == 'Я готовий ризикнути':

            item = types.KeyboardButton("Назад")
            markup.add(item)
            mess = 'Оберіть, будь ласка, <b>галузь</b> роботи'
            await message.answer(mess, parse_mode='html', reply_markup=markup)
            await states.Test.pr_branch.set()


@dp.message_handler(content_types=['text'], text="Оплата", state=ChatMode.ChatId)
async def bot_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        salary = data['price']
        event_id = data['event']
    # print("salary")
    # print(salary)
    # print("event_id")
    # print(event_id)
    event = Event.get(event_id)
    # print('event')
    # print(event)
    price = (float(salary) + (float(salary) * 0.09))
    percent = (float(salary) * 0.09)
    order_id = event.id
    # print(order_id)
    # print('order')
    markup = types.InlineKeyboardMarkup()
    p = Payment()
    url = Payment.generate_new_url_for_pay(p, order_id, price)
    button_check_event = types.InlineKeyboardButton(
        "Оплатити",
        url=url)
    markup.add(button_check_event)

    mess = f"Відповідно до встановленої вами ціни, оплата за виконання завдання складає: {salary}" \
           f"\nКомісія сервісу становить: {percent}" \
           f"\nЩоб оплатити роботу скористайтесь українським порталом е-комерції, натиснувши кнопку «Оплатити» нижче:"
    await message.answer(mess, reply_markup=markup)


@dp.message_handler(content_types=['text'], text="Готово", state=ChatMode.ChatId)
async def bot_complete(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    button_check_event = types.InlineKeyboardButton("Так", callback_data="complete")
    markup.add(button_check_event)
    await message.answer(mess_for_complete, reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data[:8] == "complete", state=ChatMode.ChatId)
@dp.callback_query_handler(lambda c: c.data[:8] == "complete")
async def process_enter_chat(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        user_name = data['user']
        event_id = data['event']
        chat_id = data['ChatId']
        event = Event.get(event_id)
        order_id = event.id
        # print("name")
        # print(user_name)
        # print("event_id")
        # print(event_id)
        await client_bot.send_message(
            admin,
            f'Підтвердежена оплата: id-замовлення {order_id} робітник- @{user_name}',

        )
        await client_bot.send_message(
            channel_for_work,
            f'Виконано:  \n{event.name}\n\n{event.description}\n\nЦіна:{event.salary} '
            f'\n#Захищенийпост')
        await client_bot.send_message(message.from_user.id, 'Підтвержено виконання роботи, можете завершувати розмову')
        await service_bot.send_message(chat_id, 'Підтвержено виконання роботи, можете завершувати розмову')



@dp.message_handler(content_types=['text'], text="Підтвердити оплату", state=ChatMode.ChatId)
async def bot_success(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        event_id = data['event']
        chat_id = data['ChatId']
    event = Event.get(event_id)
    order_id = event.id
    p = Payment()
    markup = types.ReplyKeyboardMarkup()
    button_exit = types.KeyboardButton("Вийти з чату")
    markup.add(button_exit)
    if Payment.get_order_status_from_liqpay(p, order_id):
        await message.answer(f"Оплата підтверджена")
        await service_bot.send_message(chat_id, mess_for_em)
    else:
        markup = types.ReplyKeyboardMarkup()
        success = types.KeyboardButton("Підтвердити оплату")
        markup.add(success)
        await message.answer(f"Оплата не підтверджена", reply_markup=markup)


@dp.message_handler(content_types=['text'], text="Опублікувати захищений пост", state=states.Test.post)
async def bot_post(message: types.Message, state: FSMContext):
    data = await state.get_data()
    branch = data.get("answer1")
    details = data.get("answer2")
    price = data.get("answer3")
    event = Event(
        name=branch,
        description=details,
        salary=price,
        creator_id=message.from_user.id
    )
    db.add(event)
    db.commit()
    await message.answer(m1, parse_mode='html')
    mess = f'🔵 Активно  \n{branch}\n\n{details}\nЦіна:{price} \n#Захищенийпост'
    markup = types.InlineKeyboardMarkup()
    button_check_event = types.InlineKeyboardButton(
        "Зв'язатися",
        url=f'https://t.me/ChatForWorkKyivBot/?start=test{message.from_user.id}_e{event.id}')
    markup.add(button_check_event)
    await message.answer(mess)
    post_message = await client_bot.send_message(id_channel, mess, reply_markup=markup)
    event.message_id = post_message.message_id
    db.commit()
    await state.finish()


@dp.message_handler(content_types=['text'], text="Опублікувати звичайний пост", state=states.Test.pr_post)
async def bot_post(message: types.Message, state: FSMContext):
    data = await state.get_data()
    branch1 = data.get("pr1")
    details1 = data.get("pr2")
    price1 = data.get("pr3")
    print(branch1)
    print(details1)
    print(price1)
    await message.answer(m1, parse_mode='html')
    mess = f'🔵 Активно  \n{branch1}\n\n{details1}\nЦіна:{price1} \nПисати: @{message.from_user.username}'
    await message.answer(mess)
    await client_bot.send_message(id_channel, mess)
    await state.finish()


@dp.message_handler(state=states.Test.Q1)
async def answer_branch(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(answer1=answer)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item = types.KeyboardButton("Назад")
    markup.add(item)
    await message.answer(
        'Максимально детально <b>опишіть</b> роботу',
        parse_mode='html',
        reply_markup=markup
    )
    await states.Test.next()


@dp.message_handler(state=states.Test.pr_branch)
async def answer_branch(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(pr1=answer)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item = types.KeyboardButton("Назад")
    markup.add(item)
    await message.answer(
        'Максимально детально <b>опишіть</b> роботу',
        parse_mode='html',
        reply_markup=markup
    )
    await states.Test.next()


@dp.message_handler(state=states.Test.pr_details)
async def answer_branch(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(pr2=answer)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item = types.KeyboardButton("Назад")
    markup.add(item)
    mess = 'Напишіть <b>ціну</b> роботи'
    await message.answer(mess, parse_mode='html', reply_markup=markup)
    await states.Test.next()


@dp.message_handler(state=states.Test.pr_price)
async def answer_branch(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(pr3=answer)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item = types.KeyboardButton("Назад")
    item1 = types.KeyboardButton("Опублікувати звичайний пост")
    markup.add(item1, item)
    mess = 'Готово'
    await message.answer(mess, parse_mode='html', reply_markup=markup)
    await states.Test.next()


@dp.message_handler(state=states.Test.Q2)
async def answer_branch(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(answer2=answer)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item = types.KeyboardButton("Назад")
    markup.add(item)
    mess = 'Напишіть <b>ціну</b> роботи'
    await message.answer(mess, parse_mode='html', reply_markup=markup)
    await states.Test.next()


@dp.message_handler(state=states.Test.Q3)
async def answer_branch(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(answer3=answer)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item = types.KeyboardButton("Назад")
    item1 = types.KeyboardButton("Опублікувати захищений пост")
    markup.add(item1, item)
    mess = 'Готово'
    await message.answer(mess, parse_mode='html', reply_markup=markup)
    await states.Test.next()


@dp.callback_query_handler(lambda c: c.data[:7] == "user_id", state=ChatMode.ChatId)
@dp.callback_query_handler(lambda c: c.data[:7] == "user_id")
async def process_enter_chat(callback_query: CallbackQuery, state: FSMContext) -> None:
    await ChatMode.ChatId.set()
    user_id = callback_query.data[7:]
    print(user_id)
    async with state.proxy() as data:
        data['ChatId'] = user_id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    exit_b = types.KeyboardButton("Вийти з чату")
    markup.add(exit_b)
    await client_bot.send_message(
        callback_query.from_user.id, 'Ви війшли в режим чату', reply_markup=markup)
    await client_bot.send_message(
        callback_query.from_user.id, 'Напишіть ваше повідомлення')


@dp.callback_query_handler(lambda c: c.data[:9] == "yes_price", state=ChatMode.ChatId)
@dp.callback_query_handler(lambda c: c.data[:9] == "yes_price")
async def process_no_chat(callback_query: CallbackQuery, state: FSMContext) -> None:
    await ChatMode.price.set()
    await ChatMode.user.set()
    await ChatMode.event.set()
    user, price, event_id = re.match(r'^yes_price(\w*)_e(\d*)_i(\d*)$', callback_query.data).groups()
    async with state.proxy() as data:
        chat_id = data['ChatId']
    async with state.proxy() as data:
        data['price'] = price
        data['user'] = user
        data['event'] = event_id
    print('event id')
    print(event_id)
    # chat = callback_query.data[9:]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    salary = types.KeyboardButton("Оплата")
    success = types.KeyboardButton("Підтвердити оплату")
    exit_button = types.KeyboardButton("Вийти з чату")
    complete_button = types.KeyboardButton("Готово")
    markup.add(salary, success, exit_button, complete_button)
    await client_bot.send_message(
        callback_query.from_user.id,
        'Тепер Ви можете оплатити, після оплати натисніть кнопку "Підтвердити оплату"',
        reply_markup=markup
    )
    # await service_bot.send_message(chat_id, f'Ціна не була підтверджена \n\nВід: @{message.from_user.username}')
    await ChatMode.ChatId.set()
    await service_bot.send_message(chat_id, f'Ціна була підтверджена')


@dp.message_handler(state=ChatMode.ChatId)
async def state_chatid(message: types.Message, state: FSMContext):
    if message.text == 'Вийти з чату':
        await state.finish()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        newpost = types.KeyboardButton("Новий пост")
        markup.add(newpost)
        return await message.answer('Ви завершили розмову', reply_markup=markup)
    async with state.proxy() as data:
        chat_id = data['ChatId']
    if message.text != 'Оплата':
        if message.text != 'Підтвердити оплату':
            mess = f'Вам прийшло повідомлення:\n\n{message.text} \n\nВід: @{message.from_user.username}'
            return await service_bot.send_message(
                chat_id, mess)



async def on_startup(dp):
    await client_bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await client_bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')

print(WEBHOOK_PATH)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )

