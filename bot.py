import os
import telebot
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json
import time
import re
from datetime import datetime

TOKEN = "8904331723:AAFu0cLXdzyCa_kOyzG_8niUqPcLfPLAGEY"
LAVA_WALLET = "R11602732"
CRYPTO_WALLET = "UQCxVBC_Sj5WQ6wUIB1TFFXiOMHRNKx6mFkDUKIVSOWZ0I00"
MIN_DEPOSIT = 25

bot = telebot.TeleBot(TOKEN)
users = {}
user_steps = {}

# Веб-сервер для Render
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

# Сохранение пользователя
def save_user(chat_id, username):
    if chat_id not in users:
        users[chat_id] = {
            "reg_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "balance": 0,
            "total_deposit": 0,
            "stars_bought": 0,
            "username": username
        }

# Клавиатуры
def get_main_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🌟 Купить звёзды")
    keyboard.row("👤 Профиль", "🆔 Мой ID")
    return keyboard

def get_stars_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("⭐ 15 шт - 20 ₽")
    keyboard.row("⭐ 25 шт - 48 ₽")
    keyboard.row("⭐ 50 шт - 65 ₽")
    keyboard.row("⭐ 100 шт - 126 ₽")
    keyboard.row("◀️ Назад")
    return keyboard

def get_payment_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🏦 СБП (Lava)", "💎 Криптовалюта (USDT)")
    keyboard.row("◀️ Назад")
    return keyboard

def get_back_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("◀️ Назад")
    return keyboard

def get_profile_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("💰 Пополнить баланс")
    keyboard.row("◀️ Назад")
    return keyboard

def format_profile(chat_id):
    u = users.get(chat_id, {})
    return (f"👤 <b>Профиль</b>\n\n"
            f"🆔 ID: {chat_id}\n"
            f"📛 Username: @{u.get('username', 'нет')}\n"
            f"💰 <b>Баланс: {u.get('balance', 0)} ₽</b>\n"
            f"📈 Всего пополнено: {u.get('total_deposit', 0)} ₽\n"
            f"⭐ Куплено звёзд: {u.get('stars_bought', 0)} шт\n\n"
            f"📅 Регистрация: {u.get('reg_date', 'неизвестно')}")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    username = message.from_user.username or "user"
    save_user(chat_id, username)
    bot.send_message(chat_id, f"🌟 Добро пожаловать!\n🆔 Ваш ID: {chat_id}", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "🆔 Мой ID")
def my_id(message):
    bot.send_message(message.chat.id, f"🆔 Ваш ID: {message.chat.id}")

@bot.message_handler(func=lambda m: m.text == "👤 Профиль")
def profile(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, format_profile(chat_id), reply_markup=get_profile_keyboard(), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "💰 Пополнить баланс")
def deposit(message):
    chat_id = message.chat.id
    user_steps[chat_id] = {"step": "entering_amount"}
    bot.send_message(chat_id, f"💵 Введите сумму пополнения (мин. {MIN_DEPOSIT} ₽):", reply_markup=get_back_keyboard())

@bot.message_handler(func=lambda m: m.text == "🌟 Купить звёзды")
def buy_stars(message):
    bot.send_message(message.chat.id, "⭐ Выберите количество звёзд:", reply_markup=get_stars_keyboard())

@bot.message_handler(func=lambda m: m.text and "⭐" in m.text and "шт" in m.text)
def choose_stars(message):
    chat_id = message.chat.id
    parts = message.text.split("-")
    stars = int(parts[0].replace("⭐", "").replace("шт", "").strip())
    price = int(parts[1].replace("₽", "").strip())
    user_steps[chat_id] = {"step": "buying_stars", "stars": stars, "price": price}
    bot.send_message(chat_id, f"⭐ {stars} звёзд = {price} ₽\nВыберите способ оплаты:", reply_markup=get_payment_keyboard())

@bot.message_handler(func=lambda m: m.text == "🏦 СБП (Lava)")
def pay_sbp(message):
    chat_id = message.chat.id
    if chat_id in user_steps and user_steps[chat_id].get("step") == "buying_stars":
        price = user_steps[chat_id]["price"]
        bot.send_message(chat_id, f"💳 Оплатите {price} ₽ по СБП:\n<b>Lava кошелёк:</b> {LAVA_WALLET}\n\n✅ После оплаты отправьте ЛЮБОЕ ФОТО", reply_markup=get_back_keyboard(), parse_mode="HTML")
        user_steps[chat_id]["step"] = "waiting_stars_payment"

@bot.message_handler(func=lambda m: m.text == "💎 Криптовалюта (USDT)")
def pay_crypto(message):
    chat_id = message.chat.id
    if chat_id in user_steps and user_steps[chat_id].get("step") == "buying_stars":
        price = user_steps[chat_id]["price"]
        bot.send_message(chat_id, f"💎 Оплатите {price} ₽ (≈{price/90:.2f} USDT):\n<b>Кошелёк:</b> <code>{CRYPTO_WALLET}</code>\n\n✅ После оплаты отправьте ЛЮБОЕ ФОТО", reply_markup=get_back_keyboard(), parse_mode="HTML")
        user_steps[chat_id]["step"] = "waiting_stars_payment"

@bot.message_handler(func=lambda m: m.text == "◀️ Назад")
def back(message):
    chat_id = message.chat.id
    if chat_id in user_steps:
        del user_steps[chat_id]
    bot.send_message(chat_id, "Главное меню:", reply_markup=get_main_keyboard())

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    if chat_id in user_steps:
        step = user_steps[chat_id].get("step")
        
        if step == "waiting_screenshot":
            amount = user_steps[chat_id].get("amount", 0)
            users[chat_id]["balance"] += amount
            users[chat_id]["total_deposit"] += amount
            bot.send_message(chat_id, f"✅ Баланс пополнен на {amount} ₽!\n💰 Новый баланс: {users[chat_id]['balance']} ₽", reply_markup=get_profile_keyboard())
            del user_steps[chat_id]
        
        elif step == "waiting_stars_payment":
            stars = user_steps[chat_id].get("stars", 0)
            users[chat_id]["stars_bought"] += stars
            bot.send_message(chat_id, f"✅ Оплачено! ⭐ {stars} звёзд начислено.\nСпасибо за покупку!", reply_markup=get_main_keyboard())
            del user_steps[chat_id]
    else:
        bot.send_message(chat_id, "❓ Сначала выберите действие в меню", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: True)
def unknown(message):
    bot.send_message(message.chat.id, "❓ Используйте кнопки меню", reply_markup=get_main_keyboard())

print("✅ Бот запущен")
bot.infinity_polling()
