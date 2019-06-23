# coding: utf-8

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
import logging
import yaml
import datetime
import mysql.connector

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

token = open('token.conf', 'r').read().replace("\n", "")
chatid_redazione = open('chatid.conf', 'r').read().replace("\n", "")

APPROVA, NONAPPROVA, BANNA = range(3)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Ciao! Sono il bot di www.domandeimpossibili.it\nUsa il comando /domanda per inviare una domanda alla redazione.")
    #print(update.message.chat_id)

def domanda(bot, update):
    global di_db
    cursor = di_db.cursor()
    sql = "SELECT * FROM utenti WHERE chat_id = " + str(update.message.from_user.id) + ";"
    cursor.execute(sql)
    res = cursor.fetchone()
    if(res is None):
        sql = ( 
            'INSERT INTO utenti('
            'chat_id, ' + ("username, " if(update.message.from_user.username) != None else '') + 'nome)'
            ' VALUES ('
            '' + str(update.message.from_user.id) + ", " + ''
            '' + (("'" + str(update.message.from_user.username) + "', ") if(update.message.from_user.username) != None else '') + ''
            '' + "'" + str(update.message.from_user.first_name) +  "')" + ''
        )
        #print(sql)
        cursor.execute(sql)
        di_db.commit()
        #print("Nuovo utente registrato")
    #if(update.message.from_user.username != "None"):
    bot.sendMessage(chat_id=update.message.chat_id, text="Inserisci la tua domanda")
    return 0 #stato successivo del conv handler
    

def nuova_domanda(bot, update):
    #prendere il valore di count nel DB, controllare se < 5 e aumentarlo di 1
    bot.sendMessage(chat_id=update.message.chat_id, text="La tua domanda è stata registrata.\nSe vuoi mandare un'altra domanda digita nuovamente /domanda")

    keyboard =  [[InlineKeyboardButton("Approva", callback_data=APPROVA)],
                 [InlineKeyboardButton("Scarta", callback_data=NONAPPROVA),
                  InlineKeyboardButton("Banna Utente", callback_data=BANNA)
                 ]
                ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(chat_id=chatid_redazione, text="Nuova domanda da @" + str(update.message.from_user.username) + "\n" + update.message.text, reply_markup=reply_markup)
    return ConversationHandler.END

def cancel(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Comando annullato")
    return ConversationHandler.END

def button(bot, update):
    msgID = update.callback_query.message.message_id
    msgChatID = update.callback_query.message.chat.id
    if(str(update.callback_query.data) == str(APPROVA)):
        msgText = update.callback_query.message.text + "\n\n" + "Approvata da " + update.callback_query.from_user.first_name + "\n\n#domandeimpossibili"
        bot.editMessageText(text = msgText, chat_id = msgChatID, message_id = msgID, reply_markup = None)
    elif(str(update.callback_query.data) == str(NONAPPROVA)):
        bot.deleteMessage(chat_id = msgChatID, message_id = msgID)
    elif(str(update.callback_query.data) == str(BANNA)):
        print("prova")


def read_db_conf():
    global di_db
    conf = open("dbconf.yaml", "r")
    doc = yaml.safe_load(conf)
    try:
        di_db = mysql.connector.connect(
            host = doc["db_host"],
            user = doc["db_user"],
            passwd = doc["db_psw" ],
            database = doc["db_name"]
        )
    except:
        print("DB connection error")
        return
    finally:
        print("DB connection successfull")

def main():
    print("Bot started at " + str(datetime.datetime.now().time()))

    read_db_conf()

    updater = Updater(token=token)
    dp = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dp.add_handler(start_handler)
    
    domanda_handler = CommandHandler('domanda', domanda)
    nuova_domanda_handler = MessageHandler(Filters.text, nuova_domanda)
    cancel_handler = CommandHandler('cancel', cancel)

    conv_handler = ConversationHandler(
        entry_points=[domanda_handler],

        states={
            0: [nuova_domanda_handler]
        },

        fallbacks=[cancel_handler]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()