from curses.ascii import isdigit
import traceback
from operator import itemgetter

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
    'ADMIN_ORDER_FUNCTIONS',
    'ADMIN_ORDER_ADD_NAME',
    'ADMIN_ORDER_ADD_DESC',
    'ADMIN_ORDER_ADD_PRICE',
    'ADMIN_ORDER_ADD_PHOTO',
    'ADMIN_ORDER_EDIT_ITEM',
    'ADMIN_ORDER_REMOVE_ITEM',
    'ADMIN_ORDER_EDIT_ITEM_CATEGORY',
    'ADMIN_ORDER_EDIT_ITEM_UPDATED',
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
            context.user_data["edit_index"] = None
            context.user_data["edit_category"] = None
            context.bot_data["total_num_of_orders"] = 0  # 1-indexed
            context.bot_data["curr_order_index"] = 0 # start from 0
            context.bot_data["orders"] = []
            if len(context.bot_data["orders"]) == 0:
                context.bot_data["orders"].append({ # for 1-indexing
                    "order_index": 0,
                    "name": None,
                    "desc": None,
                    "price": None,
                    "photo": None
                })
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
    # chat_id = update.message.chat_id
    # print("CHAT ID IS ", chat_id)
    return USER_MENU

# USER REGISTER 
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

# USER EDIT 

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
    text = f"You have chosen to update your {category}. \n"
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
    update.callback_query.delete_message()
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

# USER ORDER 

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
        [InlineKeyboardButton("Order", callback_data='admin_order'), ],
    ]
    if len(context.bot_data["orders"]) == 0:
        context.bot_data["orders"].append({ # for 1-indexing
            "order_index": 0,
            "name": None,
            "desc": None,
            "price": None,
            "photo": None
        })
    text = "Welcome to the admin menu! Bob is at your command..."
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    print("An admin has started the bot")
    return ADMIN_MENU

def admin_order(update, context):
    keyboard = []
    total_num_of_orders = context.bot_data["total_num_of_orders"]
    text = f"Total number of orders: {total_num_of_orders}. \n"

    keyboard.append([InlineKeyboardButton("Add", callback_data='admin_order_add')])
    keyboard.append([InlineKeyboardButton("Edit", callback_data='admin_order_edit')])
    keyboard.append([InlineKeyboardButton("Remove", callback_data='admin_order_remove')])
    keyboard.append([InlineKeyboardButton("Remove All", callback_data='admin_order_remove_all')])
    text += "To add in new items, you can click the 'Add' keyboard.\n"
    text += "If there isn't any more items to be added, please click the 'remove' keyboard."
    update.callback_query.message.chat.send_message(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_ORDER_FUNCTIONS

def admin_order_add(update, context):
    update.callback_query.delete_message()
    text = "You have selected to add on to the current list of orders. \n"
    text += "Let's start off with the name of the item that you are selling. \n"
    update.callback_query.message.chat.send_message(text)
    return ADMIN_ORDER_ADD_NAME

def admin_order_add_name(update, context):
    name = update.message.text
    context.bot_data["total_num_of_orders"] += 1
    context.bot_data["curr_order_index"] += 1
    total_num_of_orders = context.bot_data["total_num_of_orders"] 
    curr_order_index = context.bot_data["curr_order_index"]
    text = f"Total number of orders: {total_num_of_orders} \n "
    text += f"Current order index: {curr_order_index} \n "
    text += f"The item name will be {name} \n"
    context.bot_data["orders"].append({
        "order_index": curr_order_index,
        "name": name,
        "desc": None,
        "price": None,
        "photo": None
    })
    text += "Now, do give a short description of the item"
    update.message.reply_text(text)
    return ADMIN_ORDER_ADD_DESC

def admin_order_add_desc(update, context):
    desc = update.message.text
    text = f"Description saved! \n"
    text += "How much will you be selling this for?"

    curr_order_index = context.bot_data["curr_order_index"]
    context.bot_data["orders"][curr_order_index]["desc"] = desc  
    update.message.reply_text(text)
    return ADMIN_ORDER_ADD_PRICE

def admin_order_add_price(update, context):
    price = update.message.text
    try:
        if float(price) or int(price):
            curr_order_index = context.bot_data["curr_order_index"]
            context.bot_data["orders"][curr_order_index]["price"] = price  
            item = context.bot_data["orders"][curr_order_index]["name"]
            text = f"The price for {item} will be at ${price}. \n"
            text += "Please insert a photo so that people can have some visualisation of what the item is."
            update.message.reply_text(text)
            return ADMIN_ORDER_ADD_PHOTO
    except:
        text = "Please provide in integer or float values."
        update.message.reply_text(text)
        return ADMIN_ORDER_ADD_PRICE

def admin_order_add_photo(update, context):
    photo = update.message.photo[-1].file_id
    curr_order_index = context.bot_data["curr_order_index"]
    context.bot_data["orders"][curr_order_index]["photo"] = photo
    text = f"Photo captured! \n"
    text += "You can continue adding items from /admin_menu order function."
    update.message.reply_text(text)
    chat_id = update.message.chat_id
    try:
        context.bot.send_photo(
            chat_id,
            photo=photo,
            caption=(
                "This is the photo that you have sent."
            )
        )
        print(context.bot_data["orders"])
        return ADMIN_MENU
    except IndexError:
        text = "Please send a photo! \n"
        update.message.reply_text(text)
        return ADMIN_ORDER_ADD_PRICE

def admin_order_edit(update, context):
    keyboard = []
    total_num_of_orders = context.bot_data["total_num_of_orders"]
    for order_index in range(1, total_num_of_orders+1):
        order_name = context.bot_data["orders"][order_index]["name"]
        keyboard.append([InlineKeyboardButton(order_name, callback_data=order_name)])
        print(order_name)
    text = "These are the current orders that Bob knows. You can click into any of them to edit. \n"
    update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_ORDER_EDIT_ITEM

def admin_order_edit_item(update, context):
    item = update.callback_query.data
    text = f"You have chosen to edit {item}. \n"
    print(context.bot_data["orders"])
    print("FIND THIS: ", item)
    item_index = list(map(itemgetter('name'), context.bot_data["orders"])).index(item)
    context.user_data["edit_index"] = item_index
    text += "Now, look carefully on the details for the item, and select which one to edit. \n"
    order = context.bot_data["orders"][item_index]
    text += f"Name: {order['name']}\n"
    text += f"Desc: {order['desc']}\n"
    text += f"Price: {order['price']}\n"
    text += f"Photo: {order['photo']}\n"
    
    keyboard = [
        [InlineKeyboardButton("Name", callback_data='name')],
        [InlineKeyboardButton("Desc", callback_data='desc')],
        [InlineKeyboardButton("Price", callback_data='price')],
        [InlineKeyboardButton("Photo", callback_data='photo')],
    ]
    update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_ORDER_EDIT_ITEM_CATEGORY

def admin_order_edit_item_category(update, context):
    category = update.callback_query.data
    text = f"You have chosen to edit the {category}. \n"
    if category == "price":
        text += "Price has to be a float in 2 decimal places. (There will be no checks here) \n"
    text += "Please send the updated version to me in the next text. \n"
    update.callback_query.message.chat.send_message(text)
    context.user_data["edit_category"] = category
    return ADMIN_ORDER_EDIT_ITEM_UPDATED

def admin_order_edit_item_updated(update, context):
    category = context.user_data["edit_category"]
    if category == 'photo':
        message = update.message.photo[-1].file_id
    else:
        message = update.message.text
    
    item_index = context.user_data["edit_index"]
    order = context.bot_data["orders"][item_index]
    order[category] = message
    text = "This is the updated list, and if you wish to update anything else, please head back to /admin_menu. \n"
    text += f"Name: {order['name']}\n"
    text += f"Desc: {order['desc']}\n"
    text += f"Price: {order['price']}\n"
    text += f"Photo: {order['photo']}\n"
    update.message.reply_text(text)
    return ADMIN_MENU

def admin_order_remove(update, context):
    text = "Choose which order to remove. \n"
    keyboard = []
    total_num_of_orders = context.bot_data["total_num_of_orders"]
    for order_index in range(1, total_num_of_orders+1):
        order_name = context.bot_data["orders"][order_index]["name"]
        keyboard.append([InlineKeyboardButton(order_name, callback_data=order_name)])
    update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_ORDER_REMOVE_ITEM

def admin_order_remove_item(update, context):
    item = update.callback_query.data
    text = f"{item} removed! \n"
    # Find the position of the item in the list
    # Pop item and bring the rest forward.
    # Total num of orders -= 1

    update.callback_query.message.chat.send_message(text)
    return ADMIN_MENU

def admin_order_remove_all(update, context):
    total_num_of_orders = 0
    context.bot_data["total_num_of_orders"] = total_num_of_orders  # 1-indexed
    context.bot_data["curr_order_index"] = 0 # start from 0
    context.bot_data["orders"] = []
    text = "All of the previous orders have been cleared. \n"
    text = f"Total number of orders: {total_num_of_orders} \n "
    update.callback_query.message.edit_text(text)
    return ADMIN_MENU

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
            ],
            ADMIN_MENU: [
                CallbackQueryHandler(admin_order)
            ],
            ADMIN_ORDER_FUNCTIONS: [ #NEW
                CallbackQueryHandler(admin_order_add, pattern='admin_order_add'),
                CallbackQueryHandler(admin_order_edit, pattern='admin_order_edit'),
                CallbackQueryHandler(admin_order_remove, pattern='admin_order_remove'),
                CallbackQueryHandler(admin_order_remove_all, pattern='admin_order_remove_all'),
            ],
            ADMIN_ORDER_ADD_NAME:[
                MessageHandler(Filters.text, callback=admin_order_add_name),
            ],
            ADMIN_ORDER_ADD_DESC:[
                MessageHandler(Filters.text, callback=admin_order_add_desc),
            ],
            ADMIN_ORDER_ADD_PRICE:[
                MessageHandler(Filters.text, callback=admin_order_add_price),
            ],
            ADMIN_ORDER_ADD_PHOTO:[
                MessageHandler(Filters.photo, callback=admin_order_add_photo),
            ],
            ADMIN_ORDER_EDIT_ITEM:[
                CallbackQueryHandler(admin_order_edit_item)
            ],
            ADMIN_ORDER_EDIT_ITEM_CATEGORY:[
                CallbackQueryHandler(admin_order_edit_item_category)
            ],
            ADMIN_ORDER_EDIT_ITEM_UPDATED:[
                MessageHandler(Filters.all, callback=admin_order_edit_item_updated),
            ],
            ADMIN_ORDER_REMOVE_ITEM:[
                CallbackQueryHandler(admin_order_remove_item)
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
    # dispatcher.bot_data["total_num_of_orders"] = 1
    # dispatcher.bot_data["orders"] = []
    # dispatcher.bot_data["orders"].append({
    #     "order_index": 1,
    #     'name': "Qian",
    #     'desc': "this",
    #     'price': 6,
    #     'photo': None,
    # })


    updater.start_polling()
    updater.idle()