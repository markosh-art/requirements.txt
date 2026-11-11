import os
import telebot

# Токен, который дал BotFather (лучше вставлять напрямую или через переменные окружения)
TOKEN = "ЗДЕСЬ_ВСТАВЬТЕ_ВАШ_ТОКЕН_ОТ_BOTFATHER"

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