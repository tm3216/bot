import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, Update
import sqlite3


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)


async def echo(update: Update, context):
    reply_keyboard = [['/new_order', '/order_list'],
                      ['/help']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Добро пожаловать", reply_markup=markup)


async def new_order(update: Update, context):
    await update.message.reply_text("Введите адрес")
    return 2


async def adress_new_order(update: Update, context):
    locality = update.message.text
    con = sqlite3.connect("orders")
    cur = con.cursor()
    cur.execute(f"INSERT into orders (adress) values ('{locality}')")
    con.commit()
    print(locality)
    await update.message.reply_text('Укажите цену')


async def stop(update: Update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    application = Application.builder().token("6944853635:AAHGpI8v4TBjauMG6gx9LAHtzKN_uHa6u6g").build()
    text_handler = MessageHandler(filters.TEXT & filters.COMMAND, echo)
    application.add_handler(CommandHandler("new_order", new_order))
    application.add_handler(CommandHandler("adress_new_order", adress_new_order))
    application.add_handler(text_handler)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('echo', echo)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_order)],
            2: [MessageHandler(~filters.TEXT & filters.COMMAND, adress_new_order)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
