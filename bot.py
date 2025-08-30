import telebot
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace with your BotFather token
BOT_TOKEN = "8498118490:AAGlTd-UjCMlTVohBAQs7YQGC1Hz357GosY"
ADMIN_USERNAME = "@ahmedomarahmedom"
ADMIN_CHAT_ID = YOUR_TELEGRAM_CHAT_ID   # <-- Replace with your Telegram ID

bot = telebot.TeleBot(BOT_TOKEN)

# Task links by country
TASKS = {
    "Pakistan": [
        "https://singingfiles.com/show.php?l=0&u=2207781&id=59477",
        "https://singingfiles.com/show.php?l=0&u=2207781&id=59478"
    ],
    "US": [
        "https://singingfiles.com/show.php?l=0&u=2207781&id=71677",
        "https://singingfiles.com/show.php?l=0&u=2207781&id=66965",
        "https://singingfiles.com/show.php?l=0&u=2207781&id=67265"
    ]
}

# Store user balances in memory (for testing)
# You can replace with database (SQLite/JSON) for persistence
balances = {}

# Ask user for country
@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.chat.id
    if user_id not in balances:
        balances[user_id] = 0.0  # initialize balance

    text = (
        "💸 *Earn Money with MoneyGrip Bot* 💸\n\n"
        "👉 Complete simple tasks and earn real money.\n"
        "👉 Payments available via *PayPal* & *Easypaisa*.\n"
        f"👉 After completing tasks, contact admin: {ADMIN_USERNAME}\n\n"
        "📋 Select your country to see tasks:"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🇵🇰 Pakistan", callback_data="country_Pakistan"))
    markup.add(InlineKeyboardButton("🇺🇸 US", callback_data="country_US"))
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# Handle country selection
@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def show_task(call):
    country = call.data.split("_")[1]
    if country in TASKS:
        link = random.choice(TASKS[country])  # pick random link
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 Open Task ($0.01)", url=link))
        markup.add(InlineKeyboardButton("✅ I’ve Completed Task", callback_data=f"done_{country}"))
        bot.send_message(
            call.message.chat.id,
            f"✅ Task for *{country}*:\n\nComplete this task and earn *$0.01* 💵\n\n"
            f"After completion, contact admin: {ADMIN_USERNAME}",
            parse_mode="Markdown",
            reply_markup=markup
        )

# Handle task completion
@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def task_done(call):
    country = call.data.split("_")[1]
    user = call.from_user
    user_id = call.message.chat.id

    # Add $0.01 to balance
    if user_id not in balances:
        balances[user_id] = 0.0
    balances[user_id] += 0.01

    # Confirm to user
    bot.send_message(
        call.message.chat.id,
        f"🎉 Task submitted! Your balance is now *${balances[user_id]:.2f}* 💰\n\n"
        f"📩 Please wait for admin {ADMIN_USERNAME} to verify and send payment.",
        parse_mode="Markdown"
    )

    # Notify Admin
    bot.send_message(
        ADMIN_CHAT_ID,
        f"🔔 *Task Completion Notification*\n\n"
        f"👤 User: {user.first_name} (@{user.username})\n"
        f"🆔 User ID: {user.id}\n"
        f"🌍 Country: {country}\n"
        f"💰 Balance: ${balances[user_id]:.2f}\n"
        f"✅ Reported task completed.",
        parse_mode="Markdown"
    )

# Check balance
@bot.message_handler(commands=["balance"])
def check_balance(message):
    user_id = message.chat.id
    balance = balances.get(user_id, 0.0)
    bot.send_message(
        message.chat.id,
        f"💼 Your current balance: *${balance:.2f}*",
        parse_mode="Markdown"
    )

# Withdraw info
@bot.message_handler(commands=["withdraw"])
def withdraw_info(message):
    user_id = message.chat.id
    balance = balances.get(user_id, 0.0)
    text = (
        "💳 *Withdraw Instructions*\n\n"
        f"💼 Your current balance: *${balance:.2f}*\n\n"
        "➡️ Complete tasks to increase your balance ($0.01 per task).\n"
        f"➡️ After completion, contact admin: {ADMIN_USERNAME}\n"
        "➡️ Payment methods: PayPal / Easypaisa.\n\n"
        "⚠️ Payment is sent manually after verification."
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# Default handler
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    bot.send_message(
        message.chat.id,
        "💡 Use /start to begin earning tasks.\n💰 Use /balance to check balance.\n💳 Use /withdraw for payment instructions."
    )

print("🤖 Bot is running...")
bot.infinity_polling()
