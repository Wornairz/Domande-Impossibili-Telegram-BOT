# coding: utf-8

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
import logging
import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def domanda(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Inserisci la tua domanda")
    return 0

def nuovaDomanda(bot, update):
    print(update.message.text)
    bot.sendMessage(chat_id=update.message.chat_id, text="La tua domanda è stata registrata.\nSe vuoi mandare un'altra domanda digita nuovamente \\domanda")
    return ConversationHandler.END

def cancel(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Comando annullato")
    return ConversationHandler.END

def main():
    print("Bot started at " + str(datetime.datetime.now().time()))
    token = open('token.conf', 'r').read()
    #chatid_redazione = open('chatid.conf', 'r').read()
    
    updater = Updater(token=token)
    dp = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dp.add_handler(start_handler)
    
    domandaHandler = CommandHandler('domanda', domanda)
    nuovaDomandaHandler = MessageHandler(Filters.text, nuovaDomanda)
    cancelHandler = CommandHandler('cancel', cancel)

    conv_handler = ConversationHandler(
        entry_points=[domandaHandler],

        states={
            0: [nuovaDomandaHandler]
        },

        fallbacks=[cancelHandler]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()