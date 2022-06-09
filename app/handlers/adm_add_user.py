import sqlite3 as sql
from os import getenv
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class NewUser(StatesGroup):
    waiting_user_name = State()
    waiting_user_id = State()
    waiting_user_key = State()


async def add_user_name(message: types.Message, state: FSMContext):
    if message.from_user.id == int(getenv("ADMIN_ID")):
        await message.answer("Введите имя аккаунта нового пользователя")
        await NewUser.waiting_user_name.set()
    else:
        await message.answer("Вы не администратор!")
        await state.finish()


async def add_user_id(message: types.Message, state: FSMContext):
    if message.text[0] == "@":
        await state.update_data(name=message.text[1:])
    else:
        await state.update_data(name=message.text)
    await message.answer("Введите ID аккаунта нового пользователя")
    await NewUser.waiting_user_id.set()


async def add_user_key(message: types.Message, state: FSMContext):
    await state.update_data(id=message.text)
    await message.answer("Введите ключ для запросов нового пользователя")
    await NewUser.waiting_user_key.set()


async def add_new_user(message: types.Message, state: FSMContext):
    await state.update_data(key=message.text)
    user_information = await state.get_data()
    with sql.connect("verified_users.sqlite3") as con:
        cur = con.cursor()
    user_information = (user_information["name"], user_information["id"], user_information["key"])
    cur.execute(f"INSERT INTO users VALUES(?, ?, ?)", user_information)
    con.commit()
    await message.answer("Юзер успешно добавлен")
    await state.finish()


def register_handlers_adduser(dp: Dispatcher):
    dp.register_message_handler(add_user_name, commands="adm_add", state="*")
    dp.register_message_handler(add_user_id, state=NewUser.waiting_user_name)
    dp.register_message_handler(add_user_key, state=NewUser.waiting_user_id)
    dp.register_message_handler(add_new_user, state=NewUser.waiting_user_key)
