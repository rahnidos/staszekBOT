from dbConnector import dbConnector
from telegram.ext import CommandHandler
from telegram.ext import Updater
#from staszek import staszek
import logging
import sys

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

db = dbConnector.Instance()

def findUserName(update, context):
    tusername=update.message.from_user.first_name
    if (update.message.from_user.last_name): tusername=update.message.from_user.last_name
    if (update.message.from_user.username): tusername=update.message.from_user.username
    return tusername
def answerTxt(update, context, ans):
    ans='@'+findUserName(update, context)+': '+ans
    context.bot.sendMessage(chat_id=update.effective_chat.id, text=ans)
#@#TODO answer photo

def start(update, context):
    answerTxt(update, context, 'Jestem Bot. Staszek Bot.')
    #@#TODO Komunikat startowy niech bierze też z bazy jako parametr

def question(update, context):
    answerTxt(update, context, 'tu będzie odpowiedź')

def main():
    btoken=db.getParam('token')
    if btoken==False:
        logging.error('No token! Are you configured this app correctly?')
        sys.exit(1)
    updater = Updater(token=btoken, use_context=True)
    dispatcher = updater.dispatcher
    comlist=db.getCommands()
    for com in comlist:
        dispatcher.add_handler(CommandHandler(com[0], eval(com[1])))

    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
	main()
