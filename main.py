from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import random

# 🧠 تنظیمات اصلی
TOKEN = "8246648556:AAG6yvrLYsQN-GlgdrPBgBWmNmKfNE4bgWo"
OWNER_ID = 7776714237  # آیدی عددی مالک

# 🎲 تابع استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.first_name

    keyboard = []

    if user_id == OWNER_ID:
        keyboard = [
            [InlineKeyboardButton("🧠 پنل مدیریت", callback_data="admin_panel")],
            [InlineKeyboardButton("🎲 تاس انداختن", callback_data="dice")],
        ]
        text = f"👑 خوش آمدی {name} عزیز!\n\nتو مالک ربات هستی."
    else:
        keyboard = [[InlineKeyboardButton("🎲 تاس انداختن", callback_data="dice")]]
        text = f"سلام {name} 🌸\nبه ربات بازی تاس خوش اومدی!"

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

# 🧭 پنل مدیریت
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.delete()

    keyboard = [
        [InlineKeyboardButton("💰 دادن کوین", callback_data="give_coin")],
        [InlineKeyboardButton("💸 گرفتن کوین", callback_data="take_coin")],
        [InlineKeyboardButton("⚙️ تنظیم کوین", callback_data="set_coin")],
        [InlineKeyboardButton("🔒 بن کردن کاربر", callback_data="ban_user")],
        [InlineKeyboardButton("❌ خاموش کردن ربات", callback_data="shutdown_confirm")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("🧠 پنل مدیریت فعال شد:", reply_markup=reply_markup)

# 🔒 تأیید خاموش کردن ربات
async def shutdown_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.delete()

    keyboard = [
        [InlineKeyboardButton("✅ بله", callback_data="shutdown_yes"),
         InlineKeyboardButton("❌ خیر", callback_data="admin_panel")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="admin_panel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("⚠️ آیا مطمئنی می‌خوای ربات خاموش بشه؟", reply_markup=reply_markup)

# ✅ اجرای خاموشی
async def shutdown_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.delete()
    await query.message.reply_text("💤 ربات خاموش شد! (البته به‌صورت نمایشی 😄)")

# 🎲 بخش تاس انداختن
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.delete()

    keyboard = [
        [InlineKeyboardButton("⚪ زوج", callback_data="even"),
         InlineKeyboardButton("🔵 فرد", callback_data="odd")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("🎲 حدس بزن عدد تاس زوج باشه یا فرد؟", reply_markup=reply_markup)

# 🎯 نتیجه تاس
async def dice_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    choice = query.data
    await query.message.delete()

    dice_number = random.randint(1, 6)
    parity = "even" if dice_number % 2 == 0 else "odd"

    if choice == parity:
        result_text = f"🎉 عدد تاس: {dice_number}\nتبریک! حدست درست بود 😎"
    else:
        result_text = f"🎲 عدد تاس: {dice_number}\nاشتباه حدس زدی 😅"

    keyboard = [[InlineKeyboardButton("🎲 دوباره!", callback_data="dice")],
                [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(result_text, reply_markup=reply_markup)

# 🔙 برگشت به منوی اصلی
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.delete()

    user_id = query.from_user.id
    keyboard = []

    if user_id == OWNER_ID:
        keyboard = [
            [InlineKeyboardButton("🧠 پنل مدیریت", callback_data="admin_panel")],
            [InlineKeyboardButton("🎲 تاس انداختن", callback_data="dice")],
        ]
        text = "🏠 بازگشت به منوی اصلی مالک:"
    else:
        keyboard = [[InlineKeyboardButton("🎲 تاس انداختن", callback_data="dice")]]
        text = "🏠 بازگشت به منوی اصلی:"

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(text, reply_markup=reply_markup)

# 🚀 اجرای برنامه
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
app.add_handler(CallbackQueryHandler(shutdown_confirm, pattern="^shutdown_confirm$"))
app.add_handler(CallbackQueryHandler(shutdown_yes, pattern="^shutdown_yes$"))
app.add_handler(CallbackQueryHandler(dice, pattern="^dice$"))
app.add_handler(CallbackQueryHandler(dice_result, pattern="^(even|odd)$"))
app.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"))

print("🤖 Bot is running...")
app.run_polling()
