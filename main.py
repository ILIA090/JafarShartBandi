import telebot
from telebot import types
import json
from datetime import datetime
import random
import os

# ====== تنظیمات اولیه ======
TOKEN = "YOUR_BOT_TOKEN"
OWNER_USERNAME = "iliaManzari"  # بدون @

bot = telebot.TeleBot(TOKEN)
data_file = "data.json"

# ====== توابع ذخیره و لود داده ======
def load_data():
    if not os.path.exists(data_file):
        return {"users": {}, "banned": [], "bot_on": True}
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data():
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ====== شروع ربات ======
@bot.message_handler(commands=["start"])
def start(message):
    user = message.from_user
    username = user.username or f"id_{user.id}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # بررسی روشن بودن ربات
    if not data.get("bot_on", True) and username != OWNER_USERNAME:
        bot.send_message(message.chat.id, "⚠️ ربات در حال حاضر خاموش است.")
        return

    # بررسی بن
    if username in data.get("banned", []):
        bot.send_message(message.chat.id, "⛔ شما از استفاده از ربات بن شده‌اید!")
        return

    # ثبت کاربر
    if username not in data["users"]:
        data["users"][username] = {"coins": 10, "joined": now}
        save_data()

    # منو مالک
    if username == OWNER_USERNAME:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("💰 دادن کوین", callback_data="give_coin"),
            types.InlineKeyboardButton("💸 گرفتن کوین", callback_data="take_coin")
        )
        markup.add(
            types.InlineKeyboardButton("⚖️ تنظیم کوین", callback_data="set_coin")
        )
        markup.add(
            types.InlineKeyboardButton("🚫 بن کردن کاربر", callback_data="ban_user"),
            types.InlineKeyboardButton("✅ حذف بن", callback_data="unban_user")
        )
        markup.add(
            types.InlineKeyboardButton("🔴 خاموش کردن ربات", callback_data="off_bot"),
            types.InlineKeyboardButton("🟢 روشن کردن ربات", callback_data="on_bot")
        )
        bot.send_message(message.chat.id,
                         f"👑 خوش آمدی {user.first_name}!\n\n"
                         "📍 پنل مدیریت فعال شد:",
                         reply_markup=markup)
    else:
        # منو کاربران عادی
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("ℹ️ اطلاعات من", callback_data="info"),
            types.InlineKeyboardButton("🎲 انداختن تاس", callback_data="dice")
        )
        markup.add(
            types.InlineKeyboardButton("💱 انتقال کوین", callback_data="transfer"),
            types.InlineKeyboardButton("📢 گزارش", callback_data="report")
        )
        bot.send_message(message.chat.id,
                         f"🎉 خوش آمدی @{username}!\n📅 تاریخ عضویت: {now}",
                         reply_markup=markup)

# ====== کال‌بک دکمه‌ها ======
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    username = call.from_user.username or f"id_{call.from_user.id}"
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    # ===== پنل مالک =====
    if username == OWNER_USERNAME:
        if call.data == "give_coin":
            bot.edit_message_text("👤 لطفاً نام کاربر را بفرستید:", chat_id, msg_id)
            bot.register_next_step_handler(call.message, give_coin_user)
        elif call.data == "take_coin":
            bot.edit_message_text("👤 نام کاربر را بفرستید:", chat_id, msg_id)
            bot.register_next_step_handler(call.message, take_coin_user)
        elif call.data == "set_coin":
            bot.edit_message_text("👤 نام کاربر را بفرستید:", chat_id, msg_id)
            bot.register_next_step_handler(call.message, set_coin_user)
        elif call.data == "ban_user":
            bot.edit_message_text("🚫 نام کاربر برای بن:", chat_id, msg_id)
            bot.register_next_step_handler(call.message, ban_user)
        elif call.data == "unban_user":
            bot.edit_message_text("✅ نام کاربر برای حذف بن:", chat_id, msg_id)
            bot.register_next_step_handler(call.message, unban_user)
        elif call.data == "off_bot":
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("✅ بله", callback_data="confirm_off"),
                types.InlineKeyboardButton("❌ خیر", callback_data="cancel_off")
            )
            bot.edit_message_text("⚠️ مطمئنید می‌خواهید ربات را خاموش کنید؟", chat_id, msg_id, reply_markup=markup)
        elif call.data == "confirm_off":
            data["bot_on"] = False
            save_data()
            bot.edit_message_text("🔴 ربات خاموش شد!", chat_id, msg_id)
        elif call.data == "cancel_off":
            bot.edit_message_text("✅ عملیات لغو شد.", chat_id, msg_id)
        elif call.data == "on_bot":
            data["bot_on"] = True
            save_data()
            bot.edit_message_text("🟢 ربات روشن شد و آماده خدمت است!", chat_id, msg_id)

    # ===== کاربران عادی =====
    else:
        if call.data == "info":
            u = data["users"].get(username, {})
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="back_main"))
            bot.edit_message_text(
                f"👤 @{username}\n💰 کوین‌ها: {u.get('coins',0)}\n📅 عضویت: {u.get('joined','❓')}",
                chat_id, msg_id, reply_markup=markup
            )
        elif call.data == "dice":
            bot.edit_message_text("🎲 مقدار کوینی که می‌خواهید شرط ببندید را بفرستید:", chat_id, msg_id)
            bot.register_next_step_handler(call.message, dice_bet)
        elif call.data == "back_main":
            start(call.message)

# ====== توابع مالک ======
def give_coin_user(msg):
    usern = msg.text.replace("@", "")
    if usern not in data["users"]:
        bot.send_message(msg.chat.id, "❌ کاربر یافت نشد.")
        return
    bot.send_message(msg.chat.id, "💰 تعداد کوینی که می‌خواهید بدهید را وارد کنید:")
    bot.register_next_step_handler(msg, lambda m: give_coin_amount(m, usern))

def give_coin_amount(msg, usern):
    try:
        amount = int(msg.text)
        data["users"][usern]["coins"] += amount
        save_data()
        bot.send_message(msg.chat.id, f"✅ {amount} کوین به @{usern} اضافه شد.")
    except:
        bot.send_message(msg.chat.id, "❌ مقدار نامعتبر است.")

# ====== بازی تاس ======
def dice_bet(msg):
    usern = msg.from_user.username
    try:
        amount = int(msg.text)
    except:
        bot.send_message(msg.chat.id, "⚠️ فقط عدد ارسال کنید!")
        return

    if amount > data["users"][usern]["coins"]:
        bot.send_message(msg.chat.id, "❌ موجودی کافی نیست!")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🔵 زوج", callback_data=f"dice_even_{amount}"),
        types.InlineKeyboardButton("🔴 فرد", callback_data=f"dice_odd_{amount}")
    )
    bot.send_message(msg.chat.id, "🎯 انتخاب کنید:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("dice_"))
def dice_result(call):
    username = call.from_user.username
    amount = int(call.data.split("_")[-1])
    choice = "even" if "even" in call.data else "odd"
    roll = random.randint(1, 6)
    win = (roll % 2 == 0 and choice == "even") or (roll % 2 == 1 and choice == "odd")
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if win:
        data["users"][username]["coins"] += amount
        bot.edit_message_text(f"🎲 عدد {roll} آمد!\n✨ بردی! {amount} کوین به حساب‌ت اضافه شد.", chat_id, msg_id)
    else:
        data["users"][username]["coins"] -= amount
        bot.edit_message_text(f"🎲 عدد {roll} آمد!\n😢 باختی! {amount} کوین ازت کم شد.", chat_id, msg_id)
    save_data()

# ====== اجرای ربات ======
print("🤖 Bot is running...")
bot.infinity_polling()
