from dbConnector import dbConnector
from registry import registry
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from gepetto import gepetto


R = registry.Instance()
D = dbConnector.Instance()
G = gepetto()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARN
)


def prepareCommandsHandlers():
    rCommList=D.select_list('select real from commands where type=1')
    for command in rCommList:
        application.add_handler(CommandHandler(command[0],eval(command[0])))




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=R.t['start'])

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer=G.askGepetto(" ".join(context.args))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Roll Handler")

async def randMember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="randMemebr Handler")

async def rollLocation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="roll Location")


if __name__ == '__main__':

    
    application = ApplicationBuilder().token(R.cfg['token']).build()
    
    
    prepareCommandsHandlers()
    
    application.run_polling()

