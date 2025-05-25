
import requests
from flask import Flask, render_template, request, redirect
from threading import Thread
import time
import telegram

app = Flask(__name__)

# Конфигурация (изменяется в интерфейсе)
target_price = 97000
telegram_token = ""
telegram_user_id = ""
interval = 60  # секунд

# Получение цены BTC
def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur"
    try:
        response = requests.get(url)
        return response.json()["bitcoin"]["eur"]
    except:
        return None

# Telegram уведомление
def notify(price):
    try:
        bot = telegram.Bot(token=telegram_token)
        bot.send_message(chat_id=telegram_user_id, text=f"Цена BTC достигла {price}€")
    except Exception as e:
        print("Ошибка при отправке уведомления:", e)

# Фоновая проверка
def check_price_loop():
    global target_price
    while True:
        price = get_btc_price()
        if price and target_price and price >= target_price:
            notify(price)
        time.sleep(interval)

@app.route("/", methods=["GET", "POST"])
def index():
    global target_price, telegram_token, telegram_user_id
    message = ""
    if request.method == "POST":
        try:
            target_price = int(request.form["target_price"])
            telegram_token = request.form["telegram_token"]
            telegram_user_id = request.form["telegram_user_id"]
            message = "Настройки обновлены!"
        except Exception as e:
            message = f"Ошибка: {e}"
    price = get_btc_price()
    return render_template("index.html", price=price, target=target_price, message=message)

# Запуск фонового потока
Thread(target=check_price_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
