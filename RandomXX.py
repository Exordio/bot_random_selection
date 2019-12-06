#Бот созданный для случайного выбора пользователя из списка зарегистрированных.
#Достаточно добавить его в беседу, так же необходимо указать в скрипте, кто имеет право ролить.
#Файл Ball.dat содержит список участников

#Работает через вебхуки, для запуска необходима машина с белым IP, либо дедик.
#author: Golubev Ivan 

import linecache
import tokenz
import random
import math
import telebot
import requests
import json
import cherrypy

webhook_host = '' # Указать публичный IP
webhook_port = 443
webhook_listen = '0.0.0.0'
webhook_SSL_cert = '/home/ubuntu/Boot_webhook_pooling/webher_cert.pem' # Самоподписаный серт
webhook_SSL_PRIV = '/home/ubuntu/Boot_webhook_pooling/webher_pkey.pem' # Ключ серта
webhook_url_kekbase = "https://%s:%s" % (webhook_host, webhook_port)
webhook_url_path = "/%s/" % (tokenz.token_for_bot)

bot = telebot.TeleBot(tokenz.token_for_bot)

class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения 
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

#Функция логов

def log_from_bot(message, ans):
    print("\n =========================================")
    from datetime import datetime
    print(datetime.now())
    now = datetime.now()
    print("Получено сообщение от {0} {1}. id = {2} \n Содержание : {3}".format(message.from_user.first_name,
                                                                             message.from_user.last_name,
                                                                             str(message.from_user.id),
                                                                             message.text))
    print('Бот : ', ans)
    LOGFILE = open("/LOG_FILES/{0}.{1}.{2}:{3}:{4}.LOGZ".format(message.from_user.first_name,message.from_user.last_name,now.year, now.month, now.day),"a")
    LOGFILE.write("==================================================================================\n"
                  "Получено сообщение от {0} {1}. id = {2} \nСодержание : {3} \nБот ответил:{5}\nВремя сообщения : {4}\n".format(message.from_user.first_name,
                                                                                                                message.from_user.last_name,
                                                                                                                str(message.from_user.id),
                                                                                                                message.text,
                                                                                                                datetime.today(),ans))
    LOGFILE.close()

random.seed()
#Дефолтные команды для бота


@bot.message_handler(func=lambda message: True, commands=['start'])
def Start_Command(message):
    ans = "Бот специально созданный для розыгрышей\nС наступающим. 🍷\n✨✨ © Grow Community ✨✨"
    #bot.send_message(message.from_user.id, ans)
    userKeyboard = telebot.types.ReplyKeyboardMarkup(True, False, True)
    userKeyboard.row('Поучаствовать :)')
    userKeyboard.row('Количество участников')
    bot.send_message(message.chat.id, ans ,reply_markup=userKeyboard)
    log_from_bot(message,ans)
@bot.message_handler(func=lambda message: True, commands=['stop'])
def Stop_Command(message):
    ans = 'Всего доброго 🍺🍻, С наступающим :)'
    hide_userKeyboad = telebot.types.ReplyKeyboardRemove(True)
    bot.send_message(message.chat.id, ans ,reply_markup=hide_userKeyboad)
    log_from_bot(message,ans)

@bot.message_handler(func=lambda message: True, commands=['LetsRoll'])
def Roll(message):
    CountStr = open('Ball.dat','r')
    i = 0
    for line in CountStr:
        i+=1;
    CountStr.close()
    #FindStr = open("Ball.dat")
    #StrFind = FindStr.read()
    #Winner = StrFind.split('\n',)
    bot.send_message(message.chat.id,"Победитель в розыгрыше : {0}, Поздравляем!\nВскоре с вами свяжется администрация для вручения приза".format(linecache.getline('Ball.dat',random.randint(1,i))))





#Реакция на сообщения
@bot.message_handler(func=lambda message: True,content_types=['text'])
def ReactOnText(message):
    if (message.text == "Поучаствовать :)"):
        The_Participants = open('Ball.dat','r')
        Id_users = The_Participants.read()
        The_Participants.close()
        Participant = Id_users.count(str(message.from_user.id))
        if (Participant == 0):
            The_Participants = open('Ball.dat','a')
            The_Participants.write("Nickname : {0} {1}, id = {2}\n".format(message.from_user.first_name,message.from_user.last_name,str(message.from_user.id)))
            The_Participants.close()
            ans = "Вы успешно зарегестрировались на участие в конкурсе :)"
            bot.send_message(message.chat.id,ans)
            log_from_bot(message,ans)
        else:
            ans = "Вы уже учавствуете в конкурсе :) "
            bot.send_message(message.chat.id,ans)
            log_from_bot(message,ans)
    if (message.text == 'Количество участников'):
        CountStr = open('Ball.dat', 'r')
        i = 0
        for line in CountStr:
            i += 1;
        CountStr.close()
        bot.send_message(message.chat.id, "На данный момент участников : {0} 🎱".format(i))



bot.remove_webhook()

bot.set_webhook(url=webhook_url_kekbase + webhook_url_path, certificate=open(webhook_SSL_cert, 'r'))
cherrypy.config.update({
    'server.socket_host': webhook_listen,
    'server.socket_port': webhook_port,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': webhook_SSL_cert,
    'server.ssl_private_key': webhook_SSL_PRIV
})

cherrypy.quickstart(WebhookServer(), webhook_url_path, {'/':{}})
