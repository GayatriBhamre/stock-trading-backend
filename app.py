# #from nsetools import Nse
# from flask import render_template
# from flask import Flask, jsonify, request
# import requests

# app = Flask(__name__)
# #nse = Nse()

# from db import init_db

# init_db()

# # Virtual user (training only)

# user = {
#     "balance": 50000  # ₹50,000 virtual money
# }


# # Sample NIFTY 50 stocks (first 5)

# NIFTY_STOCKS = {
#     "RELIANCE": "RELIANCE.NS",
#     "TCS": "TCS.NS",
#     "INFY": "INFY.NS",
#     "ICICIBANK": "ICICIBANK.NS",
#     "HDFCBANK": "HDFCBANK.NS"
# }


# # Get live price from Yahoo Finance

# '''def get_live_price(symbol):
#     url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
#     headers = {"User-Agent": "Mozilla/5.0"}

#     try:
#         response = requests.get(url, headers=headers, timeout=5)
#         if response.status_code != 200 or response.text.strip() == "":
#             return None
#         data = response.json()
#         return data["quoteResponse"]["result"][0]["regularMarketPrice"]
#     except (requests.exceptions.RequestException, IndexError, KeyError):
#         return None '''

# '''def get_live_price(symbol):
#     try:
#         stock_code = symbol.replace(".NS", "")
#         quote = nse.get_quote(stock_code)
#         return quote.get("lastPrice")
#     except:
#         return None'''

# def get_live_price(symbol):
#     mock_prices = {
#         "RELIANCE.NS": 2850,
#         "TCS.NS": 3720,
#         "INFY.NS": 1510,
#         "ICICIBANK.NS": 1030,
#         "HDFCBANK.NS": 1580
#     }
#     return mock_prices.get(symbol)



# # Health check

# @app.route("/")
# def home():
#     return "Backend running successfully"


# # Get balance

# @app.route("/api/balance", methods=["GET"])
# def get_balance():
#     return jsonify(user)


# # Get stocks with live prices

# @app.route("/api/stocks", methods=["GET"])
# def get_stocks():
#     stock_data = []
#     for name, symbol in NIFTY_STOCKS.items():
#         price = get_live_price(symbol)
#         stock_data.append({
#             "name": name,
#             "price": price if price is not None else "Unavailable"
#         })
#     return jsonify(stock_data)


# # Wishlist (combined GET & POST)

# wishlist = []

# @app.route("/api/wishlist", methods=["GET", "POST"])
# def wishlist_route():
#     if request.method == "POST":
#         data = request.json
#         if "symbol" not in data or "target_price" not in data:
#             return jsonify({"error": "Invalid request"}), 400

#         wishlist.append({
#             "symbol": data["symbol"],
#             "target_price": data["target_price"],
#             "status": "waiting"
#         })
#         return jsonify({"message": "Stock added to wishlist"})

#     else:  # GET
#         return jsonify(wishlist)


# # Check wishlist status with live prices

# @app.route("/api/wishlist/check", methods=["GET"])
# def check_wishlist():
#     for item in wishlist:
#         symbol = item["symbol"]

#         if symbol not in NIFTY_STOCKS:
#             item["status"] = "invalid symbol"
#             continue

#         live_price = get_live_price(NIFTY_STOCKS[symbol])

#         if live_price is None:
#             item["status"] = "price unavailable"
#         elif live_price <= item["target_price"]:
#             item["status"] = "eligible"
#         else:
#             item["status"] = "waiting"

#         item["live_price"] = live_price

#     return jsonify(wishlist)


# # Buy stock 

# @app.route("/api/order/buy", methods=["POST"])
# def buy_stock():
#     data = request.json
#     symbol = data.get("symbol")

#     if symbol not in NIFTY_STOCKS:
#         return jsonify({"error": "Invalid stock symbol"}), 400

#     live_price = get_live_price(NIFTY_STOCKS[symbol])
#     if live_price is None:
#         return jsonify({"error": "Live price unavailable"}), 400

#     if user["balance"] >= live_price:
#         user["balance"] -= live_price
#         return jsonify({
#             "message": "Order executed successfully",
#             "buy_price": live_price,
#             "remaining_balance": user["balance"]
#         })

#     return jsonify({"error": "Insufficient balance"}), 400

# @app.route("/dashboard")
# def dashboard():
#     return render_template("index.html")


# # Run server

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, jsonify, request, render_template
from db import init_db, get_db

app = Flask(__name__)

init_db()

user = {
    "balance": 50000
}

NIFTY_STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "HDFCBANK": "HDFCBANK.NS"
}

def get_live_price(symbol):
    prices = {
        "RELIANCE.NS": 2850,
        "TCS.NS": 3720,
        "INFY.NS": 1510,
        "ICICIBANK.NS": 1030,
        "HDFCBANK.NS": 1580
    }
    return prices.get(symbol)

@app.route("/")
def home():
    return "Backend running successfully"

@app.route("/api/balance", methods=["GET"])
def get_balance():
    return jsonify(user)

@app.route("/api/stocks", methods=["GET"])
def get_stocks():
    data = []
    for name, symbol in NIFTY_STOCKS.items():
        price = get_live_price(symbol)
        data.append({
            "name": name,
            "price": price if price else "Unavailable"
        })
    return jsonify(data)

@app.route("/api/wishlist", methods=["GET", "POST"])
def wishlist():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        data = request.json
        if "symbol" not in data or "target_price" not in data:
            return jsonify({"error": "Invalid request"}), 400

        cursor.execute(
            "INSERT INTO wishlist (symbol, target_price, status) VALUES (?, ?, ?)",
            (data["symbol"], data["target_price"], "waiting")
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Wishlist item saved"})

    rows = cursor.execute("SELECT * FROM wishlist").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/api/wishlist/check", methods=["GET"])
def check_wishlist():
    conn = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("SELECT * FROM wishlist").fetchall()

    for row in rows:
        symbol = row["symbol"]

        if symbol not in NIFTY_STOCKS:
            status = "invalid symbol"
            live_price = None
        else:
            live_price = get_live_price(NIFTY_STOCKS[symbol])
            status = "eligible" if live_price <= row["target_price"] else "waiting"

        cursor.execute(
            "UPDATE wishlist SET status=?, live_price=? WHERE id=?",
            (status, live_price, row["id"])
        )

    conn.commit()
    updated = cursor.execute("SELECT * FROM wishlist").fetchall()
    conn.close()

    return jsonify([dict(row) for row in updated])

@app.route("/api/order/buy", methods=["POST"])
def buy_stock():
    data = request.json
    symbol = data.get("symbol")

    if symbol not in NIFTY_STOCKS:
        return jsonify({"error": "Invalid stock"}), 400

    price = get_live_price(NIFTY_STOCKS[symbol])
    if not price:
        return jsonify({"error": "Live price unavailable"}), 400

    if user["balance"] < price:
        return jsonify({"error": "Insufficient balance"}), 400

    user["balance"] -= price

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (symbol, buy_price) VALUES (?, ?)",
        (symbol, price)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Order placed",
        "buy_price": price,
        "remaining_balance": user["balance"]
    })

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
