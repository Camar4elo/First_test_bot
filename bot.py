import logging
from math import e
from os import sep
from posixpath import join
import re
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
        string = ' '.join(words_list)
        if len(string.split()) > 0:
            update.message.reply_text(f'Вы написали количество слов: {len(string.split())}')
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


def replace_char(city):
    exceptions = ['ь', 'ы', 'ъ', 'ё', 'ц',]
    if city[-1] in exceptions:
        city = city.replace(city[-1], '')
    return city
 

def city_transformation(city):
    words = []
    for word in city:
        words.append(word.capitalize())
    city = ' '.join(words)
    return city


def get_bot_city(cities_dict, user_city, update, context):
    cities_count = len(cities_dict) - 1
    for bot_city in cities_dict:
        bot_city_count = cities_dict.index(bot_city)
        bot_city = bot_city.lower()
        if bot_city[0] == user_city[-1]:
            bot_city = bot_city.split()
            bot_city = city_transformation(bot_city)
            update.message.reply_text(f'Мой город: {bot_city}')
            cities_dict.remove(bot_city)
            bot_city = replace_char(bot_city)
            for city in cities_dict:
                city_count = len(cities_dict) - 1
                if city[0] == bot_city[-1].capitalize():
                    update.message.reply_text(f'Тогда Ваш город на букву "{bot_city[-1].capitalize()}"')
                    context.user_data.update({'letters' : [bot_city[-1].capitalize()]})
                    break
                elif city[0] != bot_city[-1].capitalize() and city_count == cities_count:
                    update.message.reply_text(f'Кажется, городов оканчивающихся на букву "{user_city[-1].capitalize()}" больше нет напишите город с любой буквы')
                    context.user_data.update({'letters': ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ч', 'Ш', 'Щ', 'Э', 'Ю', 'Я']})
                    break
            break
        elif bot_city[0] != user_city[-1] and bot_city_count == cities_count:
            update.message.reply_text(f'Кажется, городов оканчивающихся на букву "{user_city[-1].capitalize()}" больше нет напишите город с любой буквы')
            context.user_data.update({'letters': ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ч', 'Ш', 'Щ', 'Э', 'Ю', 'Я']})
            break

def user_play_cities(update, context):
    cities = get_cities()
    user_id = str(update.message.from_user["id"])
    user_city = update.message.text.split()[1:]
    user_city = city_transformation(user_city)
    if user_id not in context.user_data:
        context.user_data.update({user_id : cities.copy()})
        context.user_data.update({'letters' : ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ч', 'Ш', 'Щ', 'Э', 'Ю', 'Я']})
    cities_dict = context.user_data[user_id]
    letters = context.user_data['letters']
    if user_city in cities_dict:
        if user_city[0] not in letters:
            update.message.reply_text(f'Ваш город должен начинаться с буквы "{letters[0]}"')
        else:
            update.message.reply_text(f'Ваш город: {user_city}')
            cities_dict.remove(user_city)
            user_city = replace_char(user_city)
            update.message.reply_text(f'Тогда мой город на букву "{user_city[-1].capitalize()}"')
            get_bot_city(cities_dict, user_city, update, context)
    else:
        if user_city[0] not in letters:
            update.message.reply_text(f'Ваш город должен начинаться с буквы "{letters[0]}"')
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