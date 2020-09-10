from dbConnector import dbConnector
from telegram.ext import CommandHandler
from telegram.ext import Updater
import logging
import sys

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

db = dbConnector.Instance()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Jestem Bot. Staszek Bot.")
    #@#TODO Komunikat startowy niech bierze też z bazy jako parametr

def main():
    btoken=db.getParam('token')
    if btoken==False:
        logging.error('No token! Are you configured this app correctly?')
        sys.exit(1)
    updater = Updater(token=btoken, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
	main()
