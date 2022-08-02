import traceback

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
)

from keys import API_KEY, USER_ADMINS

# To assign each status to a number
_STATES = [
    'USER_MENU',
    'ADMIN_MENU',
]

# Set some state variables
# MAIN_MENU= range(7)
for i, state in enumerate(_STATES):
    globals()[state] = i

def start(update, context):
    chat_id = update.effective_chat.id

    if chat_id > 0: #private message
        if "registered" in context.user_data and context.user_data['registered']:
            return user_menu(update, context)

        if chat_id in USER_ADMINS:
            text = "Welcome to the exclusive ADMINS ONLY page!!!!"
            update.message.reply_text(text)
            return admin_menu(update, context)

        # RESIDENTS
        text = "Hello! I am RC4fe Telegram bot, called Bob!"
        update.message.reply_text(text)
        print("RC4fe Bob is alive!")
        return user_menu(update, context)
    else:
        text = "Please private message the bot instead!"
        update.message.reply_text(text)
        return

def user_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Order", callback_data='user_order')],
        [InlineKeyboardButton("Remind", callback_data='user_remind')],
    ]

    text = "What would you like Bob to do?"
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return USER_MENU

def user_order(update, context):
    update.callback_query.delete_message()
    text = "USER ORDER"
    print(text)
    update.callback_query.message.chat.send_message(text)
    return

def user_remind(update, context):
    update.callback_query.delete_message()
    text = "USER REMIND"
    update.callback_query.message.chat.send_message(text)
    return

# ==================== ADMIN FUNCTIONS ====================

def admin_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("order", callback_data='order'), ],

    ]
    text = "Welcome to the admin menu! Bob is at your command..."
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_MENU

def admin_order(update, context):
    text = "ADMIN ORDER"
    update.message.reply_text(text)
    return

if __name__ == '__main__':
    top_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
             # current status: whatisreceivedfromuser(function to be called, pattern  = 'callback_data')
            USER_MENU: [
                CallbackQueryHandler(user_order, pattern='user_order'),
                CallbackQueryHandler(user_remind, pattern='user_remind'),
            ],
            ADMIN_MENU: [
                CallbackQueryHandler(admin_order, pattern='admin_order'),
            ],
        },

        # after /start, these commands will take over for menu page
        fallbacks=[
            CommandHandler('user_menu', callback=user_menu),
            CommandHandler('admin_menu', callback=admin_menu),
        ]
    )

    updater = Updater(API_KEY, use_context=True)
    dispatcher = Updater(API_KEY)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(top_conv)
    # dispatcher.add_error_handler(err)

    updater.start_polling()
    updater.idle()