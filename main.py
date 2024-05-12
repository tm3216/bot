import sqlite3
import logging
from typing import Dict
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_COST, TYPING_COMMENT, CHECK, CHECK1, CHECK2 = range(6)

reply_keyboard = [["Добавить заказ"], ['Список заказов']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        "Добро пожаловать",
        reply_markup=markup,
    )
    return CHOOSING


async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f"Введите адрес")
    return TYPING_COST


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    user_data['adress'] = text
    await update.message.reply_text('Укажите цену')
    return TYPING_COMMENT


async def input_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    user_data['summ'] = text
    await update.message.reply_text('Добавьте комментарий')
    return CHECK


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    user_data['comment'] = text
    keyboard = [["Подтвердить"], ["Отмена", "Редактировать"]]
    kb = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(f"Проверьте:\n адрес: {user_data['adress']}\n цена: {user_data['summ']}\n комментарий: {user_data['comment']}", reply_markup=kb)
    return CHECK1


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['В главное меню']]
    kb = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    con = sqlite3.connect("orders")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO orders (adress, summ, comment)
                    VALUES ('{context.user_data['adress']}', {int(context.user_data['summ'])}, '{context.user_data['comment']}')''')
    con.commit()
    con.close()
    await update.message.reply_text('Заказ добавлен', reply_markup=kb)
    return CHECK2


async def order_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    con = sqlite3.connect("orders")
    cur = con.cursor()
    list_of_orders = list(cur.execute(f'''SELECT id, adress, summ, comment FROM orders'''))
    keyboard = [[]]
    for el in list_of_orders:
        await update.message.reply_text(f'Заказ №{el[0]}: \n адрес: {el[1]}\n цена: {el[2]}\n комментарий: {el[3]}')
        keyboard[0].append(str(el[0]))
    kb = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Выберите заказ, который хотите взять', reply_markup=kb)


def main():
    application = Application.builder().token("6944853635:AAHGpI8v4TBjauMG6gx9LAHtzKN_uHa6u6g").build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("Добавить заказ"), regular_choice
                ),
                MessageHandler(
                    filters.Regex("Список заказов"), order_list
                )
            ],
            TYPING_COMMENT: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), input_comment
                )
            ],
            TYPING_COST: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    received_information,
                )
            ],
            CHECK: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    check,
                )
            ],
            CHECK1: [
                MessageHandler(
                    filters.Regex("Подтвердить"), add
                ),
                MessageHandler(
                    filters.Regex("Отмена"), start
                ),
                MessageHandler(
                    filters.Regex("Редактировать"), regular_choice
                )
            ],
            CHECK2: [
                MessageHandler(
                    filters.Regex("В главное меню"), start
                )
            ]
        },
        fallbacks=[MessageHandler(filters.TEXT, start)],
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
