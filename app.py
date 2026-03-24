from dbConnector import dbConnector
import logging
from typing import Callable
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv
import os
import dice as dice_module


load_dotenv()
debug = os.getenv("DEBUG")
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS=os.getenv("ADMIN_IDS").split(",") if os.getenv("ADMIN_IDS") else []
D = dbConnector.Instance()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARN
)

def admin_check(update, context) -> bool:
    admin_ids = ADMIN_IDS
    user_id = update.effective_user.id
    return str(user_id) in admin_ids

async def start_handler(update, context):
    await update.message.reply_text("uźyj /help, źeby zobaczyć co umiem")

async def restart_bot(update, context):
    await update.message.reply_text("OK")
   
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def dice_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Użyj: /dice k6+4 (albo inny format dice)")
        return

    dice_expr = context.args[0]
    d = dice_module.Dice.Instance()
    result = d.roll(dice_expr)
    await update.message.reply_text(f'{result}')
    
COMMANDS = [
    {
        "name": "start",
        "handler": start_handler,
        "only_admin": False,
    },
    {
        "name": "restart",
        "handler": restart_bot,
        "only_admin": True,
    },
    {
        "name": "dice",
        "handler": dice_cmd,
        "only_admin": False,
    },
]

async def admin_cmd(update, context, handler):
    if not admin_check(update, context):
        await update.message.reply_text("Za cieńki w uszach jesteś")
        return
    await handler(update, context)

def setup_commands(app):
    for cmd in COMMANDS:
        name=cmd["name"]
        handler=cmd["handler"]
        only_admin=cmd["only_admin"]

        if only_admin:
            async def _admin_handler(update, context, handler=handler):
                await admin_cmd(update, context, handler)
            app.add_handler(CommandHandler(name, _admin_handler))
        else:
            app.add_handler(CommandHandler(name, handler))

async def error_handler(update, context):
    logging.error(f"Update {update} caused error {context.error}")

if __name__ == '__main__':

    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("hello", hello))
    app.add_error_handler(error_handler)
    setup_commands(app)    
    app.run_polling()

