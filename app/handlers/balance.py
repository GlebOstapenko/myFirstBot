import sqlite3 as sql
import requests
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class Balance(StatesGroup):
    waiting_checkout_id = State()


# Получаем ключ для запроса по API из БД
def get_key(user_name="", user_id=""):
    with sql.connect("verified_users.sqlite3") as con:
        cur = con.cursor()
    cur.execute(f"SELECT rowid, * FROM users WHERE user_id == '{user_id}' ")
    cur.execute(f"SELECT rowid, * FROM users WHERE user_name == '{user_name}' ")
    results = cur.fetchall()
    if len(results) != 0:
        return results[0][3]
    else:
        return "Error"


# Возвращает список касс на подключённом аккаунте
def get_checkouts(key):
    params = dict(Authorization=key)
    res = requests.get("https://api.interkassa.com/v1/purse", headers=params).json()
    print(res)
    if "Auth: forbidden for current ip" in res.items():
        return "Bad ip"
    result = {}
    for elem in res["data"]:
        checkout_name = res["data"][elem]["name"][0:-4]
        checkout_id = res["data"][elem]["settings"]["co"]
        result.update({checkout_name: checkout_id})
    return result


# Возвращает актуальные балансы по кассе на момент запроса (выбора кассы на клавиатуре)
def get_balance(checkout_id, key):
    params = dict(Authorization=key)
    res = requests.get("https://api.interkassa.com/v1/purse", headers=params).json()
    msg_balance = f"Баланс по кассе {checkout_id}\n"
    for elem in res["data"]:
        if res["data"][elem]["settings"]["co"] == checkout_id:
            curr = res["data"][elem]["name"][-3:]
            balance = res["data"][elem]["balance"]
            msg_balance += curr + "\n" + balance + "\n"
            if res["data"][elem]["frozen"] != "0.0000":
                frozen = res["data"][elem]["frozen"]
                msg_balance += frozen + "\n"
            msg_balance += "\n"
    return msg_balance


async def get_currency_start(message: types.Message, state: FSMContext):
    # Получаем ключ для запроса по API
    await state.update_data(key=get_key(message.from_user.username, message.from_user.id))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Если пользователь по имени аккаунта или ID не добавлен в whitelist выдаёт "ошибку/рекомендацию"
    if (await state.get_data("key"))["key"] == "Error":
        await message.answer("Для активации данного функционала необходимо написать в поддержку",
                             reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    # Если пользователь добавлен в базу то происходи запрос информации
    else:
        checkout_list = get_checkouts((await state.get_data("key"))["key"])
        # В личнои кабинете могли не добавить IP с которого бот отправляет запрос
        if checkout_list == "Bad ip":
            await message.answer(f"В личном кабинете необходимо добавить IP в список доступных",
                                 reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
        # IP добавлен и запрос успешно обработан и получен список активных касс
        else:
            await state.update_data(checkout_list=checkout_list)
            for name in checkout_list:
                keyboard.add(name)
            await message.answer("Выберите кассу для проверки баланса:", reply_markup=keyboard)
            await Balance.waiting_checkout_id.set()


async def get_currency_final(message: types.Message, state: FSMContext):
    # Проверка, вдруг пользователь решил ввести данные кассы вручную вручную
    user_data = await state.get_data()
    if message.text not in user_data["checkout_list"]:
        await message.answer("Пожалуйста, выберите кассу, используя клавиатуру ниже.")
        return
    # Отправляет сообщение с актуальными балансами
    user_data = await state.get_data()
    await message.answer(get_balance(user_data['checkout_list'][message.text], user_data['key']),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


def register_handlers_balance(dp: Dispatcher):
    dp.register_message_handler(get_currency_start, commands="balance", state="*")
    dp.register_message_handler(get_currency_final, state=Balance.waiting_checkout_id)
