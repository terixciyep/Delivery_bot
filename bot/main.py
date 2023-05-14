from aiogram import Bot, Dispatcher,types, executor
from API1 import ID
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import sqlite3 as sq
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import state
from aiogram import Bot


storage = MemoryStorage()

bot = Bot(ID)
dp = Dispatcher(bot, storage=storage)

with sq.connect("waves.db") as sq_con:
    cur = sq_con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS waves (
        today INTEGER PRIMARY KEY AUTOINCREMENT,
        waves INTEGER check(waves BETWEEN 0 AND 24)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS stores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        store TEXT
    )""")
    cur.execute('''CREATE TABLE IF NOT EXISTS orders (
        wave INTEGER,
        name TEXT,
        phone INTEGER
    )''')


START_COMMAND ='''<b>Доставка ГУУ</b>

<b>/Order</b> - Сделать заказ    
    
<b>/waves</b> - волны на сегодня

<b>/shops</b> - доступные магазины
'''


class MainStates(state.StatesGroup):
    first = state.State()
    second = state.State()
    third = state.State()


order = []


async def on_startup(_):
    print('Бот успешно включен, обновления, полученные в оффлайн режиме, были пропущены')


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.delete()
    await message.answer(START_COMMAND, parse_mode='HTML')


@dp.message_handler(commands=['waves'])
async def waves_info(message: types.Message):
    await message.delete()
    waves = cur.execute('SELECT waves FROM waves').fetchall()
    waves = [str(wave) for wave in waves]
    waves = ''.join(waves)
    waves = waves.replace('(', ' ').replace(')', ' ')
    await message.answer(f"Доступные на сегодня волны для регистрации заказов:{waves}")


@dp.message_handler(commands=['Order'])
async def order_command(message: types.Message, state: FSMContext):
    await message.delete()
    ko = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=3)
    keys = cur.execute('SELECT waves FROM waves ORDER BY waves DESC').fetchall()
    keys = [key[0] for key in keys]
    for i in keys:
        ko.add(KeyboardButton(i))
    print(keys)
    await message.answer('Выберите время', parse_mode='HTML', reply_markup=ko)
    await MainStates.first.set()


@dp.message_handler(state=MainStates.first)
async def wave_set_order(message: types.Message, state: FSMContext):
    order.append(message.text)
    print(order)
    await message.answer('Введите ваше имя', parse_mode='HTML')
    await MainStates.second.set()


@dp.message_handler(state=MainStates.second)
async def name_set_order(message: types.Message, state: FSMContext):
    order.append(message.text)
    await message.answer('Теперь введите ваш номер телефона', parse_mode='HTML')
    await MainStates.third.set()


@dp.message_handler(state=MainStates.third)
async def name_set_order(message: types.Message, state: FSMContext):
    global order
    order.append(message.text)
    print(order)
    await state.finish()
    await message.answer('Ваша очередь зарегистрирована, ожидайте звонка курьера!')
    await bot.send_message('courier id',order[2])
    cur.execute(f"INSERT INTO orders(wave, name, phone) VALUES (?, ?, ?)", (order[0], order[1], order[2]))
    sq_con.commit()
    order = []


@dp.message_handler(commands=['shops'])
async def shops_list(message: types.Message):
    shops = cur.execute('SELECT store FROM stores').fetchall()
    shops = [shop[0] for shop in shops]
    shops = ', '.join(shops)
    await message.answer(f'Сегодняшняя доставка работает в магазинах {shops}')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)