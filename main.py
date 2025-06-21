import telebot
from telebot import types
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

users = {}  # Активные чаты: {user1_id: user2_id, user2_id: user1_id}
freeid = None  # ID пользователя в очереди
users_data = {}  # Локации: {user_id: {"country": "страна", "city": "город"}}

# --- Команда START ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет. Это анонимный чат.\n"
        "Используй /find для поиска собеседника.\n"
        "Можно указать локацию (/set_location) и искать рядом (/find_nearby).\n"
        "/stop — остановить диалог."
    )

# --- Установка локации ---
@bot.message_handler(commands=['set_location'])
def set_location(message):
    msg = bot.send_message(
        message.chat.id,
        "Отправь страну и город (например: Россия, Москва):"
    )
    bot.register_next_step_handler(msg, save_location)

def save_location(message):
    if message.text:
        if "," in message.text:
            country, city = message.text.split(",", 1)
            users_data[message.chat.id] = {
                "country": country.strip(),
                "city": city.strip()
            }
            bot.send_message(message.chat.id, f"Локация сохранена: {country}, {city}")
        else:
            users_data[message.chat.id] = {
                "country": message.text.strip(),
                "city": "Не указан"
            }
            bot.send_message(message.chat.id, f"Страна сохранена: {message.text}")

# --- Обычный поиск ---
@bot.message_handler(commands=['find'])
def find(message):
    global freeid
    if message.chat.id not in users:
        bot.send_message(message.chat.id, "Поиск...")
        if freeid is None:
            freeid = message.chat.id
        else:
            bot.send_message(message.chat.id, "Собеседник найден.")
            bot.send_message(freeid, "Собеседник найден.")
            users[freeid] = message.chat.id
            users[message.chat.id] = freeid
            freeid = None
    else:
        bot.send_message(message.chat.id, "Вы уже в чате. /stop — выйти.")

# --- Поиск по локации ---
@bot.message_handler(commands=['find_nearby'])
def find_nearby(message):
    global freeid
    if message.chat.id not in users:
        if message.chat.id not in users_data:
            bot.send_message(message.chat.id, "Сначала укажите локацию (/set_location).")
            return

        user_data = users_data[message.chat.id]
        bot.send_message(message.chat.id, f"Ищем в {user_data['country']}, {user_data['city']}...")

        # Если есть ожидающий с такой же локацией
        if freeid and freeid in users_data:
            freeid_data = users_data[freeid]
            if (freeid_data["country"] == user_data["country"] and 
                freeid_data["city"] == user_data["city"]):
                bot.send_message(message.chat.id, "Найден собеседник из вашего города.")
                bot.send_message(freeid, "Найден собеседник из вашего города.")
                users[freeid] = message.chat.id
                users[message.chat.id] = freeid
                freeid = None
                return

        # Если нет — добавляем в очередь
        if freeid is None:
            freeid = message.chat.id
        else:
            bot.send_message(message.chat.id, "Пока никого рядом нет. Используйте /find для обычного поиска.")
    else:
        bot.send_message(message.chat.id, "Вы уже в чате. /stop — выйти.")

# --- Остановка чата ---
@bot.message_handler(commands=['stop'])
def stop(message):
    global freeid
    if message.chat.id in users:
        partner_id = users[message.chat.id]
        bot.send_message(message.chat.id, "Чат остановлен.")
        bot.send_message(partner_id, "Собеседник вышел из чата.")
        del users[partner_id]
        del users[message.chat.id]
    elif message.chat.id == freeid:
        freeid = None
        bot.send_message(message.chat.id, "Поиск отменен.")
    else:
        bot.send_message(message.chat.id, "Вы не в чате.")

# --- Пересылка сообщений ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'voice'])
def chat(message):
    if message.chat.id in users:
        bot.send_message(users[message.chat.id], message.text)
    else:
        bot.send_message(message.chat.id, "Нет активного чата. /find — начать поиск.")

bot.polling()
