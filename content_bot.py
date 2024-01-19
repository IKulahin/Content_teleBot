import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
import asyncio
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

bot = Bot('YOUR_API_TOKEN')


class MyState(StatesGroup):
    wait_content = State()
    wait_finding = State()


def creating_table():
    """Creating the table for content in the Database"""
    connect = sqlite3.connect('bot_db.sqlite3')
    cur = connect.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS Contents(
        id INTEGER PRIMARY KEY,
        content VARCHAR(255));""")
    connect.close()


creating_table()
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message):
    """Starting default func"""
    await message.answer('Привіт! Я контент-бот, виберіть записати чи знайти контент за номером')


@dp.message(MyState.wait_content)
async def add_content(message: types.Message, state: FSMContext):
    """This function add received content to table in database"""
    await state.clear()
    content = message.text
    connect = sqlite3.connect('bot_db.sqlite3')
    cur = connect.cursor()
    cur.execute(f'''INSERT INTO Contents (content) VALUES(
                "{content}"
                );'''
                )
    connect.commit()
    connect.close()
    await message.answer(f'Контент додано за кодом: {cur.lastrowid}')


@dp.message(MyState.wait_finding)
async def finding_content(message: types.Message):
    """This function find content, which was searched by user"""
    searching = message.text
    connect = sqlite3.connect('bot_db.sqlite3')
    cur = connect.cursor()
    result = cur.execute(f"""SELECT * FROM Contents WHERE id = ?""", (searching,))
    row = result.fetchone()
    if row:
        await message.answer(f'Ось контент за вашим кодом: \n{row[1]}')
    else:
        await message.answer('Не знайдено контенту за наданим кодом')


@dp.message(Command('add'))
async def wait_add(message: types.Message, state: FSMContext):
    """Calling the add_content function"""
    await state.set_state(MyState.wait_content)
    await message.answer('Введіть текст, який отримає унікальний код')


@dp.message(Command('find'))
async def wait_finding(message: types.Message, state: FSMContext):
    """Calling the finding_content function"""
    await state.set_state(MyState.wait_finding)
    await message.answer('Введіть код, за яким хочете отримати контент')


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
