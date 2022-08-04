from curses.ascii import isdigit
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
    'USER_REGISTER_NAME',
    'USER_REGISTER_MOBILE',
    'USER_REGISTER_HOUSE',
    'USER_REGISTER_ROOM',
    'EDIT_USER',
    'EDIT_USER_CATEGORY',
    'EDIT_USER_UPDATED',
    'EDIT_USER_UPDATED_HOUSE',
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
        context.user_data["name"] = None
        context.user_data["mobile"] = None
        context.user_data["house"] = None
        context.user_data["room"] = None
        context.user_data["edit_category"] = None
        print("RC4fe Bob is alive!")
        return user_menu(update, context)
    else:
        text = "Please private message the bot instead!"
        update.message.reply_text(text)
        return

# ====================  USER FUNCTIONS ====================

def user_menu(update, context):
    keyboard = []
    if not context.user_data['name']:
        keyboard.append([InlineKeyboardButton("Register", callback_data='user_register')])
    else:
        keyboard.append([InlineKeyboardButton("Edit Profile", callback_data='edit_user')])
    
    keyboard.append([InlineKeyboardButton("Order", callback_data='user_order')])
    keyboard.append([InlineKeyboardButton("Remind", callback_data='user_remind')])
    

    text = "What would you like Bob to do?"
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return USER_MENU

def user_register(update, context):
    update.callback_query.delete_message()
    text = "Hello! My Name is Bob and I am here to serve your needs for admin stuffs related to RC4fe. \n"
    text += "Before we start, please enter your name so that I can remember your existence"
    update.callback_query.message.chat.send_message(text)
    return USER_REGISTER_NAME

def user_register_name(update, context):
    user_name = update.message.text
    context.user_data['name'] = user_name

    text = f"Hello {user_name}!! What a nice name! Please share with me your mobile number so that I can contact you in the future."
    update.message.reply_text(text)
    return USER_REGISTER_MOBILE

def user_register_mobile(update, context):
    user_mobile = update.message.text
    context.user_data['mobile'] = user_mobile

    if not user_mobile.isnumeric():
        text = "Please enter numbers!"
        update.message.reply_text(text)
        return USER_REGISTER_MOBILE
    elif int(user_mobile) < 70000000:
        text = "Please enter a Singapore mobile number!"
        update.message.reply_text(text)
        return USER_REGISTER_MOBILE

    user_name = context.user_data['name']
    user_mobile = int(user_mobile)
    text = f"{user_name}, with contact number of {user_mobile} will be saved in my brain's memory. \n"
    text += "Which is the cool house that you are in?"
    
    keyboard = [
        [InlineKeyboardButton("Aquila", callback_data='Aquila')],
        [InlineKeyboardButton("Ursa", callback_data='Ursa')],
        [InlineKeyboardButton("Noctua", callback_data='Noctua')],
        [InlineKeyboardButton("Leo", callback_data='Leo')],
        [InlineKeyboardButton("Draco", callback_data='Draco')],
    ]
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return USER_REGISTER_HOUSE

def user_register_house(update, context):
    user_house = update.callback_query.data
    context.user_data['house'] = user_house

    text = f"{user_house} best house! \n"
    text += "Last question, what is your room number?"
    update.callback_query.message.chat.send_message(text)
    return USER_REGISTER_ROOM

def user_register_room(update, context):
    user_room = update.message.text
    context.user_data['room'] = user_room

    user_name = context.user_data['name']
    user_mobile = context.user_data['mobile']
    user_house = context.user_data['house']
    text = f"{user_name} from {user_house}, living in {user_room} and with contact number {user_mobile}. \n"
    text += "Thanks for the free stalking information! Just joking! Your details will be protected and will not be shared around. \n"
    text += "If you would like to edit your profile details, you can go to the /user_menu and click on the 'Edit Profile' button."
    update.message.reply_text(text)
    return USER_MENU

def edit_user(update, context):
    user_name = context.user_data['name']
    user_mobile = context.user_data['mobile']
    user_house = context.user_data['house']
    user_room = context.user_data['room']
    text = f"Name: {user_name} \n"
    text += f"Mobile Number: {user_mobile} \n"
    text += f"House: {user_house} \n"
    text += f"Room Number: {user_room} \n \n"

    text += "Would you like to edit your profile?"
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data='yes')],
        [InlineKeyboardButton("No", callback_data='no')],
    ]
    update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return EDIT_USER

def edit_user_followup(update, context):
    response = update.callback_query.data
    if response == "no":
        text = "Your profile will be just as it is, and there will be no changes. \n"
        text += "You can head back to /user_menu for more functions."
        update.callback_query.message.chat.send_message(text)
        return USER_MENU
    else:
        text = "You have chosen to update your profile. Which of the following needs to be updated?"
        keyboard = [
            [InlineKeyboardButton("Name", callback_data='name')],
            [InlineKeyboardButton("Mobile Number", callback_data='mobile')],
            [InlineKeyboardButton("House", callback_data='house')],
            [InlineKeyboardButton("Room Number", callback_data='room')],
        ]
        update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return EDIT_USER_CATEGORY

def edit_user_category(update, context):
    category = update.callback_query.data
    context.user_data['edit_category'] = category
    text = f"You have chosen to edit the category of {category}. \n"
    text += "Please enter the updated version."
    if category == "house":
        keyboard = [
            [InlineKeyboardButton("Aquila", callback_data='Aquila')],
            [InlineKeyboardButton("Ursa", callback_data='Ursa')],
            [InlineKeyboardButton("Noctua", callback_data='Noctua')],
            [InlineKeyboardButton("Leo", callback_data='Leo')],
            [InlineKeyboardButton("Draco", callback_data='Draco')],
        ]
        update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return EDIT_USER_UPDATED_HOUSE

    update.callback_query.message.chat.send_message(text)
    return EDIT_USER_UPDATED

def edit_user_updated_house(update, context):
    house = update.callback_query.data
    text = f"Your house has been changed to {house}. \n"
    text += f"You can head back to /user_menu for other functions."
    context.user_data['house'] = house
    update.callback_query.message.chat.send_message(text)
    return USER_MENU

def edit_user_updated(update, context):
    response = update.message.text
    category = context.user_data['edit_category'] 
    if category == "name":
        text = f"Your name has been updated to {response}. Nice to meet you! \n"
        context.user_data['name'] = response
    elif category == "mobile": 
        if not response.isnumeric():
            text = "Please enter numbers!"
            update.message.reply_text(text)
            return EDIT_USER_UPDATED
        elif int(response) < 70000000:
            text = "Please enter a Singapore mobile number!"
            update.message.reply_text(text)
            return EDIT_USER_UPDATED
        context.user_data['mobile'] = response
    elif category == "room":
        text = f"Your room has been updated to {response}. Nice to stalking you! \n"
        context.user_data['room'] = response
    
    text += f"You can head back to /user_menu for other functions."
    update.message.reply_text(text)
    return USER_MENU

def user_order(update, context):
    update.callback_query.delete_message()
    text = "Bob will now take the order for you... \n"
    text += "First item on the menu is "
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
                CallbackQueryHandler(user_register, pattern='user_register'),
                CallbackQueryHandler(edit_user, pattern='edit_user'),
                CallbackQueryHandler(user_order, pattern='user_order'),
                CallbackQueryHandler(user_remind, pattern='user_remind'),
            ],
            ADMIN_MENU: [
                CallbackQueryHandler(admin_order, pattern='admin_order'),
            ],
            USER_REGISTER_NAME: [
                MessageHandler(Filters.text, callback=user_register_name),
            ],
            USER_REGISTER_MOBILE:[
                MessageHandler(Filters.text, callback=user_register_mobile),
            ],
            USER_REGISTER_HOUSE:[
                CallbackQueryHandler(user_register_house),
            ],
            USER_REGISTER_ROOM:[
                MessageHandler(Filters.text, callback=user_register_room),
            ],
            EDIT_USER:[
                CallbackQueryHandler(edit_user_followup),
            ],
            EDIT_USER_CATEGORY:[
                CallbackQueryHandler(edit_user_category),
            ],
            EDIT_USER_UPDATED_HOUSE:[
                CallbackQueryHandler(edit_user_updated_house),
            ],
            EDIT_USER_UPDATED:[
                MessageHandler(Filters.text, callback=edit_user_updated),
            ]
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
    dispatcher.user_data[757010830] = {
        'name': "Qian",
        'mobile': 823167842163,
        'house': "Draco",
        'room': 1232,
    }

    updater.start_polling()
    updater.idle()