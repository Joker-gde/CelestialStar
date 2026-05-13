import urllib.request
import json
import time
import re
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = "8904331723:AAFu0cLXdzyCa_kOyzG_8niUqPcLfPLAGEY"
last_id = 0

# ========== НАСТРОЙКИ ==========
CRYPTO_WALLET = "UQCxVBC_Sj5WQ6wUIB1TFFXiOMHRNKx6mFkDUKIVSOWZ0I00"
LAVA_WALLET = "R11602732"
MIN_DEPOSIT = 25

users = {}
user_steps = {}

print("✅ Бот запущен")

# ========== ВЕБ-СЕРВЕР ДЛЯ RENDER ==========
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

# Запускаем веб-сервер в отдельном потоке
import os
threading.Thread(target=run_web_server, daemon=True).start()

# ========== ОСТАЛЬНОЙ КОД БОТА ==========
def save_user(chat_id, username):
    if chat_id not in users:
        users[chat_id] = {
            "reg_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "balance": 0,
            "total_deposit": 0,
            "stars_bought": 0,
            "username": username
        }

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        req = urllib.request.Request(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Ошибка: {e}")

def get_main_keyboard():
    return {
        "keyboard": [
            [{"text": "🌟 Купить звёзды"}],
            [{"text": "👤 Профиль"}],
            [{"text": "🆔 Мой ID"}]
        ],
        "resize_keyboard": True
    }

def get_stars_keyboard():
    return {
        "keyboard": [
            [{"text": "⭐ 15 шт - 20 ₽"}],
            [{"text": "⭐ 25 шт - 48 ₽"}],
            [{"text": "⭐ 50 шт - 65 ₽"}],
            [{"text": "⭐ 100 шт - 126 ₽"}],
            [{"text": "◀️ Назад"}]
        ],
        "resize_keyboard": True
    }

def get_payment_methods_keyboard():
    return {
        "keyboard": [
            [{"text": "🏦 СБП (Lava)"}],
            [{"text": "💎 Криптовалюта (USDT)"}],
            [{"text": "◀️ Назад"}]
        ],
        "resize_keyboard": True
    }

def get_profile_keyboard():
    return {
        "keyboard": [
            [{"text": "💰 Пополнить баланс"}],
            [{"text": "◀️ Назад"}]
        ],
        "resize_keyboard": True
    }

def get_back_keyboard():
    return {"keyboard": [[{"text": "◀️ Назад"}]], "resize_keyboard": True}

def format_profile(chat_id):
    u = users.get(chat_id, {})
    return (f"👤 <b>Профиль</b>\n\n"
            f"🆔 ID: {chat_id}\n"
            f"📛 Username: @{u.get('username', 'нет')}\n"
            f"💰 <b>Баланс: {u.get('balance', 0)} ₽</b>\n"
            f"📈 Всего пополнено: {u.get('total_deposit', 0)} ₽\n"
            f"⭐ Куплено звёзд: {u.get('stars_bought', 0)} шт\n\n"
            f"📅 Регистрация: {u.get('reg_date', 'неизвестно')}")

while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id+1}"
        response = urllib.request.urlopen(url).read()
        data = json.loads(response)
        
        if "result" in data:
            for update in data["result"]:
                last_id = update["update_id"]
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    username = msg.get("from", {}).get("username", "user")
                    if chat_id not in users:
                        save_user(chat_id, username)
                    
                    if text == "◀️ Назад" and chat_id in user_steps:
                        send_message(chat_id, "Главное меню:", get_main_keyboard())
                        del user_steps[chat_id]
                        continue
                    
                    if chat_id in user_steps:
                        step = user_steps[chat_id].get("step")
                        
                        if step == "entering_amount":
                            try:
                                amount = int(text)
                                if amount < MIN_DEPOSIT:
                                    send_message(chat_id, f"❌ Минимальная сумма {MIN_DEPOSIT} ₽", get_back_keyboard())
                                    continue
                                user_steps[chat_id]["amount"] = amount
                                send_message(chat_id, f"💰 Сумма: {amount} ₽\nВыберите способ оплаты:", get_payment_methods_keyboard())
                                user_steps[chat_id]["step"] = "choosing_payment"
                            except:
                                send_message(chat_id, "❌ Введите ЧИСЛО (сумму в рублях):", get_back_keyboard())
                            continue
                        
                        if step == "choosing_payment":
                            amount = user_steps[chat_id].get("amount")
                            if text == "🏦 СБП (Lava)":
                                send_message(chat_id, f"💳 Оплатите по СБП:\n<b>Lava кошелёк:</b> {LAVA_WALLET}\n<b>Сумма:</b> {amount} ₽\n\n📸 После оплаты отправьте СКРИН чека", get_back_keyboard())
                                user_steps[chat_id]["step"] = "waiting_screenshot"
                            elif text == "💎 Криптовалюта (USDT)":
                                send_message(chat_id, f"💎 Оплатите USDT:\n<b>Кошелёк:</b> <code>{CRYPTO_WALLET}</code>\n<b>Сумма:</b> ≈{amount/90:.2f} USDT\n\n📸 После оплаты отправьте СКРИН", get_back_keyboard())
                                user_steps[chat_id]["step"] = "waiting_screenshot"
                            elif text == "◀️ Назад":
                                send_message(chat_id, format_profile(chat_id), get_profile_keyboard())
                                del user_steps[chat_id]
                            else:
                                send_message(chat_id, "Выберите способ оплаты:", get_payment_methods_keyboard())
                            continue
                        
                        if step == "waiting_screenshot" and msg.get("photo"):
                            amount = user_steps[chat_id].get("amount", 0)
                            users[chat_id]["balance"] += amount
                            users[chat_id]["total_deposit"] += amount
                            send_message(chat_id, f"✅ Баланс пополнен на {amount} ₽!\n💰 Новый баланс: {users[chat_id]['balance']} ₽", get_profile_keyboard())
                            del user_steps[chat_id]
                            continue
                    
                    if msg.get("photo"):
                        send_message(chat_id, "❓ Сначала выберите действие", get_main_keyboard())
                        continue
                    
                    if text == "/start":
                        send_message(chat_id, f"🌟 Добро пожаловать!\n🆔 Ваш ID: {chat_id}", get_main_keyboard())
                    elif text == "🆔 Мой ID":
                        send_message(chat_id, f"🆔 Ваш ID: {chat_id}\n🤖 ID бота: {TOKEN.split(':')[0]}", get_main_keyboard())
                    elif text == "👤 Профиль":
                        send_message(chat_id, format_profile(chat_id), get_profile_keyboard())
                        elif text == "💰 Пополнить баланс":
                        send_message(chat_id, f"💵 Введите сумму пополнения (мин. {MIN_DEPOSIT} ₽):", get_back_keyboard())
                        user_steps[chat_id] = {"step": "entering_amount"}
                    elif text == "🌟 Купить звёзды":
                        send_message(chat_id, "⭐ Выберите количество звёзд:", get_stars_keyboard())
                    elif "⭐" in text and "шт" in text and "₽" in text:
                        parts = text.split("-")
                        stars = int(parts[0].replace("⭐", "").replace("шт", "").strip())
                        price = int(parts[1].replace("₽", "").strip())
                        user_steps[chat_id] = {"step": "buying_stars", "stars": stars, "price": price}
                        send_message(chat_id, f"⭐ {stars} звёзд = {price} ₽\nВыберите способ оплаты:", get_payment_methods_keyboard())
                    elif text == "🏦 СБП (Lava)" and user_steps.get(chat_id, {}).get("step") == "buying_stars":
                        stars = user_steps[chat_id]["stars"]
                        price = user_steps[chat_id]["price"]
                        send_message(chat_id, f"💳 Оплатите {price} ₽ по СБП:\n<b>Lava кошелёк:</b> {LAVA_WALLET}\n\n✅ После оплаты отправьте СКРИН", get_back_keyboard())
                        user_steps[chat_id]["step"] = "waiting_stars_payment"
                    elif text == "💎 Криптовалюта (USDT)" and user_steps.get(chat_id, {}).get("step") == "buying_stars":
                        stars = user_steps[chat_id]["stars"]
                        price = user_steps[chat_id]["price"]
                        send_message(chat_id, f"💎 Оплатите {price} ₽ (≈{price/90:.2f} USDT):\n<b>Кошелёк:</b> <code>{CRYPTO_WALLET}</code>\n\n✅ После оплаты отправьте СКРИН", get_back_keyboard())
                        user_steps[chat_id]["step"] = "waiting_stars_payment"
                    elif "waiting_stars_payment" in str(user_steps.get(chat_id, {})) and msg.get("photo"):
                        stars = user_steps[chat_id]["stars"]
                        users[chat_id]["stars_bought"] += stars
                        send_message(chat_id, f"✅ Оплачено! ⭐ {stars} звёзд начислено.\nСпасибо за покупку!", get_main_keyboard())
                        del user_steps[chat_id]
                    else:
                        send_message(chat_id, "❓ Используйте кнопки меню", get_main_keyboard())
        
        time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(3)
                        
