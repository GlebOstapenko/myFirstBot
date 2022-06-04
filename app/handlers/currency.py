from requests import request
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

available_currency = request("GET", "https://api.interkassa.com/v1/currency").json()



class Currency(StatesGroup):
    waiting_currency1 = State()
    waiting_currency2 = State()





async def get_currency_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for name in available_currency["data"]:
        keyboard.add(name)
    await message.answer("Выберите валюту для обмена:", reply_markup=keyboard)
    await Currency.waiting_currency1.set()


# Обратите внимание: есть второй аргумент
async def currency1_chosen(message: types.Message, state: FSMContext):
    if message.text not in available_currency["data"]:
        await message.answer("Пожалуйста, выберите валюту, используя клавиатуру ниже.")
        return
    await state.update_data(chose_currency1=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    user_data = await state.get_data()
    available_currency["data"][user_data['chose_currency1']].pop("id")
    for size in available_currency["data"][user_data['chose_currency1']]:
        keyboard.add(size)
    await Currency.next()
    await message.reply("Теперь выберите вторую валюту :", reply_markup=keyboard)


async def currency2_chosen(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text not in available_currency["data"][user_data['chose_currency1']]:
        await message.answer("Пожалуйста, выберите валюту, используя клавиатуру ниже.")
        return
    await state.update_data(chose_currency2=message.text)
    user_data = await state.get_data()
    exchange_rates = request("GET", "https://api.interkassa.com/v1/currency").json()
    exchange_rates = exchange_rates["data"][user_data['chose_currency1']][user_data['chose_currency2']]
    await message.answer(f"Курс обмена {user_data['chose_currency1']} на {user_data['chose_currency2']}:\n"
                         f"Покупка - {exchange_rates['in']}\n"
                         f"Продажа - {exchange_rates['out']}", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()




def register_handlers_currency(dp: Dispatcher):
    dp.register_message_handler(get_currency_start, commands="currency", state="*")
    dp.register_message_handler(currency1_chosen, state=Currency.waiting_currency1)
    dp.register_message_handler(currency2_chosen, state=Currency.waiting_currency2)

