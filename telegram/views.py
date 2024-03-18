from django.shortcuts import render
from django.http import HttpResponse
from telebot import types
from django.core.mail import send_mail
from django.conf import settings
import telebot
import requests
from .webhook import bot

# Create your views here.

NEWS_API = 'cf5b98ffe2474d7ebb6565092f04c5c1'

def base(request):
    return HttpResponse("Welcome!")


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_1 = types.InlineKeyboardButton('help', callback_data='help')
    btn_2 = types.InlineKeyboardButton('Search News', callback_data='News')
    markup.add(btn_1, btn_2)

    if message.from_user.last_name != None:
        bot.send_message(message.chat.id, f"Welcome, {message.from_user.first_name} {message.from_user.last_name} 😀 \nUshbu telegram bot orqali siz so'ngi yangiliklarni olishingiz va ulashishingiz mumkin", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"Welcome, {message.from_user.first_name} 😀 \nUshbu telegram bot orqali siz so'ngi yangiliklarni olishingiz va ulashishingiz mumkin", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "News")
def callback_query(call):
    news_message = get_news()
    if news_message:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_share = types.InlineKeyboardButton('Ulashish', callback_data='share')
        markup.add(btn_share)
        
        bot.send_message(call.message.chat.id, news_message, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Yangilik topilmadi")


def get_news():
    url = "https://newsapi.org/v2/top-headlines"
    parameters = {
        "apiKey": NEWS_API,
        "country": "us",
        "pageSize": 1,
    }

    response = requests.get(url, params=parameters)
    data = response.json()

    if response.status_code == 200:
        articles = data.get("articles")
        if articles:
            title = articles[0]["title"]
            description = articles[0]["description"]
            image_url = articles[0]["urlToImage"]
            
            message = f"<b>{title}</b>\n\n{description}\n\nImage: {image_url}"
            
            return message
        else:
            return None
    else:
        print("Error:", data.get("message"))
        return None
users_waiting_for_email = {}

@bot.callback_query_handler(func=lambda call: call.data == "share")
def share_callback(call):
    bot.send_message(call.message.chat.id, "Iltimos, yangiliklarni qaysi email manziliga ulashmoqchisiz?")
    users_waiting_for_email[call.message.chat.id] = "share"

@bot.message_handler(func=lambda message: message.chat.id in users_waiting_for_email and users_waiting_for_email[message.chat.id] == "share")
def handle_share_email(message):
    chat_id = message.chat.id
    email = message.text.strip()

    if "@" not in email:
        bot.send_message(chat_id, "Noto'g'ri email formati. Iltimos, to'g'ri email manzilini kiriting.")
        return

    users_waiting_for_email[chat_id] = email
    bot.send_message(chat_id, "Rahmat! Yangiliklar tez orada bu emailga ulanadi.")

    news_data = get_news()
    if news_data:
        send_news_to_email(email, news_data)
    else:
        bot.send_message(chat_id, "Yangilik topilmadi")

def send_news_to_email(email, news_data):
    bot.send_message(users_waiting_for_email[email], news_data)

# def send_email():
#     subject = ''
#     message = ''
#     from_email = ''
#     recipient_list = []
#     send_mail(subject, message, from_email, recipient_list)