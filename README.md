# 🎯 Pricoremindo

![Pricoremindo Logo](logo.png)

**Pricoremindo** is your personal price sniper. 
The bot automatically monitors prices for selected items (e.g., on OLX.pl) and instantly notifies you via Telegram when the price drops to your target level.

> "Don't overpay. Wait for your price."

---

## 🚀 Features

* **🕵️ Autonomous Monitoring:** Checks prices every hour in the background.
* **📱 Telegram Control:** Add, view, and remove items directly from your phone.
* **⚡ Hybrid Mode:** Runs simultaneously as a console application and a Telegram bot (powered by `threading`).
* **💾 Local Database:** All tracking data is securely stored in SQLite.
* **🔔 Smart Alerts:** * Notifies you of *any* price change.
    * Screams **"BUY NOW!"** when the price hits your target.

---

## 🛠 Tech Stack

* **Python 3.x**
* **SQLite3** (Data storage)
* **pyTelegramBotAPI** (Bot interface)
* **BeautifulSoup4 + Requests** (Web scraping)
* **Threading** (Concurrency)

---

## ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/pricoremindo.git](https://github.com/YOUR_USERNAME/pricoremindo.git)
    cd pricoremindo
    ```

2.  **Install dependencies:**
    ```bash
    pip install pyTelegramBotAPI beautifulsoup4 requests
    ```

3.  **Configuration:**
    Open `main.py` and update the following variables with your credentials:
    ```python
    TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
    CHAT_ID = 'YOUR_CHAT_ID'
    ```

4.  **Start the Sniper:**
    ```bash
    python main.py
    ```

---

## 🎮 How to Use

### Via Telegram:
Manage your tracking list from anywhere:

* `/add [url] [price]` — Add a new item to track
* `/remove [ID]` — Remove an item from tracking
* `/list` — Receive all of your items that you're tracking

### Via Terminal (Menu):
When running locally, you have access to the console menu:
1.  **Add Product** (Manual entry).
2.  **Check Prices Now** (Force update).
3.  **Start Auto-Monitoring** (Enters the hourly loop).

---

## 👨‍💻 Author

Created as a learning project to automate the routine hunt for LEGO sets and other treasures.
Open for suggestions and improvements!
