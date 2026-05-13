import os
import telebot
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

TOKEN = "8904331723:AAFu0cLXdzyCa_kOyzG_8niUqPcLfPLAGEY"
bot = telebot.TeleBot(TOKEN)

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

# Обработчики команд
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"✅ Бот работает!\nТвой ID: {message.chat.id}")

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.send_message(message.chat.id, f"Твой ID: {message.chat.id}")

print("Бот запущен")
bot.infinity_polling()
