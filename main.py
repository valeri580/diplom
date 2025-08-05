import telebot
import random
import os
from dotenv import load_dotenv
import requests
import json

# Загружаем переменные окружения из .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    raise RuntimeError("Ошибка: Токен Telegram-бота не найден. Проверьте, что файл .env находится рядом с main.py и содержит строку TELEGRAM_BOT_TOKEN=ваш_токен_бота")

bot = telebot.TeleBot(TOKEN)

motivations = [
    "Сегодня твой день — начни его с улыбки! 😊",
    "Ты намного сильнее, чем думаешь. 💪",
    "Не сдавайся, даже если сложно. ✨",
    "Каждый день — новый шанс изменить свою жизнь. 🌅",
    "Верь в себя и у тебя всё получится! 🚀",
    "Ошибки — это ступеньки к успеху. 🪜",
    "Смелость — это начало победы. 🦁",
    "Действуй сейчас, не откладывай на завтра! ⏳",
    "Твои мечты важнее страхов. 🌠",
    "Ты способен на большее, чем думаешь! 🔥"
]

smart_quotes = [
    "Секрет перемен состоит в том, чтобы сосредоточиться на создании нового, а не на борьбе со старым. Сократ — древнегреческий философ. 🧠",
    "Только тот, кто предпринимает абсурдные попытки, сможет достичь невозможного. Альберт Эйнштейн. 🔬",
    "Наше величайшее слабое место заключается в отказе. Самый верный путь к успеху — всегда пробовать ещё один раз. Томас Эдисон. 💡",
    "Дорогу осилит идущий. Овидий. 🛤️",
    "Не бойся медленно идти вперёд, бойся стоять на месте. Китайская пословица. 🐢",
    "Счастье — это не что-то готовое. Оно приходит от ваших собственных действий. Далай-лама. ☀️",
    "Успех — это сумма небольших усилий, повторяемых изо дня в день. Роберт Коллиер. 📈",
    "Великие дела начинаются с малого шага. Лао-цзы. 👣",
    "Побеждает тот, кто верит в победу. Лев Толстой. 🏆",
    "Сила не в том, чтобы никогда не падать, а в том, чтобы подниматься каждый раз, когда упал. Конфуций. 🏋️"
]

# Хранилище пользовательских фраз и уникальных очередей цитат
user_data = {}

from telebot import types

def get_markup():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Цитата дня", callback_data="quote_of_the_day")
    btn2 = types.InlineKeyboardButton("Мой мотиватор", callback_data="my_motivation")
    markup.add(btn1, btn2)
    return markup

# Получить уникальную цитату для пользователя
def get_unique_quote(user_id):
    if user_id not in user_data or not user_data[user_id].get('quote_queue'):
        # Перемешиваем и сохраняем очередь
        queue = smart_quotes.copy()
        random.shuffle(queue)
        user_data.setdefault(user_id, {})['quote_queue'] = queue
    return user_data[user_id]['quote_queue'].pop()

# Получить уникальную мотивацию для пользователя
def get_unique_motivation(user_id):
    if user_id not in user_data or not user_data[user_id].get('motivation_queue'):
        queue = motivations.copy()
        # Добавляем пользовательские фразы
        queue += user_data.get(user_id, {}).get('user_motivations', [])
        random.shuffle(queue)
        user_data.setdefault(user_id, {})['motivation_queue'] = queue
    return user_data[user_id]['motivation_queue'].pop()

# Получить цитату с внешнего API
def get_external_quote():
    try:
        resp = requests.get('https://api.forismatic.com/api/1.0/', params={
            'method': 'getQuote',
            'format': 'json',
            'lang': 'ru'
        }, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            text = data.get('quoteText', '').strip()
            author = data.get('quoteAuthor', '').strip()
            if author:
                return f'"{text}"\n{author}'
            else:
                return text
        else:
            return None
    except Exception:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    with open('1754391065.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    bot.send_message(
        message.chat.id,
        "Привет! Я — твой бот-мотиватор.\n\nЯ могу прислать тебе:\n- Мотивирующую фразу: /getmotivation\n- Мотивирующую цитату: /getsmartquote\n- Добавить свою фразу: /addmotivation <текст>\n- Добавить свою цитату: /addquote <текст>\n- Получить цитату из интернета: /externalquote\n\nВведи одну из этих команд, чтобы получить заряд вдохновения!"
    )

@bot.message_handler(commands=['getmotivation'])
def send_motivation(message):
    user_id = message.from_user.id
    motivation = get_unique_motivation(user_id)
    bot.send_message(message.chat.id, motivation, reply_markup=get_markup())

@bot.message_handler(commands=['getsmartquote'])
def send_smart_quote(message):
    user_id = message.from_user.id
    quote = get_unique_quote(user_id)
    bot.send_message(message.chat.id, quote, reply_markup=get_markup())

@bot.message_handler(commands=['externalquote'])
def send_external_quote(message):
    quote = get_external_quote()
    if quote:
        bot.send_message(message.chat.id, f"Цитата из интернета:\n{quote}", reply_markup=get_markup())
    else:
        bot.send_message(message.chat.id, "Не удалось получить цитату из интернета.", reply_markup=get_markup())

@bot.message_handler(commands=['addmotivation'])
def add_motivation(message):
    user_id = message.from_user.id
    text = message.text[len('/addmotivation'):].strip()
    if not text:
        bot.send_message(message.chat.id, "Пожалуйста, укажи текст своей мотивирующей фразы после команды.")
        return
    user_data.setdefault(user_id, {}).setdefault('user_motivations', []).append(text)
    bot.send_message(message.chat.id, "Твоя мотивирующая фраза добавлена!", reply_markup=get_markup())

@bot.message_handler(commands=['addquote'])
def add_quote(message):
    user_id = message.from_user.id
    text = message.text[len('/addquote'):].strip()
    if not text:
        bot.send_message(message.chat.id, "Пожалуйста, укажи текст своей цитаты после команды.")
        return
    user_data.setdefault(user_id, {}).setdefault('user_quotes', []).append(text)
    bot.send_message(message.chat.id, "Твоя цитата добавлена!", reply_markup=get_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.from_user.id
    if call.data == "quote_of_the_day":
        # Включаем пользовательские цитаты
        all_quotes = smart_quotes + user_data.get(user_id, {}).get('user_quotes', [])
        if user_id not in user_data or not user_data[user_id].get('quote_queue'):
            queue = all_quotes.copy()
            random.shuffle(queue)
            user_data.setdefault(user_id, {})['quote_queue'] = queue
        quote = user_data[user_id]['quote_queue'].pop()
        bot.send_message(call.message.chat.id, f"Цитата дня:\n{quote}", reply_markup=get_markup())
    elif call.data == "my_motivation":
        all_motivations = motivations + user_data.get(user_id, {}).get('user_motivations', [])
        if user_id not in user_data or not user_data[user_id].get('motivation_queue'):
            queue = all_motivations.copy()
            random.shuffle(queue)
            user_data.setdefault(user_id, {})['motivation_queue'] = queue
        motivation = user_data[user_id]['motivation_queue'].pop()
        bot.send_message(call.message.chat.id, f"Твой мотиватор:\n{motivation}", reply_markup=get_markup())

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_message(
        message.chat.id,
        "Введи /getmotivation для получения мотивирующей фразы или /getsmartquote для получения мотивирующей цитаты.",
        reply_markup=get_markup()
    )

if __name__ == "__main__":
    print("Бот запущен!")
    bot.polling(none_stop=True) 