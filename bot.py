from telegram import ReplyKeyboardMarkup, Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
import requests
from db import BotDB
BotDB = BotDB('cleverBot.db')

keyboardMenu = ReplyKeyboardMarkup([['Новый поиск'], ['История']], resize_keyboard = True, one_time_keyboard = True)

state = 0
address_str = ''
history = ''

def start(update, context):
    global state
    state = 0
    if not BotDB.user_exists(update.effective_chat.id):
        BotDB.add_user(update.effective_chat.id)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Я бог адресов, нажмите 'Новый запрос', чтобы узнать полный адрес, или 'Историю', чтобы посмотреть вашу историю запросов.", reply_markup = keyboardMenu)

def text (update, context):
    # выбор кнопки в /start
    global state
    global history
    answer = update.message.text
    if answer == 'Новый поиск':
        state += 1
        update.message.reply_text('Введите адрес.')
    elif answer == 'История':
        history = BotDB.get_records(update.effective_chat.id)
        if(len(history)):
            update.message.reply_text(f'Количество поисковых запросов: {len(history)}.')
            for i in range(5):
                update.message.reply_text(f'{history[i][2]} -> {history[i][1]} ({history[i][4]})')
        else:
            update.message.reply_text("Поисковых запросов не обнаружено.")
        state = 0
    elif state > 0:
        address_str = get_address(answer)
        BotDB.add_record(update.effective_chat.id, answer, address_str)
        update.message.reply_text(address_str)
    else:
        update.message.reply_text('Я кнопочный бот, пожалуйста, используйте кнопки.')

def get_address(address):
    PARAMS = {
        "apikey":"66dfb8f3-66e3-451d-ab7e-fcbbf35b98e1",
        "format":"json",
        "lang":"ru_RU",
        "kind":"house",
        "results" : 1,
        "geocode": address
    }
    #запрос по адресу геокодера.
    try:
        r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=PARAMS)
        #получаем данные
        json_data = r.json()
        #вытаскиваем из всего пришедшего json именно строку с полным адресом.
        global address_str
        address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]
        #возвращаем полученный адрес
        return address_str
    except Exception as e:
        #если не смогли, то возвращаем ошибку
        return "Не найдено"

def main():
    #создаем бота и указываем его токен
    token = "2098729940:AAHT49ysh_bOYHeyD96XmJxRh1FQA8TWwtw"
    updater = Updater(token, use_context=True) 
    #создаем регистратор событий, который будет понимать, что сделал пользователь и на какую функцию надо переключиться.
    dispatcher = updater.dispatcher

    #регистрируем команду /start и говорим, что после нее надо использовать функцию def start
    dispatcher.add_handler(CommandHandler("start", start))
    #регистрируем получение текста и говорим, что после нее надо использовать функцию def text
    dispatcher.add_handler(MessageHandler(Filters.text, text))
    #запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    #запускаем функцию def main
    main()    