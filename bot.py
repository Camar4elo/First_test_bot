import logging
from math import e
from os import sep
from posixpath import join
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
    user_id = str(update.message.from_user["id"])


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
        if symbol in text:
            text = text.split(sep=symbol)
            updated_text = '/'.join(text)
    try:
        user_date = datetime.strptime(updated_text, '%Y/%m/%d')
        moon = ephem.next_full_moon(user_date)
        update.message.reply_text(f'Ближайшее полнолуние будет: {moon}')
    except (ValueError, TypeError):
        update.message.reply_text(f'{text} не является датой, введите дату в формате: гггг/мм/дд, гггг.мм.дд, гггг:мм:дд, гггг-мм-дд или гггг_мм_дд')

def get_cities():
    with open('cities.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        cities = content.split(sep='\n')
        return cities


def user_play_cities(update, context):
    cities = get_cities()
    exceptions = ['ь', 'ы', 'ъ', 'ё', 'ц']
    user_id = str(update.message.from_user["id"])
    user_city = update.message.text.split()[1:]
    updated_user_city = []
    for word in user_city:
        updated_user_city.append(word.capitalize())
    user_city = ' '.join(updated_user_city)
    if user_id not in context.user_data:
        context.user_data.update({user_id : cities.copy()})
    city_db = context.user_data[user_id]
    if user_city in city_db:
        update.message.reply_text(f'Ваш город: {user_city}')
        city_db.remove(user_city)
        if user_city[-1] in exceptions:
            user_city = user_city.replace(user_city[-1], '')
        update.message.reply_text(f'Тогда мой город на букву "{user_city[-1].capitalize()}"')
        len_city_db = len(city_db) - 1
        for bot_city in city_db:
            index_bot_city = city_db.index(bot_city)
            bot_city = bot_city.lower()
            if bot_city[0] == user_city[-1]:
                bot_city = bot_city.split()
                updated_bot_city = []
                for word in bot_city:
                    updated_bot_city.append(word.capitalize())
                bot_city = ' '.join(updated_bot_city)
                update.message.reply_text(f'Мой город: {bot_city}')
                city_db.remove(bot_city)
                if bot_city[-1] in exceptions:
                    bot_city = bot_city.replace(bot_city[-1], '')
                update.message.reply_text(f'Тогда Ваш город на букву "{bot_city[-1].capitalize()}"')
                break
            elif bot_city[0] != user_city[-1] and index_bot_city == len_city_db:
                update.message.reply_text(f'Кажется городов оканчивающихся на букву "{user_city[-1].capitalize()}" больше нет')
    else:
        update.message.reply_text(f'Города {user_city} нет или этот город уже был')


def main():
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet', user_ask_planet))
    dp.add_handler(CommandHandler('wordcount', user_ask_wordcount))
    dp.add_handler(CommandHandler('full_moon', user_ask_full_moon))
    dp.add_handler(CommandHandler('cities', user_play_cities))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    mybot.start_polling()
    logging.info('Бот стартовал')
    mybot.idle()

if __name__ == '__main__':
    main()