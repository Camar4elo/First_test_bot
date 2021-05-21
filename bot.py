from doctest import master
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import settings
import ephem
import datetime

logging.basicConfig(filename='bot.log', level=logging.INFO)

PROXY = {'proxy_url': settings.PROXY_URL,
    'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}
    }

def greet_user(update, context):
    update.message.reply_text('Приветствую тебя, о Великий пользователь!')

def user_ask_planet(update, context):
    planets = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Moon', 'Sun']
    text = update.message.text.split()
    for user_planet in text:
        try:
            planets.index(user_planet)
            print(user_planet)
            planet = getattr(ephem, user_planet)(datetime.datetime.today().strftime("%Y/%m/%d"))
            print(planet)
            constellation = ephem.constellation(planet)
            update.message.reply_text(f'Сегодня эта планета находится в созведии: {constellation}')
        except ValueError:
            None

def talk_to_me(update, context):
    text = update.message.text
    print(text)
    update.message.reply_text(text)

def main():
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('planet', user_ask_planet))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    mybot.start_polling()
    logging.info('Бот стартовал')
    mybot.idle()

if __name__ == '__main__':
    main()