import config
import telebot
import requests
from bs4 import BeautifulSoup
import random
import re
import sqlite3

bot = telebot.TeleBot(config.TOKEN_1)

def cocktail_time(cocktail: str) -> str:
    """This function parses the cocktail recipe from the site"""
    comps, message, message_with_ingredients, message_with_things, recipe_text = {}, '', '', '', ''
    cocktails = {
        'апероль шприц': '1098-aperol-shprits',
        'голубая лагуна': '314-golubaya-laguna',
        'маргарита': '39-margarita',
        'белый русский': '15-belyy-russkiy',
        'мохито': '57-mohito',
        'б-52': '164-b-52',
        'секс на пляже': '814-seks-na-plyazhe',
        'негрони': '55-negroni',
        'кровавая мэри': '31-krovavaya-meri',
        'космополитен': '29-kosmopoliten',
        }
    if cocktail.lower() in cocktails:
        url = 'https://ru.inshaker.com/cocktails/' + cocktails[cocktail.lower()]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.findAll('div', class_='good-count')
        items_ingredients = soup.findAll('div', class_='previews')
        items_tools = soup.findAll('td', class_='name')
        items_recipe = soup.find('ul', class_='steps')
        for item in items_ingredients:
            key = 'name'
            comps.setdefault(key, [])
            comps[key].append(item.find('ul', class_='ingredients'))
            comps[key] = re.findall(r'[а-я А-Я]+', str(comps[key]))
            while ' ' in comps[key]:
                comps[key].remove(' ')
            while 'х' in comps[key]:
                comps[key].remove('х')
        for item in items:
            key = 'amount'
            comps.setdefault(key, [])
            comps[key].append(item.find(key).text)
        for item in items:
            key = 'unit'
            comps.setdefault(key, [])
            comps[key].append(item.find(key).text)
        for item in items_tools:
            key = 'tools_name'
            comps.setdefault(key, [])
            if item.find('a', href=True) == None:
                break
            else:
                comps[key].append(item.find('a', href=True).get_text(strip=True))
                comps[key] = re.findall(r'[а-я А-Я]+', str(comps[key]))
                while ' ' in comps[key]:
                    comps[key].remove(' ')
        # Рецепт
        recipe = items_recipe.find_all('li')
        for text in recipe:
            recipe_text += text.contents[0] + '\n'
        #
        for i in range(len(comps['name'])):
            message_with_ingredients += f"{comps['name'][i]} {comps['amount'][i]} {comps['unit'][i]}\n"
        for i in range(len(comps['name']), len(comps['tools_name'])):
            message_with_things += f"{comps['tools_name'][i]} {comps['amount'][i]} {comps['unit'][i]}\n"
        message = f"*Необходимые ингредиенты*\n{message_with_ingredients}\n*Необходимые штучки*\n{message_with_things}\n*Рецепт*\n{recipe_text}"
    else:
        message = 'Такого коктейля нет в нашем списке'
    return f'Коктейль *{cocktail.title()}* 🍸\n\n{message}'


def exchange_rates():
    response = requests.get('https://yandex.ru/')
    soup = BeautifulSoup(response.text, 'html.parser')
    s = soup.findAll('span', class_='inline-stocks__value_inner')
    nums = re.findall(r'\d+', str(s))
    nums = [int(i) for i in nums]
    dollar = str(nums[0])+','+str(nums[1])
    euro = str(nums[2])+','+str(nums[3])
    return (f'1 💵 = {dollar} ₽\n1 💶 = {euro} ₽')


def horoscope(message):
    zodiac_sign = dict(aries = 'овен', taurus = 'телец', gemini = 'близнецы', cancer = 'рак', leo = 'лев', virgo = 'дева', libra = 'весы', scorpio = 'скорпион', sagittarius = 'стрелец', capricorn = 'козерог', aquarius = 'водолей', pisces = 'рыбы')
    for zodiac_en, zodiac_ru in zodiac_sign.items():
        if zodiac_ru == message.text.lower():
            needed_zodiac_sign = zodiac_en
    if message.text.lower() in list(zodiac_sign.values()):
        url = 'https://1001goroskop.ru/?znak=' + needed_zodiac_sign
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        quotes = soup.find('p').text
    else:
        quotes = 'Такого знака ещё нет...'
    bot.send_message(message.chat.id, quotes)
    return (quotes)


'''
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)
'''


@bot.message_handler(commands=['start'])
def send_welcome(message):
    
    with sqlite3.connect('users.db') as connect:
        cursor = connect.cursor()
        #print("Подключен к SQLite")
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER UNIQUE,
            first_name TEXT,
            username TEXT,
            last_name TEXT
            )""")
        cursor.execute("INSERT OR IGNORE INTO users VALUES(?, ?, ?, ?);", [message.from_user.id, message.from_user.first_name, message.from_user.username, message.from_user.last_name])
    '''
    with open("bots_users.txt", "a") as file:
        info = {
            'user_id': message.from_user.id, 
            'user_first_name': message.from_user.first_name, 
            'user_last_name': message.from_user.last_name
        }
        info_id = str(info.get('user_id'))
        info_first_name = str(info.get('user_first_name'))
        info_last_name = str(info.get('user_last_name'))
        file.write(f'ID : {info_id} / Имя : {info_first_name} / Фамилия : {info_last_name}\n')
    '''
    markup_inline = telebot.types.InlineKeyboardMarkup()
    item_weather = telebot.types.InlineKeyboardButton(text = '🌡️Погода', callback_data = 'weather')
    item_news = telebot.types.InlineKeyboardButton(text = '📰Новости', callback_data = 'news')
    item_exchange = telebot.types.InlineKeyboardButton(text = '💱Курс', callback_data = 'exchange')
    item_horoscope = telebot.types.InlineKeyboardButton(text = '💫Гороскоп', callback_data = 'horoscope')
    item_cocktail = telebot.types.InlineKeyboardButton(text = '🍸Выпить', callback_data = 'cocktail')
    item_coin_flipping = telebot.types.InlineKeyboardButton(text = '🍀Монета', callback_data = 'coin_flipping')
    markup_inline.add(item_weather, item_news, item_exchange, item_horoscope, item_cocktail, item_coin_flipping)
    bot.send_message(message.from_user.id, 'Привет, чем могу помочь?', reply_markup = markup_inline)


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.from_user.id, 'Напиши Привет или /start')


@bot.message_handler(commands = ['get_info', 'info'])
def get_user_info(message):
    markup_inline = telebot.types.InlineKeyboardMarkup()  # создает клавиатуру под сообщением
    item_yes = telebot.types.InlineKeyboardButton(text = 'Да', callback_data = 'yes')  # создаем кнопки
    item_no = telebot.types.InlineKeyboardButton(text = 'Нет', callback_data = 'no')

    markup_inline.add(item_yes, item_no)  # добавляем кнопки НА клаву
    bot.send_message(message.from_user.id, 'Инфо?', reply_markup = markup_inline)  # сообщение к которому будут крепиться кнопки


#@bot.callback_query_handler(func=lambda call: call.data in ['yes', 'no'])
@bot.callback_query_handler(func=lambda call: True)  # лямбда- всегда ожидает ответа, и в случаи нажатия - выполняется. 
def answer(call):
    if call.data == 'yes':
        markup_reply = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard=True)  # resize_keyboard делает клаву меньше
        item_id = telebot.types.KeyboardButton('Мой ID')
        item_username = telebot.types.KeyboardButton('Моё имя')
        markup_reply.add(item_id, item_username)
        bot.send_message(call.message.chat.id, 'Жми на одну из кнопок', reply_markup=markup_reply)
    elif call.data == 'no':
        pass
    elif call.data == 'weather':
        bot.send_message(call.message.chat.id, what_is_the_weather())
    elif call.data == 'news':
        bot.send_message(call.message.chat.id, what_is_the_news())
    elif call.data == 'exchange':
        bot.send_message(call.message.chat.id, exchange_rates())
    elif call.data == 'horoscope':
        message_horoscope = bot.send_message(call.message.chat.id, 'Какой знак зодиака?')
        bot.register_next_step_handler(message_horoscope, horoscope)
    elif call.data == 'cocktail':
        markup_inline = telebot.types.InlineKeyboardMarkup(row_width=2)
        coc_mo = telebot.types.InlineKeyboardButton(text = 'Мохито', callback_data = 'mo')
        coc_gl = telebot.types.InlineKeyboardButton(text = 'Голубая лагуна', callback_data = 'gl')
        coc_ma = telebot.types.InlineKeyboardButton(text = 'Маргарита', callback_data = 'ma')
        coc_bl = telebot.types.InlineKeyboardButton(text = 'Белый русский', callback_data = 'bl')
        coc_52 = telebot.types.InlineKeyboardButton(text = 'Б-52', callback_data = '52')
        markup_inline.add(coc_mo, coc_gl, coc_ma, coc_bl, coc_52)
        bot.send_message(call.message.chat.id, 'Какой хочешь коктейль?', reply_markup = markup_inline)
    elif call.data == 'mo':
        bot.send_message(call.message.chat.id, cocktail_time(cocktail='мохито'), reply_markup=None, parse_mode= 'Markdown')
    elif call.data == 'gl':
        bot.send_message(call.message.chat.id, cocktail_time(cocktail='голубая лагуна'), reply_markup=None, parse_mode= 'Markdown')
    elif call.data == 'ma':
        bot.send_message(call.message.chat.id, cocktail_time(cocktail='маргарита'), reply_markup=None, parse_mode= 'Markdown')
    elif call.data == 'bl':
        bot.send_message(call.message.chat.id, cocktail_time(cocktail='белый русский'), reply_markup=None, parse_mode= 'Markdown')
    elif call.data == '52':
        bot.send_message(call.message.chat.id, cocktail_time(cocktail='б-52'), reply_markup=None, parse_mode= 'Markdown')
    elif call.data == 'coin_flipping':
        bot.send_message(call.message.chat.id, coin_flipping())


@bot.message_handler(content_types = ['text'])
def get_text_messages(message):
    if message.text.lower() == 'привет':
        #bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}! Сейчас я расскажу тебе...')
        markup_inline = telebot.types.InlineKeyboardMarkup()
        item_weather = telebot.types.InlineKeyboardButton(text = '🌡️Погода', callback_data = 'weather')
        item_news = telebot.types.InlineKeyboardButton(text = '📰Новости', callback_data = 'news')
        item_exchange = telebot.types.InlineKeyboardButton(text = '💱Курс', callback_data = 'exchange')
        item_horoscope = telebot.types.InlineKeyboardButton(text = '💫Гороскоп', callback_data = 'horoscope')
        item_cocktail = telebot.types.InlineKeyboardButton(text = '🍸Выпить', callback_data = 'cocktail')
        item_coin_flipping = telebot.types.InlineKeyboardButton(text = '🍀Монета', callback_data = 'coin_flipping')
        markup_inline.add(item_weather, item_news, item_exchange, item_horoscope, item_cocktail, item_coin_flipping)
        bot.send_message(message.from_user.id, f'Привет, *{message.from_user.first_name}*! Чем могу помочь?', reply_markup = markup_inline, parse_mode= 'Markdown')
    elif message.text.lower() == 'как дела':
        bot.send_message(message.from_user.id, 'Всё хорошо!')
    elif message.text.lower() == 'спасибо':
        bot.send_sticker(message.from_user.id, 'CAACAgIAAxkBAAEBz_RgDpoYahQJGJj-jbTJhjE8VFe9KgACOwADO2AkFFKC45_2IelfHgQ')
    elif message.text.lower() == 'погода':
        bot.send_message(message.from_user.id, what_is_the_weather())
    elif message.text.lower() == 'новости':
        bot.send_message(message.from_user.id, what_is_the_news())
    elif message.text.lower() == 'курс':
        bot.send_message(message.from_user.id, exchange_rates())
    elif message.text.lower() == 'гороскоп':
        message_horoscope = bot.send_message(message.from_user.id, 'Какой знак зодиака?')
        bot.register_next_step_handler(message_horoscope, horoscope)
    elif message.text == 'Мой ID':
        bot.send_message(message.from_user.id, f'Твой ID {message.from_user.id}', reply_markup=None)
    elif message.text == 'Мой ник':
        bot.send_message(message.from_user.id, f'Твоё имя {message.from_user.first_name} {message.from_user.last_name}', reply_markup=None)

    elif message.text.lower() == 'мохито':
        bot.send_message(message.from_user.id, cocktail_time(cocktail=message.text), reply_markup=None, parse_mode= 'Markdown')
    elif message.text.lower() == 'голубая лагуна':
        bot.send_message(message.from_user.id, cocktail_time(cocktail=message.text), reply_markup=None, parse_mode= 'Markdown')
    elif message.text.lower() == 'маргарита':
        bot.send_message(message.from_user.id, cocktail_time(cocktail=message.text), reply_markup=None, parse_mode= 'Markdown')
    elif message.text.lower() == 'белый русский':
        bot.send_message(message.from_user.id, cocktail_time(cocktail=message.text), reply_markup=None, parse_mode= 'Markdown')
    elif message.text.lower() == 'б-52':
        bot.send_message(message.from_user.id, cocktail_time(cocktail=message.text), reply_markup=None, parse_mode= 'Markdown')

    else:
        bot.send_message(message.from_user.id, 'Я тебя не понимаю. Напиши /help.')


def what_is_the_weather():
    url = 'https://wttr.in'
    weather_request = requests.get(url + '/Moscow?format=')
    weather_text = requests.get(url + '/Moscow?format=%C', headers={'Accept-Language': 'ru'})
    weather_temperature = requests.get(url + '/Moscow?format=%t+%c')
    weather_sunrise = requests.get(url + '/Moscow?format=%S')
    weather_sunset = requests.get(url + '/Moscow?format=%s')
    weather_message = f'В Москве сейчас {weather_text.text.lower()}, {weather_temperature.text}\nВосход {weather_sunrise.text}🌅\nЗакат {weather_sunset.text}🌇'
    return weather_message


def what_is_the_news():
    news_message = ''
    url = 'https://www.currenttime.tv/news'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('h4', class_='media-block__title media-block__title--size-4')
    for quote in quotes[ : 5]:
        news_message += f'{quote.text}'
    return news_message


def coin_flipping():
    coin_flipping = random.choice(["Орёл","Решка"])
    return coin_flipping



bot.polling(none_stop=True, interval=0)











'''
import pyowm
from telebot import types

owm = pyowm.OWM(config.owmtoken, language="ru")
bot = telebot.TeleBot(config.token)

STIKER_ID = 'CAACAgIAAxkBAAJgsl60JM-sJ3RCWfPmzW1ueswOeM38AAIbAAOvxlEa6GSI_sKnQ-cZBA'
LOVE_ID = 'CAACAgIAAxkBAAJhdV61RuX6imeSKxw3lWkQUvf3bg0YAAKIAQACGELuCBbAgQyGdcsIGQQ'

# Функция проверки авторизации
def autor(chatid):
    strid = str(chatid)
    for item in config.users:
        if item == strid:
            return True
    return False
##############################

@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_mess = f"Бонжур, <b>{message.from_user.first_name}</b>!\n"
    bot.send_message(message.chat.id, send_mess, parse_mode='html')  # , reply_markup=markup_menu)

@bot.message_handler(content_types=["sticker"])
def send_sticker(message):
    bot.send_sticker(message.chat.id, STIKER_ID)

@bot.message_handler(content_types=["text"])
@bot.edited_message_handler(content_types=["text"])
def repeat_all_messages(message):
    if message.text.lower() == 'love':
        bot.send_sticker(message.chat.id, LOVE_ID)
    else:
        bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    bot.polling(none_stop=True)
'''