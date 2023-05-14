import sqlite3 as sq
from aiogram import Bot, Dispatcher, executor, types
from api import ID

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


bot = Bot(ID)
dp = Dispatcher(bot)

pk = '''Admin bot DELIVERY
/help
/orders - Заказы
/Назначить - Пишется /Назначить и указывается время - пример:/Назначить 11(время устанавливается на одну волну)
/info_now - Информация о волнах на сегодня
/close_wave - Закрывает волну  - пример:/close_wave 11 (удаляется только одна волка)
/close_all_wave - Закрыть все волны

/Stores - Список доступных магазинов к доставке
/insert_store - внести магазин в список доступных к доставке магазинов
/CloseShop - Закрыть магазин пример: /CloseShop Пятерочка
'''

ml = '''Бот настраивает волны и список доступных магазинов
'''


async def on_startup(_):
    print('Бот успешно включен, обновления, полученные в оффлайн режиме, были пропущены')


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.delete()
    await message.answer(pk, parse_mode='HTML')


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.delete()
    await message.answer(ml)


@dp.message_handler(commands=["Назначить"])
async def enter_waves(message: types.Message):
    waves = int(message.text[10:])
    if waves < 0 or waves > 24:
            await message.answer(f"Недопустимое значение: {w}. Значения должны быть в диапазоне от 0 до 24.")
            return
    cur.execute("INSERT INTO waves (today, waves) VALUES (NULL, ?)", (waves,))
    sq_con.commit()
    await message.answer('Данные внесены')


@dp.message_handler(commands=['info_now'])
async def info_waves(message: types.Message):
    await message.delete()
    waves = cur.execute('SELECT waves FROM waves').fetchall()
    waves = [str(wave) for wave in waves]
    waves = ''.join(waves)
    waves = waves.replace('(', ' ').replace(')', ' ')
    await message.answer(f"Доступные на сегодня волны для регистрации заказов:{waves}")


@dp.message_handler(commands=['close_wave'])
async def close_wave(message: types.Message):
    wave = int(message.text[11:])
    if wave < 0 or wave > 24:
        await message.answer(f'Недопустимое значение {wave}')
    cur.execute(f'DELETE FROM waves WHERE waves = {wave}')
    await message.answer('Волна закрыта')


@dp.message_handler(commands=['close_all_wave'])
async def close_wave(message: types.Message):
    await message.delete()
    cur.execute(f'DELETE FROM waves')
    await message.answer('Волны закрыты')


@dp.message_handler(commands=['insert_store'])
async def insert_wave(message: types.Message):
    store = message.text[14:]
    cur.execute(f'INSERT INTO stores (store) VALUES ("{store}") ')
    sq_con.commit()
    await message.answer('Магазин внесен в список', parse_mode='HTML')


@dp.message_handler(commands=['Stores'])
async def close_wave(message: types.Message):
    await message.delete()
    stores = cur.execute('SELECT store FROM stores ORDER BY store DESC').fetchall()
    stores = [store[0] for store in stores]
    stores = ', '.join(stores)
    await message.answer(f'список доступных магазинов: {stores}')


@dp.message_handler(commands=['orders'])
async def all_orders(message: types.Message):
    await message.delete()
    orders = cur.execute("SELECT * FROM orders ORDER BY wave").fetchall()
    for order in orders:
        order_id = order[0]
        customer_name = order[1]
        order_date = order[2]
        await message.answer(f"Волна: {order_id} Имя: {customer_name} Телефон: {order_date}")


@dp.message_handler(commands=['CloseShop'])
async def close_shop(message: types.Message):
    await message.delete()
    shop = message.text[11:]
    shops = cur.execute('SELECT store FROM stores').fetchall()
    shops = [shop1[0] for shop1 in shops]
    if shop in shops:
        cur.execute(f'DELETE FROM stores WHERE store = ("{shop}")')
        await message.answer('Магазин удален')
        return
    else:
        await message.answer('Магазина не существует')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)