from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import filters
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types.web_app_info import WebAppInfo
import json
import aiohttp
import asyncio
from config import host, user, password, db_name, TOKEN_API, endpoint, url # импортируем из config переменные
import pymysql
from datetime import datetime

start_text = '''<i><b>Приветствую в мире разнообразных общений! Я твой бот, где ты сам выбираешь, с кем общаться. В моем виртуальном арсенале множество уникальных персонажей, каждый с собственным стилем, знаниями и характером.🧜🏽‍♀️

Чтобы начать приключение, просто скажи, с кем ты хочешь пообщаться. Можешь встретиться с Марио из Королевства Грибов, Эйнштейном с его гениальными идеями, и это далеко не все!🐢

Каждый персонаж готов ответить на твои вопросы, поговорить на различные темы или даже включиться в ролевую игру. Погрузись в разговор с тем, кто тебе интересен прямо сейчас! Если захочешь сменить атмосферу, просто выбери нового персонажа, и мы перенесемся в другой мир. Готов начать? Выбирай своего собеседника и погнали!🦹🏼‍♀️</b></i>'''
mario_text = '<i><b>Привет, дружище! Мама-мия, рад видеть тебя!\nЯ — Марио 🍄, герой из Королевства Грибов. Весело, что ты здесь!\nЕсли что-то нужно, не стесняйся спрашивать. Поехали к новым приключениям вместе!\nВперёд к звёздам!✨</b></i>'
enstain_text = '<i><b>Приветствую тебя, мой друг!\nЯ — Эйнштейн 🧠, и рад приветствовать умного человека. Помни, что фантазия важнее знания, и вопросы лучше ответов.\nДавайте вместе исследовать загадки вселенной и делиться идеями.\nПусть твой день будет таким же ярким, как свет идеи в моей голове!💡</b></i>'

def sql_add_user(user_id, username, name, surname, time):
    conn = None
    try:
        conn = pymysql.connect(
            host = host,
            port = 3306,
            user = user,
            password = password,
            database = db_name,
            cursorclass = pymysql.cursors.DictCursor
        )       
        # cur = conn.cursor
        with conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS users (user_id BIGINT PRIMARY KEY NOT NULL,
                        username TEXT,
                        name TEXT,
                        surname TEXT,
                        time DATETIME,
                        messages JSON)''') # Важно для user_id уточнить BIGINT потому что user_id в телеграме может быть больше максимально допустимого значения (2147483647) для INT
        try:               
            with conn.cursor() as cur:
                cur.execute(f'''INSERT INTO users (user_id, username, name, surname, time)
                VALUES (%s, %s, %s, %s, %s)''', (user_id, username, name, surname, time))
            conn.commit()
        except pymysql.IntegrityError as e:
            print(e)
    except Exception as ex:
        print(ex)
        print('ошибка здесь')
    finally:
        # Если соединение открыто, то закрываем его
        if conn != None:
            conn.close()



def sql_donwload_dialog(user_id):
    conn = None
    try:
        conn = pymysql.connect(
            host = host,
            port = 3306,
            user = user,
            password = password,
            database = db_name,
            cursorclass = pymysql.cursors.DictCursor
        )       
        # cur = conn.cursor
        with conn.cursor() as cur:
            cur.execute(f'''SELECT messages FROM users WHERE user_id = %s''', (user_id,))
            return cur.fetchone()
    except Exception as ex:
        print(ex)
    finally:
        # Если соединение открыто, то закрываем его
        if conn != None:
            conn.close()



def sql_add_dialog(user_id, messages):
    conn = None
    try:
        conn = pymysql.connect(
            host = host,
            port = 3306,
            user = user,
            password = password,
            database = db_name,
            cursorclass = pymysql.cursors.DictCursor
        )       
        # cur = conn.cursor                      
        with conn.cursor() as cur:
            cur.execute(f'''UPDATE users SET messages = %s WHERE user_id = %s''', (messages, user_id))
        conn.commit()
    except Exception as ex:
        print(ex)
    finally:
        # Если соединение открыто, то закрываем его
        if conn != None:
            conn.close()



async def fetch_completion(messages):
    messages = messages
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': messages,
    }
    data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, data=data) as response:
            return await response.json()



storage = MemoryStorage()
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)

class Dialogs(StatesGroup):
    mario = State()
    enstain = State()



def start_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Открыть веб страницу', web_app=WebAppInfo(url=url)))
    return kb



@dp.message_handler(commands=['start'], state='*')
async def start_command(message: types.Message, state: FSMContext):
    await state.reset_state()
    sql_add_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, datetime.now())
    await bot.send_message(message.from_user.id, text=start_text, reply_markup=start_keyboard(), parse_mode='HTML')



@dp.message_handler(commands=['menu'], state='*')
async def menu_command(message: types.Message, state: FSMContext):
    await state.reset_state()
    await bot.send_message(message.from_user.id, text=f'<i><b>Нажмите на кнопку чтобы выбрать персонажа🦖</b></i>', reply_markup=start_keyboard(), parse_mode='HTML')



@dp.message_handler(content_types=['web_app_data'], state='*')
async def wep_app(message: types.Message, state: FSMContext):
    user_choose = message.web_app_data.data
    if user_choose == 'mario':
        await bot.send_message(message.from_user.id, text=mario_text, parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
        await Dialogs.mario.set()
        sql_add_dialog(message.from_user.id, None) # важно сбросить историю диалога при смене персонажа
    elif user_choose == 'enstain':
        await bot.send_message(message.from_user.id, text=enstain_text, parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
        await Dialogs.enstain.set()
        sql_add_dialog(message.from_user.id, None)



@dp.message_handler(state=Dialogs.mario)
async def text_to_mario(message: types.Message, state: FSMContext):
    messages = sql_donwload_dialog(message.from_user.id)['messages']
    # если диалог пустой то мы создаем начальную инструкцию, если диалог продолжается то мы просто добавляем в него новое сообщение от пользователя
    if messages == None:
        messages = [
                {"role": "system", "content": "Instructions: Ты Марио"},
                {"role": "user", "content": message.text}
            ]
    else:
        messages = json.loads(messages)
        messages.append({"role": "user", "content": message.text})
    answer = await fetch_completion(messages)
    answer_message = answer['choices'][0]['message']
    messages.append(answer_message)
    string_messages = json.dumps(messages)
    sql_add_dialog(message.from_user.id, string_messages)
    await bot.send_message(message.from_user.id, text=f'<i><b>{answer_message["content"]}</b></i>', parse_mode='HTML')



@dp.message_handler(state=Dialogs.enstain)
async def text_to_enstain(message: types.Message, state: FSMContext):
    messages = sql_donwload_dialog(message.from_user.id)['messages']
    # если диалог пустой то мы создаем начальную инструкцию, если диалог продолжается то мы просто добавляем в него новое сообщение от пользователя
    if messages == None:
        messages = [
                {"role": "system", "content": "Instructions: Ты Альберт Эйнштейн"},
                {"role": "user", "content": message.text}
            ]
    else:
        messages = json.loads(messages)
        messages.append({"role": "user", "content": message.text})
    answer = await fetch_completion(messages)
    answer_message = answer['choices'][0]['message']
    messages.append(answer_message)
    string_messages = json.dumps(messages)
    sql_add_dialog(message.from_user.id, string_messages)
    await bot.send_message(message.from_user.id, text=f'<i><b>{answer_message["content"]}</b></i>', parse_mode='HTML')



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)