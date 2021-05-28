import logging
from math import e
from os import sep
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import settings
import ephem
from datetime import timedelta, date, datetime

logging.basicConfig(filename='bot.log', level=logging.INFO)

PROXY = {'proxy_url': settings.PROXY_URL,
    'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}
    }


def greet_user(update, context):
    update.message.reply_text('Приветствую тебя, о Великий пользователь!')


def user_ask_planet(update, context):
    planets = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Moon', 'Sun']
    text = update.message.text.split()
    user_planet = text[1].capitalize()
    if user_planet in planets:
        planet = getattr(ephem, user_planet)(date.today().strftime("%Y/%m/%d"))
        constellation = ephem.constellation(planet)
        update.message.reply_text(f'Сегодня эта планета находится в созведии: {constellation[1]}')
    else:
        update.message.reply_text(f'Такой планеты нет (((. Попробуйте поискать в параллельной вселенной.')


def talk_to_me(update, context):
    text = update.message.text
    update.message.reply_text(text)


def user_ask_wordcount(update, context):
    exceptions_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '!', '@', '#', '$', '%', '^', '&',
                 '*', '(', ')', '_', '+', '№',';', '%', ':', '?', '-', '=', '[', ']', '{', '}', '|', '/', 
                 '<','>', '~', '``', ',', '.', ''
                ]
    text = update.message.text.split()[1:]
    count_words = len(text)
    if count_words == 0:
        update.message.reply_text(f'Кажется, что Вы ничего не написали...(((')
    else:
        words_list = []
        for word in text:
            if word not in exceptions_list:
                for char in word:
                    if char in exceptions_list:
                        word = word.replace(f'{char}', '')
                words_list.append(word)
                if word in exceptions_list:
                    words_list.remove(word)
        if len(words_list) > 0:
            update.message.reply_text(f'Вы написали количество слов: {len(words_list)}')
        else:
            update.message.reply_text(f'Кажется, что Вы не написали слов...')


def user_ask_full_moon(update, context):
    exceptions = ['.', '-', '_', ':']
    text = update.message.text.split()[1]
    for symbol in exceptions:
        print(symbol)
        if symbol in text:
            text = text.split(sep=symbol)
            updated_text = '/'.join(text)
    try:
        user_date = datetime.strptime(updated_text, '%Y/%m/%d')
        moon = ephem.next_full_moon(user_date)
        update.message.reply_text(f'Ближайшее полнолуние будет: {moon}')
    except (ValueError, TypeError):
        update.message.reply_text(f'{text} не является датой, введите дату в формате: гггг/мм/дд, гггг.мм.дд, гггг:мм:дд, гггг-мм-дд или гггг_мм_дд')

        


def main():
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet', user_ask_planet))
    dp.add_handler(CommandHandler('wordcount', user_ask_wordcount))
    dp.add_handler(CommandHandler('full_moon', user_ask_full_moon))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    mybot.start_polling()
    logging.info('Бот стартовал')
    mybot.idle()

if __name__ == '__main__':
    main()