import os
import telebot


from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Мини-сервер для обмана Render, чтобы он не ругался на закрытые порты
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Запускаем сервер в фоновом потоке, чтобы он не мешал работе бота
threading.Thread(target=run_server, daemon=True).start()




# Токен, который дал BotFather (лучше вставлять напрямую или через переменные окружения)
TOKEN = "9173918908:AAH5X-3SGNcu-79pmzXNbJ1lqEk4T6H35KQ"

bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот ArmCyber. Чем я могу помочь?")

# Обработчик обычных текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Вы написали: {message.text}")

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
