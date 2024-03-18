from django.http import HttpResponse
import telebot
from django.views.decorators.csrf import csrf_exempt
import logging

with open('bot_token.txt', 'r') as f:
    TOKEN = f.read()

bot = telebot.TeleBot(TOKEN)

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.body.decode("utf-8"))
        try:
            bot.process_new_updates([update])
        except Exception as e:
            logging.error(e)
        return HttpResponse(status=200)