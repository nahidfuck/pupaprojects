import threading
import sqlite3
from pupaparser import get_price_pro
import telebot
import time

TOKEN = '8509681388:AAEDku6-Eck0ef9kHLU5fG7pRtW-4oiXBK8'  # Replace with your actual bot token
CHAT_ID = '6377336528'  # Replace with your actual chat ID
bot = telebot.TeleBot(TOKEN)

def init_db():
    conn = sqlite3.connect('tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS olx_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE,
            current_price REAL,
            target_price REAL
        )
    ''')
    conn.commit()
    conn.close()

def add_product():
    url = input("Встав посилання на OLX: ")
    target = float(input("Яку ціну ти хочеш (zł)? "))

    print("⏳ Отримую дані про товар...")
    title, price = get_price_pro(url)
    
    if title and price:
        conn = sqlite3.connect('tracker.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO olx_tracker (title, url, current_price, target_price)
                VALUES (?, ?, ?, ?)
            ''', (title, url, price, target))
            conn.commit()
            print(f"✅ Товар '{title}' додано з поточною ціною {price} zł і цільовою ціною {target} zł.")
        except sqlite3.Error as e: 
            print(f"❌ Помилка при додаванні товару: {e}")
        conn.close()
    else:
        print("❌ Не вдалося отримати дані про товар. Перевірте посилання.")

def send_telegram_alert(message):
    try:
        bot.send_message(CHAT_ID, message)
    except Exception as e:
        print(f"Помилка надсилання в Telegram: {e}")

@bot.message_handler(commands=['list'])
def handle_telegram_list(message):
    conn = sqlite3.connect('tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, url, current_price, target_price FROM olx_tracker')
    products = cursor.fetchall()
    conn.close()

    if products:
        response = "🛒 Список товарів:\n\n"
        for id, title, url, current_price, target_price in products:
            response += f"📦 №{id}. {title}\n💰 Поточна ціна: {current_price} zł\n🎯 Цільова ціна: {target_price} zł\n🔗 {url}\n\n"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "❌ Немає доданих товарів.")

@bot.message_handler(commands=['add'])
def handle_telegram_add(message):
    try:
        parts = message.text.split()
        
        if len(parts) != 3:
            bot.reply_to(message, "❌ Неправильний формат! Пиши так:\n/add [посилання] [цільова_ціна]")
            return

        url = parts[1]
        try:
            target = float(parts[2].replace(',', '.'))
        except ValueError:
            bot.reply_to(message, "❌ Ціна має бути числом!")
            return

        bot.send_message(CHAT_ID, "⏳ Секунду, заходжу на OLX...")

        title, price = get_price_pro(url)

        if title and price:
            conn = sqlite3.connect('tracker.db')
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO olx_tracker (title, url, current_price, target_price)
                    VALUES (?, ?, ?, ?)
                ''', (title, url, price, target))
                conn.commit()
                bot.send_message(CHAT_ID, f"✅ Успішно додано в базу!\n📦 {title}\n💰 Зараз: {price} zł\n🎯 Твоя ціль: {target} zł")
            except sqlite3.Error as e:
                bot.send_message(CHAT_ID, f"❌ Помилка бази даних: {e}")
            finally:
                conn.close()
        else:
            bot.send_message(CHAT_ID, "❌ Не вдалося розпізнати товар за цим посиланням.")

    except Exception as e:
        print(f"Помилка в Telegram-обробнику: {e}")

@bot.message_handler(commands=['remove'])
def handle_telegram_remove(message):
    try:
        parts = message.text.split()
        
        if len(parts) != 2:
            bot.reply_to(message, "❌ Неправильний формат! Пиши так:\n/remove [ID]")
            return

        prod_id = int(parts[1])

        conn = sqlite3.connect('tracker.db')
        cursor = conn.cursor()
        cursor.execute('SELECT title FROM olx_tracker WHERE id = ?', (prod_id,))
        result = cursor.fetchone()

        if result:
            title = result[0]
            cursor.execute('DELETE FROM olx_tracker WHERE id = ?', (prod_id,))
            conn.commit()
            bot.send_message(CHAT_ID, f"✅ Товар '{title}' видалено з відстеження.")
        else:
            bot.send_message(CHAT_ID, "❌ Товар з таким номером не знайдено.")

        conn.close()

    except ValueError:
        bot.reply_to(message, "❌ Номер товару має бути цілим числом!")
    except Exception as e:
        print(f"Помилка в Telegram-обробнику: {e}")

def check_prices():
    conn = sqlite3.connect('tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, url, current_price, target_price FROM olx_tracker')
    products = cursor.fetchall()

    for prod in products:
        prod_id, title, url, current_price, target_price = prod
        print(f"⏳ Перевірка ціни для '{title}'...")
        _, new_price = get_price_pro(url)
        
        if new_price is not None:
            if new_price != current_price:
                cursor.execute('''
                    UPDATE olx_tracker
                    SET current_price = ?
                    WHERE id = ?
                ''', (new_price, prod_id))
                conn.commit()
                print(f"🔔 Ціна змінилася для '{title}': {current_price} zł -> {new_price} zł")
                
                if new_price <= target_price:
                    msg = f"🚀 **ЧАС КУПУВАТИ!**\n\n{title}\n🔥 Ціна впала до: {new_price} zł\n🎯 Твоя ціль була: {target_price} zł\n\n{url}"
                else:
                    msg = f"🔔 Ціна змінилася (але ще не ціль):\n\n{title}\n📉 Нова ціна: {new_price} zł\n(Чекаємо {target_price} zł)\n\n{url}"
                send_telegram_alert(msg)
            else:
                print(f"ℹ️ Ціна для '{title}' залишилася без змін: {current_price} zł")
        else:
            print(f"❌ Не вдалося отримати нову ціну для '{title}'.")
            print("Перевірте посилання\n {url}")
            

    conn.close()

def autoloop():
    print("Запуск автоматичної перевірки цін...")
    print("Натисни Ctrl+C, щоб зупинити.")
    while True:
        check_prices()
        print(f"Перевірка завершена. Наступна перевірка через 1 годину... ({time.strftime('%H:%M:%S')})")
        time.sleep(3600) 


if __name__ == "__main__":
    init_db()
    send_telegram_alert("👋 Хало! Pricoremindo активований і готовий до роботи.")
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    while True:
        print("\n--- LEGO SNIPER MENU ---")
        print("1. Додати новий товар")
        print("2. Перевірити ціни зараз")
        print("3. Запустити автоматичну перевірку")
        print("4. Вихід")
        choice = input("Обери дію: ")
        
        if choice == "1":
            add_product()
        elif choice == "2":
            check_prices()
        elif choice == "3":
            autoloop()
        elif choice == "4":
            print("Па-па! 👋")
            break