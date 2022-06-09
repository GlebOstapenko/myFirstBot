from os import getenv
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext



async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Выберите, одно из действий: \n"
        "Курс валют - /currency\n"
        "Баланс одной из ваших касс - /balance",
        reply_markup=types.ReplyKeyboardRemove()
    )


async def cmd_adm_menu(message: types.Message, state: FSMContext):
    if message.from_user.id == int(getenv("ADMIN_ID")):
        await state.finish()
        await message.answer(
            "Админ меню: \n"
            "Добавить пользователя - /adm_add\n",
            reply_markup=types.ReplyKeyboardRemove()
        )


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())



def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_start, commands=" menu", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_adm_menu, commands="adm", state="*")
