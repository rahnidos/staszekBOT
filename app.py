from dbConnector import dbConnector
from registry import registry
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

R = registry.Instance()
D = dbConnector.Instance()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARN
)
def prepareCommandsHandlers():
    rCommList=D.select_list('select alias from commands where type=1')
    for command in rCommList:
        start_handler=CommandHandler(command[0],eval(command[0]))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hola soy Staszek")

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Question Handler")



if __name__ == '__main__':

    
    #application = ApplicationBuilder().token(R.token).build()
    
    #start_handler = CommandHandler('start', start)
    
    prepareCommandsHandlers()
    #application.add_handler(start_handler)
    
    #application.run_polling()

