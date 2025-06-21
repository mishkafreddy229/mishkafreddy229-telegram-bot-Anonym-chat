import telebot
from telebot import types
from config import TOKEN

# Инициализация бота с использованием его токена
bot = telebot.TeleBot(TOKEN)

users = {}

freeid = None

@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.send_message(message.chat.id, 'Просто используй комманду /find , а что бы остановить напиши /stop')

@bot.message_handler(commands=['find'])
def find(message: types.Message):
    
    global freeid
    if message.chat.id not in users:
        bot.send_message(message.chat.id, 'Ищем...')

        if freeid is None:
            freeid = message.chat.id
        else:
            # Question:
            # Is there any way to simplify this like `bot.send_message([message.chat.id, freeid], 'Founded!')`?
            bot.send_message(message.chat.id, 'Найден!')
            bot.send_message(freeid, 'Найден!')

            users[freeid] = message.chat.id
            users[message.chat.id] = freeid
            freeid = None

        print(users, freeid) # Debug purpose, you can remove that line
    else:
        bot.send_message(message.chat.id, 'Заткнись!')


@bot.message_handler(commands=['stop'])
def stop(message: types.Message):
    global freeid

    if message.chat.id in users:
        bot.send_message(message.chat.id, 'Отключаем...')
        bot.send_message(users[message.chat.id], 'Твой опонент остановил чат`...')

        del users[users[message.chat.id]]
        del users[message.chat.id]
        
        print(users, freeid) # Debug purpose, you can remove that line
    elif message.chat.id == freeid:
        bot.send_message(message.chat.id, 'Отключаем...')
        freeid = None

        print(users, freeid) # Debug purpose, you can remove that line
    else:
        bot.send_message(message.chat.id, 'Ты не находишся в режиме поиска!')

@bot.message_handler(content_types=['animation', 'audio', 'contact', 'dice', 'document', 'location', 'photo', 'poll', 'sticker', 'text', 'venue', 'video', 'video_note', 'voice'])
def chatting(message: types.Message):
    if message.chat.id in users:
        bot.copy_message(users[message.chat.id], users[users[message.chat.id]], message.id)
    else:
        bot.send_message(message.chat.id, 'No one can hear you...')

# Запуск бота
bot.polling()