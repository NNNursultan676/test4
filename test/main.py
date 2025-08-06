from telegram.ext import Application, CommandHandler
from config import BOT_TOKEN

async def start_handler(update, context):
    await update.message.reply_text("Привет! Я работаю.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_handler))

    application.run_polling()
