from dbConnector import dbConnector
import logging
from typing import Callable
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import dice as dice_module


load_dotenv()
debug = os.getenv("DEBUG")
TOKEN = os.getenv("TELEGRAM_TOKEN")
STASZEKHOME = os.getenv("STASZEKHOME")

ADMIN_IDS=os.getenv("ADMIN_IDS").split(",") if os.getenv("ADMIN_IDS") else []
D = dbConnector.Instance()

ASK_FOLDER_ID = 1

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

async def new_folder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if not admin_check(update, context):
        await update.message.reply_text("Za cieńki w uszach jesteś")
        return ConversationHandler.END
    if not args:
        await update.message.reply_text("Jaki folder mordo?")
        return ConversationHandler.END
    folder_name = " ".join(args)
    context.user_data["pending_folder_name"]=folder_name
    await update.message.reply_text(
        f"Podaj ID dla folderu kanału lub usera dla '{folder_name}':"
    )
    return ASK_FOLDER_ID

async def handle_folder_id(update: Update, context:ContextTypes.DEFAULT_TYPE): 
    folder_id = update.message.text.strip()
    folder_name = context.user_data["pending_folder_name"]
    folder_path = os.path.join(STASZEKHOME,'pics',folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    success = D.execute("INSERT INTO folders (id,name) VALUES (?,?)", (folder_id, folder_name))
    if not success:
        await update.message.reply_text("Błąd zapisu do bazy")
        return ConversationHandler.END
    await update.message.reply_text("Folder gotowy")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Anulowano.")
    return ConversationHandler.END

    
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

def initialize():
    D.execute("CREATE TABLE IF NOT EXISTS friends (id INTEGER PRIMARY KEY, name TEXT)")
    D.execute("""CREATE TABLE IF NOT EXISTS pics (
                 id INTEGER PRIMARY KEY, 
                 filename TEXT, 
                 counter INTEGER DEFAULT 0,
                 folder TEXT
              )
              """)
    D.execute("""CREATE TABLE IF NOT EXISTS folders (
                 id TEXT PRIMARY KEY,
                 name TEXT
              )
              """)


if __name__ == '__main__':

    initialize()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("hello", hello))
    app.add_error_handler(error_handler)

    folder_conv_handler=ConversationHandler(
        entry_points=[CommandHandler("nfolder",new_folder)],
        states={
            ASK_FOLDER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_folder_id)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(folder_conv_handler)

    setup_commands(app)    
    app.run_polling()

