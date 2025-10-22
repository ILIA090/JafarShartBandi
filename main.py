import telebot
from telebot import types
import json
import random
from datetime import datetime

TOKEN = "8246648556:AAG6yvrLYsQN-GlgdrPBgBWmNmKfNE4bgWo"
OWNER_ID = 7776714237  # آیدی خودت
DATA_FILE = "data.json"
BOT_STATUS = {"active": True}

bot = telebot.TeleBot(TOKEN)

# بارگذاری یا ساخت داده‌ها
try:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
except:
    data = {"users": {}, "banned": []}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ======= منوی اصلی مالک =======
def owner_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💰 دادن کوین", callback_data="give_coin"))
    markup.add(types.InlineKeyboardButton("➖ گرفتن کوین", callback_data="take_coin"))
    markup.add(types.InlineKeyboardButton("⚙️ تنظیم کوین", callback_data="set_coin"))
    markup.add(types.InlineKeyboardButton("🚫 بن کردن", callback_data="ban_user"))
    markup.add(types.InlineKeyboardButton("✅ حذف بن", callback_data="unban_user"))
    markup.add(types.InlineKeyboardButton("🔴 خاموش کردن بات", callback_data="turn_off"))
    markup.add(types.InlineKeyboardButton("🟢 روشن کردن بات", callback_data="turn_on"))
    bot.send_message(chat_id, "سلام مالک عزیز! 👑\nمنوی مدیریت:", reply_markup=markup)

# ======= منوی کاربران معمولی =======
def user_main_menu(chat_id, username):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ℹ️ اطلاعات من", callback_data="info"))
    markup.add(types.InlineKeyboardButton("🎲 انداختن تاس", callback_data="dice"))
    markup.add(types.InlineKeyboardButton("💸 انتقال کوین", callback_data="transfer"))
    markup.add(types.InlineKeyboardButton("📝 گزارش", callback_data="report"))
    bot.send_message(chat_id, f"سلام {username}!\nتاریخ عضویت: {datetime.now().strftime('%Y-%m-%d')}\nمنو👇", reply_markup=markup)

# ======= هندلر /start =======
@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.first_name
    
    if not BOT_STATUS["active"] and user_id != str(OWNER_ID):
        bot.send_message(chat_id, "⚠️ ربات خاموش است!")
        return
    
    # مالک
    if message.from_user.id == OWNER_ID:
        owner_main_menu(chat_id)
        return
    
    # کاربران معمولی
    if user_id not in data["users"]:
        data["users"][user_id] = {"username": username, "coins": 0, "join_date": datetime.now().strftime("%Y-%m-%d")}
        save_data()
    
    if user_id in data["banned"]:
        bot.send_message(chat_id, "🚫 شما از بات بن شده‌اید!")
        return
    
    user_main_menu(chat_id, username)

# ======= هندلر دکمه‌ها =======
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = str(call.from_user.id)
    chat_id = call.message.chat.id

    # مالک
    if user_id == str(OWNER_ID):
        if call.data == "give_coin":
            msg = bot.send_message(chat_id, "👤 لطفا username کاربر را وارد کنید:")
            bot.register_next_step_handler(msg, give_coin)
        elif call.data == "take_coin":
            msg = bot.send_message(chat_id, "👤 لطفا username کاربر را وارد کنید:")
            bot.register_next_step_handler(msg, take_coin)
        elif call.data == "set_coin":
            msg = bot.send_message(chat_id, "👤 لطفا username کاربر را وارد کنید:")
            bot.register_next_step_handler(msg, set_coin)
        elif call.data == "ban_user":
            msg = bot.send_message(chat_id, "👤 لطفا username کاربر را برای بن کردن وارد کنید:")
            bot.register_next_step_handler(msg, ban_user)
        elif call.data == "unban_user":
            msg = bot.send_message(chat_id, "👤 لطفا username کاربر را برای حذف بن وارد کنید:")
            bot.register_next_step_handler(msg, unban_user)
        elif call.data == "turn_off":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✅ بله", callback_data="confirm_off"))
            markup.add(types.InlineKeyboardButton("❌ خیر", callback_data="cancel_off"))
            bot.send_message(chat_id, "آیا مطمئن هستید می‌خواهید بات را خاموش کنید؟", reply_markup=markup)
        elif call.data == "turn_on":
            BOT_STATUS["active"] = True
            bot.send_message(chat_id, "🟢 ربات روشن شد!")
    
    # کاربر معمولی
    else:
        if user_id in data["banned"]:
            bot.send_message(chat_id, "🚫 شما از بات بن شده‌اید!")
            return
        if call.data == "info":
            user = data["users"][user_id]
            bot.send_message(chat_id, f"👤 Username: {user['username']}\n💰 کوین‌ها: {user['coins']}\n📅 تاریخ عضویت: {user['join_date']}")
        elif call.data == "dice":
            msg = bot.send_message(chat_id, "💰 تعداد کوین که می‌خواهید شرط بندی کنید را وارد کنید:")
            bot.register_next_step_handler(msg, dice_bet)
        elif call.data == "transfer":
            msg = bot.send_message(chat_id, "👤 لطفا username کاربر مقصد را وارد کنید:")
            bot.register_next_step_handler(msg, transfer_username)
        elif call.data == "report":
            msg = bot.send_message(chat_id, "📝 متن گزارش را ارسال کنید:")
            bot.register_next_step_handler(msg, report)

# ======= توابع مالک =======
def give_coin(message):
    username = message.text
    for uid, user in data["users"].items():
        if user["username"] == username:
            msg = bot.send_message(message.chat.id, "💰 تعداد کوین برای دادن را وارد کنید:")
            bot.register_next_step_handler(msg, lambda m: add_coins(uid, m.text))
            return
    bot.send_message(message.chat.id, "❌ کاربر پیدا نشد!")

def add_coins(uid, amount):
    if not amount.isdigit():
        return
    data["users"][uid]["coins"] += int(amount)
    save_data()
    bot.send_message(OWNER_ID, f"💰 کوین اضافه شد به {data['users'][uid]['username']} : {amount}")

def take_coin(message):
    username = message.text
    for uid, user in data["users"].items():
        if user["username"] == username:
            msg = bot.send_message(message.chat.id, "➖ تعداد کوین برای کم کردن را وارد کنید:")
            bot.register_next_step_handler(msg, lambda m: remove_coins(uid, m.text))
            return
    bot.send_message(message.chat.id, "❌ کاربر پیدا نشد!")

def remove_coins(uid, amount):
    if not amount.isdigit():
        return
    data["users"][uid]["coins"] -= int(amount)
    if data["users"][uid]["coins"] < 0:
        data["users"][uid]["coins"] = 0
    save_data()
    bot.send_message(OWNER_ID, f"➖ کوین کم شد از {data['users'][uid]['username']} : {amount}")

def set_coin(message):
    username = message.text
    for uid, user in data["users"].items():
        if user["username"] == username:
            msg = bot.send_message(message.chat.id, "⚙️ تعداد کوین جدید را وارد کنید:")
            bot.register_next_step_handler(msg, lambda m: set_coins(uid, m.text))
            return
    bot.send_message(message.chat.id, "❌ کاربر پیدا نشد!")

def set_coins(uid, amount):
    if not amount.isdigit():
        return
    data["users"][uid]["coins"] = int(amount)
    save_data()
    bot.send_message(OWNER_ID, f"⚙️ کوین {data['users'][uid]['username']} تنظیم شد به : {amount}")

def ban_user(message):
    username = message.text
    for uid, user in data["users"].items():
        if user["username"] == username:
            data["banned"].append(uid)
            save_data()
            bot.send_message(OWNER_ID, f"🚫 کاربر {username} بن شد!")
            return
    bot.send_message(message.chat.id, "❌ کاربر پیدا نشد!")

def unban_user(message):
    username = message.text
    for uid, user in data["users"].items():
        if user["username"] == username:
            if uid in data["banned"]:
                data["banned"].remove(uid)
                save_data()
                bot.send_message(OWNER_ID, f"✅ بن کاربر {username} حذف شد!")
            return
    bot.send_message(message.chat.id, "❌ کاربر پیدا نشد!")

# ======= توابع کاربران =======
def dice_bet(message):
    user_id = str(message.from_user.id)
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "❌ حتماً باید عدد بفرستید!")
        return
    amount = int(message.text)
    if data["users"][user_id]["coins"] < amount:
        bot.send_message(message.chat.id, "❌ کوین کافی ندارید!")
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("زوج", callback_data=f"dice_even_{amount}"))
    markup.add(types.InlineKeyboardButton("فرد", callback_data=f"dice_odd_{amount}"))
    bot.send_message(message.chat.id, "🎲 انتخاب کنید شانس خود را زوج یا فرد؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("dice_"))
def dice_result(call):
    user_id = str(call.from_user.id)
    choice, amount = call.data.split("_")[1], int(call.data.split("_")[2])
    roll = random.randint(1,6)
    won = (roll % 2 == 0 and choice == "even") or (roll % 2 == 1 and choice == "odd")
    if won:
        data["users"][user_id]["coins"] += amount
        bot.send_message(call.message.chat.id, f"🎉 عدد {roll} آمد! شما برنده شدید و {amount} کوین بردید!")
    else:
        data["users"][user_id]["coins"] -= amount
        bot.send_message(call.message.chat.id, f"😢 عدد {roll} آمد! شما باختید و {amount} کوین کم شد!")
    save_data()

def transfer_username(message):
    user_id = str(message.from_user.id)
    username = message.text
    for uid, user in data["users"].items():
        if user["username"] == username:
            msg = bot.send_message(message.chat.id, "💸 چند کوین می‌خواهید انتقال دهید؟")
            bot.register_next_step_handler(msg, lambda m: transfer_coins(user_id, uid, m.text))
            return
    bot.send_message(message.chat.id, "❌ کاربر پیدا نشد!")

def transfer_coins(from_uid, to_uid, amount):
    if not amount.isdigit():
        return
    amount = int(amount)
    if data["users"][from_uid]["coins"] < amount:
        bot.send_message(from_uid, "❌ کوین کافی ندارید!")
        return
    data["users"][from_uid]["coins"] -= amount
    data["users"][to_uid]["coins"] += amount
    save_data()
    bot.send_message(from_uid, f"💸 انتقال موفقیت آمیز بود! {amount} کوین به {data['users'][to_uid]['username']} فرستاده شد.")

def report(message):
    bot.send_message(OWNER_ID, f"📝 گزارش از {message.from_user.username}:\n{message.text}")
    bot.send_message(message.chat.id, "✅ گزارش شما ارسال شد!")

# ======= هندلر خاموش کردن/روشن کردن =======
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_off","cancel_off"])
def turn_off_confirm(call):
    if call.data == "confirm_off":
        BOT_STATUS["active"] = False
        bot.send_message(call.message.chat.id, "🔴 ربات خاموش شد!")
    else:
        owner_main_menu(call.message.chat.id)

# ======= اجرای ربات =======
bot.infinity_polling()
  
