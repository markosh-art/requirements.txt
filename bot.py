import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import telebot
from telebot import types
import json
from datetime import datetime

# ==================== МИНИ-СЕРВЕР ДЛЯ RENDER ====================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
# ===============================================================

# ТОКЕН БОТА (можно заменить или оставить здесь)
TOKEN = "9173918908:AAH5X-3SGNcu-79pmzXNbJ1lqEk4T6H35KQ"
bot = telebot.TeleBot(TOKEN)

# Временное хранилище шагов пользователя для корзины в боте
user_cart = {}

# Список категорий и товаров (точь-в-точь как на сайте)
CATEGORIES_DATA = {
    "pc": {
        "title": "🖥 Рабочие станции",
        "items": [
            {"id": "pc_1", "title": "PC Level 1 Workstation", "price": 2000, "unit": "час"},
            {"id": "pc_2", "title": "PC Level 2 Pro", "price": 5000, "unit": "час"},
            {"id": "pc_3", "title": "PC Level 3 Extreme", "price": 9000, "unit": "час"}
        ]
    },
    "srv": {
        "title": "⚙️ Серверные системы",
        "items": [
            {"id": "srv_1", "title": "Server Starter Node", "price": 15000, "unit": "сутки"},
            {"id": "srv_2", "title": "Server Pro Infrastructure", "price": 35000, "unit": "сутки"},
            {"id": "srv_3", "title": "Server Enterprise Cluster", "price": 80000, "unit": "сутки"}
        ]
    },
    "net": {
        "title": "🌐 Сетевое оборудование",
        "items": [
            {"id": "net_1", "title": "Cyber Shield Gateway", "price": 12000, "unit": "шт"},
            {"id": "net_2", "title": "Managed Switch 48p", "price": 8000, "unit": "шт"},
            {"id": "net_3", "title": "Enterprise Wi-Fi 7 AP", "price": 6000, "unit": "шт"}
        ]
    }
}

# Функция сохранения заказа в файл-мост (или симуляцию базы для сайта)
def save_tg_order_to_storage(order_data):
    filename = "shared_orders.json"
    orders = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                orders = json.load(f)
        except:
            orders = []
    
    orders.insert(0, order_data)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_cart[user_id] = {} # сбрасываем корзину при старте
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn_rent = types.KeyboardButton("🚀 Аренда оборудования")
    btn_orders = types.KeyboardButton("📦 Список покупок (Админ)")
    btn_support = types.KeyboardButton("🛠 Поддержка")
    markup.add(btn_rent, btn_orders, btn_support)
    
    bot.send_message(
        message.chat.id, 
        "<b>CYBER ARENA — ArmCyber Security Solutions</b>\n\n"
        "Добро пожаловать в официальный бот управления инфраструктурой! Выберите нужный раздел в меню ниже:",
        parse_mode="HTML",
        reply_markup=markup
    )

# Обработка текстовых кнопок главного меню
@bot.message_handler(func=lambda message: True)
def handle_main_menu(message):
    text = message.text
    user_id = message.from_user.id

    if text == "🚀 Аренда оборудования":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for cat_key, cat_val in CATEGORIES_DATA.items():
            markup.add(types.InlineKeyboardButton(cat_val["title"], callback_data=f"cat_{cat_key}"))
        
        bot.send_message(message.chat.id, "Выберите категорию оборудования для конфигурации:", reply_markup=markup)

    elif text == "🛠 Поддержка":
        bot.send_message(
            message.chat.id, 
            "По всем вопросам обращайтесь к нашему специалисту поддержки:\n👉 <b>@markosh_art</b> (напишите ему напрямую)",
            parse_mode="HTML"
        )

    elif text == "📦 Список покупок (Админ)":
        msg = bot.send_message(message.chat.id, "Введите пароль доступа к терминалу (админ-панели):")
        bot.register_next_step_handler(msg, check_admin_password)

# Проверка пароля админа в боте (qwerty)
def check_admin_password(message):
    if message.text == "qwerty":
        filename = "shared_orders.json"
        if not os.path.exists(filename):
            bot.send_message(message.chat.id, "📭 В базе пока нет оформленных заказов.")
            return
        
        try:
            with open(filename, "r", encoding="utf-8") as f:
                orders = json.load(f)
            
            if not orders:
                bot.send_message(message.chat.id, "📭 Список покупок пуст.")
                return

            response_text = "<b>📋 ЖУРНАЛ ЗАКАЗОВ (ТЕРМИНАЛ):</b>\n\n"
            total_sum = 0
            for ord in orders:
                total_sum += ord.get("totalAmountAMD", 0)
                response_text += f"🆔 <b>{ord.get('orderId')}</b> | {ord.get('timestamp')}\n"
                response_text += f"👤 Клиент: <code>{ord.get('clientId')}</code>\n"
                response_text += f"🌐 Источник: {ord.get('clientEmail')}\n"
                response_text += "📦 Состав заказа:\n"
                for item in ord.get("items", []):
                    response_text += f"   • {item['title']} x{item['quantity']} — {item['subtotal']:,} AMD\n"
                response_text += f"💰 Итого: <b>{ord.get('totalAmountAMD'):,} AMD</b>\n"
                response_text += "-----------------------------------\n"
            
            response_text += f"\n💎 <b>Общая сумма всех заказов: {total_sum:,} AMD</b>"
            bot.send_message(message.chat.id, response_text, parse_mode="HTML")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка чтения базы: {e}")
    else:
        bot.send_message(message.chat.id, "❌ Неверный пароль! Доступ запрещен.")

# Обработка Inline-кнопок каталога и корзины
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.from_user.id
    if user_id not in user_cart:
        user_cart[user_id] = {}

    data = call.data

    if data.startswith("cat_"):
        cat_key = data.split("_")[1]
        cat_data = CATEGORIES_DATA[cat_key]
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for item in cat_data["items"]:
            current_qty = user_cart[user_id].get(item["id"], 0)
            markup.add(types.InlineKeyboardButton(
                f"{item['title']} ({item['price']:,} AMD/{item['unit']}) [В корзине: {current_qty}]", 
                callback_data=f"item_{item['id']}"
            ))
        markup.add(types.InlineKeyboardButton("⬅️ Назад к категориям", callback_data="back_to_cats"))
        markup.add(types.InlineKeyboardButton("🛒 Оформить заказ", callback_data="checkout_cart"))
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"<b>{cat_data['title']}</b>\nВыберите позицию для добавления в спецификацию:", parse_mode="HTML", reply_markup=markup)

    elif data == "back_to_cats":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for cat_key, cat_val in CATEGORIES_DATA.items():
            markup.add(types.InlineKeyboardButton(cat_val["title"], callback_data=f"cat_{cat_key}"))
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите категорию оборудования для конфигурации:", reply_markup=markup)

    elif data.startswith("item_"):
        item_id = data.replace("item_", "")
        # Увеличиваем количество на 1 при клике
        current = user_cart[user_id].get(item_id, 0)
        user_cart[user_id][item_id] = current + 1
        
        # Находим категорию товара, чтобы вернуть пользователя в то же меню
        found_cat = "pc"
        for c_key, c_val in CATEGORIES_DATA.items():
            if any(i["id"] == item_id for i in c_val["items"]):
                found_cat = c_key
                break
        
        # Перерисовываем меню категории с обновленным количеством
        cat_data = CATEGORIES_DATA[found_cat]
        markup = types.InlineKeyboardMarkup(row_width=1)
        for item in cat_data["items"]:
            current_qty = user_cart[user_id].get(item["id"], 0)
            markup.add(types.InlineKeyboardButton(
                f"{item['title']} ({item['price']:,} AMD/{item['unit']}) [В корзине: {current_qty}]", 
                callback_data=f"item_{item['id']}"
            ))
        markup.add(types.InlineKeyboardButton("⬅️ Назад к категориям", callback_data="back_to_cats"))
        markup.add(types.InlineKeyboardButton("🛒 Оформить заказ", callback_data="checkout_cart"))
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ Позиция добавлена!\n<b>{cat_data['title']}</b>\nВыберите еще или перейдите к оформлению:", parse_mode="HTML", reply_markup=markup)

    elif data == "checkout_cart":
        cart = user_cart.get(user_id, {})
        if not cart or all(qty == 0 for qty in cart.values()):
            bot.answer_callback_query(call.id, "Ваша корзина пуста!", show_alert=True)
            return
        
        # Собираем итоговый заказ
        selected_items = []
        grand_total = 0
        
        for c_key, c_val in CATEGORIES_DATA.items():
            for item in c_val["items"]:
                qty = cart.get(item["id"], 0)
                if qty > 0:
                    subtotal = qty * item["price"]
                    grand_total += subtotal
                    selected_items.append({
                        "id": item["id"],
                        "title": item["title"],
                        "category": c_val["title"],
                        "quantity": qty,
                        "unitPrice": item["price"],
                        "subtotal": subtotal
                    })
        
        username = f"@{call.from_user.username}" if call.from_user.username else f"id{call.from_user.id}"
        full_name = f"{call.from_user.first_name or ''} {call.from_user.last_name or ''}".strip()
        
        order_payload = {
            "orderId": "TG-" + datetime.now().strftime("%H%M%S"),
            "clientId": f"{full_name} ({username})",
            "clientEmail": "📱 Telegram Client",
            "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "items": selected_items,
            "totalAmountAMD": grand_total,
            "status": "PAID_CONFIRMED"
        }
        
        # Сохраняем в общий файл заказов
        save_tg_order_to_storage(order_payload)
        
        # Очищаем корзину пользователя
        user_cart[user_id] = {}
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🎉 <b>Заказ успешно оформлен и передан в систему!</b>\n\n"
                 f"🆔 Номер: <code>{order_payload['orderId']}</code>\n"
                 f"💰 Сумма: <b>{grand_total:,} AMD</b>\n\n"
                 f"Администратор уже видит ваш заказ в терминале под вашим Telegram-аккаунтом ({username}). Спасибо!",
            parse_mode="HTML"
        )

print("Telegram Bot started successfully...")
bot.infinity_polling()
