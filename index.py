import logging
from datetime import datetime
import time
import sqlite3 as sq
import sqlite3
from datetime import date
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
import requests
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from time import sleep
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

storage = MemoryStorage()


bot = Bot(token="5613305399:AAFp9Cjwa6cQbvjw-rMOjwkCtExyJeLXe5g")

dp = Dispatcher(bot,storage=storage)

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


ID = '398909147'

async def on_startup(_):
    print('Бот вышел в онлайн')
    global base, cur
    base = sq.connect('main.db')
    cur = base.cursor()
    time = 0.1
    if base:
        print('Data base connected OK!')
    base.execute(
            "CREATE TABLE IF NOT EXISTS info(id INTEGER, datatime REAL, name TEXT, phone INTEGER,PRIMARY KEY(id AUTOINCREMENT))")
    [var_last,] = cur.execute('SELECT max(id) FROM info').fetchone()
    print(f"var_last = {var_last}")
    base.commit()
    while True:
        base = sq.connect('main.db')
        cur = base.cursor()
        [var_max,] = cur.execute('SELECT max(id) FROM info').fetchone()
        base.commit()
        print(f"var_max = {var_max}")



        if var_last!=var_max:
            [var_new,] = cur.execute("SELECT datatime,name,phone FROM info WHERE id = ?",(var_max,))
            base.commit()
            print("True")
            await bot.send_message(ID,f"Строка с id = {var_max}\ndatatime = {var_new[0]}\nname = {var_new[1]}\nphone = {var_new[2]}")
            var_last = var_max
        else:
            print("False")
        sleep(time * 60)



@dp.message_handler(commands='add')
async def add_func(message: types.Message):
    string1 = message.text
    string2 = string1[:0]+string1[4:]
    string2 = string2.strip()
    strings = string2.split(';')
    dat = datetime.strptime(strings[0],"%d.%m.%Y") #%H:%M:%S
    # timestamp = strings[0]
    # value = datetime.fromtimestamp(timestamp)
    #print(value.strftime('%Y-%m-%d %H:%M:%S'))
    sqlite_insert = """INSERT INTO info(datatime,name,phone) VALUES(?,?,?)"""
    data_tuple = (dat, strings[1], strings[2])
    cur.execute(sqlite_insert, data_tuple)
    base.commit()
    [var_id,] = cur.execute('SELECT max(id) FROM info').fetchone()
    base.commit()
    if (strings[2]):
        await bot.send_message(message.chat.id,f"Строка с id = {var_id} создана")




@dp.message_handler(commands='del')
async def del_func(message: types.Message):
    string1 = message.text
    string2 = string1[:0] + string1[4:]
    string2 = string2.strip()
    sqlite_delete = """DELETE FROM info WHERE id = ?"""
    data_tuple = (string2,)
    cur.execute(sqlite_delete, data_tuple)
    base.commit()
    await bot.send_message(message.chat.id, f"Строка с id = {string2} удалена")



@dp.message_handler(commands='sel')
async def sel_func(message: types.Message):
    string1 = message.text
    string2 = string1[:0] + string1[4:]
    string2 = string2.strip()
    [sqlite_sel,] = cur.execute("SELECT datatime,name,phone FROM info WHERE id = ?",(string2,))
    base.commit()
    await bot.send_message(message.chat.id, f"Строка с id = {string2}\ndatatime = {sqlite_sel[0]}\nname = {sqlite_sel[1]}\nphone = {sqlite_sel[2]}")



@dp.message_handler(commands='help')
async def help_func(message: types.Message):
    await bot.send_message(message.chat.id,
                           f"Для того, чтобы добавить новую запись в бд используйте команду /add - далее ставите пробел и перечисляете дату,имя и номер телефона через <<;>> Пример - /add 01-01-2022;Иван;8918000000\n"
                           f"Для того, чтобы удалить запись из бд используйте команду /del - ставите пробел и пишите id. Пример - /del 5\n"
                           f"Для того, чтобы посмотреть нужную строчку из бд - используйте команду /sel - ставите пробел и пишите id. Пример - /sel 5")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)