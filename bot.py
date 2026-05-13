import os
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = "8904331723:AAFu0cLXdzyCa_kOyzG_8niUqPcLfPLAGEY"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

import threading
threading.Thread(target=run_web_server, daemon=True).start()

import requests
import time
last_id = 0

print("Бот запущен")

while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id+1}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "result" in data:
            for update in data["result"]:
                last_id = update["update_id"]
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    
                    if text == "/start":
                        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        send_data = {"chat_id": chat_id, "text": "✅ Бот работает!"}
                        requests.post(send_url, json=send_data)
        time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(3)
