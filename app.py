from flask import Flask, request, redirect, url_for, session
import sqlite3
from datetime import datetime
import qrcode
import csv
import os

app = Flask(__name__)
app.secret_key = "luxe_western"

# =========================================================
# 🎨 UI STYLE (FINAL PRESENTATION LOOK)
# =========================================================
style = """
<style>
body {
    font-family: Arial;
    background: linear-gradient(to right, #fff5e6, #ffe6e6);
    margin: 0;
    padding: 20px;
}

h1, h2 {
    color: #333;
}

.card {
    background: white;
    padding: 15px;
    margin: 10px;
    display: inline-block;
    width: 220px;
    border-radius: 12px;
    box-shadow: 0 6px 15px rgba(0,0,0,0.1);
}

button, a {
    background: #ff4d4d;
    color: white;
    padding: 6px 10px;
    text-decoration: none;
    border-radius: 5px;
}

a:hover {
    background: #cc0000;
}

.table {
    background: white;
    padding: 20px;
    border-radius: 12px;
}
</style>
"""

# =========================================================
# 🍽 MENU (WESTERN)
# =========================================================
menu = {
    # 🍖 MAIN COURSE
    "Grilled Steak": 25,
    "Chicken Chop": 18,
    "Spaghetti Carbonara": 16,
    "Fish & Chips": 15,
    "Caesar Salad": 12,
    "Mushroom Soup": 10,

    # 🍔 ADDITIONAL FOOD
    "Beef Burger": 14,
    "Chicken Burger": 12,
    "Cheese Fries": 9,
    "Garlic Bread": 8,
    "Mac & Cheese": 13,

    # 🍹 DRINKS
    "Coke": 5,
    "Sprite": 5,
    "Iced Lemon Tea": 6,
    "Americano Coffee": 7,
    "Latte": 9,
    "Chocolate Milkshake": 10
}

stock = {item: 10 for item in menu}
cart = {}

# =========================================================
# 📸 IMAGES
# =========================================================
images = {
    "Grilled Steak": "https://images.unsplash.com/photo-1558030006-450675393462",
    "Chicken Chop": "https://images.unsplash.com/photo-1604908177522-040b7a0e8c58",
    "Spaghetti Carbonara": "https://images.unsplash.com/photo-1525755662778-989d0524087e",
    "Fish & Chips": "https://images.unsplash.com/photo-1571091718767-18b5b1457add",
    "Caesar Salad": "https://images.unsplash.com/photo-1550304943-4f24f54ddde9",
    "Mushroom Soup": "https://images.unsplash.com/photo-1604908554007-6c8b2a6c5a6d",

    # 🍔 NEW FOOD
    "Beef Burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd",
    "Chicken Burger": "https://images.unsplash.com/photo-1550547660-d9450f859349",
    "Cheese Fries": "https://images.unsplash.com/photo-1606755962773-d324e2d15d2f",
    "Garlic Bread": "https://images.unsplash.com/photo-1601050690597-df0568f70950",
    "Mac & Cheese": "https://images.unsplash.com/photo-1543352634-99a5d50ae78e",

    # 🍹 DRINKS
    "Coke": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e",
    "Sprite": "https://images.unsplash.com/photo-1625772299848-391b2a3b0d3f",
    "Iced Lemon Tea": "https://images.unsplash.com/photo-1551024709-8f23befc6f87",
    "Americano Coffee": "https://images.unsplash.com/photo-1509042239860-f550ce710b93",
    "Latte": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735",
    "Chocolate Milkshake": "https://images.unsplash.com/photo-1572490122747-3968b75cc699"
}
# =========================================================
# 🗄 DATABASE
# =========================================================
def init_db():
    conn = sqlite3.connect("restaurant.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            address TEXT,
            table_no TEXT,
            items TEXT,
            total REAL,
            payment TEXT,
            order_type TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =========================================================
# 📦 QR GENERATOR
# =========================================================
def generate_qr(amount):
    if not os.path.exists("static"):
        os.makedirs("static")

    img = qrcode.make(f"PAY RM {amount}")
    path = "static/qr.png"
    img.save(path)
    return path

# =========================================================
# 📄 RECEIPT GENERATOR
# =========================================================
def generate_receipt(name, items, total, payment, order_type):
    filename = f"receipt_{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    with open(filename + ".txt", "w") as f:
        f.write("LUXE PALETTE WESTERN RESTAURANT\n")
        f.write("=============================\n")
        f.write(f"Name: {name}\n")
        f.write(f"Items: {items}\n")
        f.write(f"Total: RM{total}\n")
        f.write(f"Payment: {payment}\n")
        f.write(f"Order Type: {order_type}\n")

    with open(filename + ".csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name","Items","Total","Payment","Order Type"])
        writer.writerow([name, items, total, payment, order_type])

    return filename

# =========================================================
# 🏠 HOME
# =========================================================
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        session["name"] = request.form["name"]
        session["phone"] = request.form["phone"]
        session["address"] = request.form["address"]
        session["table_no"] = request.form["table_no"]
        session["payment"] = request.form["payment"]
        session["order_type"] = request.form["order_type"]
        return redirect(url_for("menu_page"))

    return style + """
    <h1>🍽 Luxe Palette Western Restaurant</h1>

    <form method="post">
        Name: <input name="name"><br><br>
        Phone: <input name="phone"><br><br>
        Address: <input name="address"><br><br>
        Table No: <input name="table_no"><br><br>

        <h3>Order Type</h3>
        <input type="radio" name="order_type" value="Dine-in" required> Dine-in
        <input type="radio" name="order_type" value="Takeaway"> Takeaway

        <h3>Payment</h3>
        <input type="radio" name="payment" value="Cash" required> Cash
        <input type="radio" name="payment" value="QR"> QR

        <br><br>
        <button type="submit">Start Order</button>
    </form>
    """

# =========================================================
# 🍴 MENU PAGE
# =========================================================
@app.route("/menu")
def menu_page():
    html = style + "<h2>🍽 Western Menu</h2>"

    for item, price in menu.items():
        html += f"""
        <div class="card">
            <img src="{images[item]}" width="200"><br>
            <b>{item}</b><br>
            RM{price}<br><br>
            <a href="/add/{item}">Add</a>
        </div>
        """

    html += "<br><a href='/cart'>Go Cart</a>"
    return html

# =========================================================
# ➕ ADD
# =========================================================
@app.route("/add/<item>")
def add(item):
    cart[item] = cart.get(item, 0) + 1
    return redirect(url_for("menu_page"))

# =========================================================
# 🛒 CART
# =========================================================
@app.route("/cart")
def cart_page():
    html = style + "<h2>🛒 Cart</h2>"
    total = 0

    for item, qty in cart.items():
        price = menu[item] * qty
        total += price
        html += f"<p>{item} x {qty} = RM{price}</p>"

    html += f"<h3>Total: RM{total}</h3>"
    html += "<a href='/checkout'>Checkout</a>"
    return html

# =========================================================
# 💳 CHECKOUT (FINAL FIXED)
# =========================================================
@app.route("/checkout")
def checkout():
    if not cart:
        return "Cart empty"

    total = sum(menu[i]*q for i,q in cart.items())
    items = ", ".join([f"{i}x{q}" for i,q in cart.items()])

    name = session.get("name","Guest")
    phone = session.get("phone","")
    address = session.get("address","")
    table_no = session.get("table_no","")
    payment = session.get("payment","Cash")
    order_type = session.get("order_type","Dine-in")

    qr_img = ""

    if payment == "QR":
        generate_qr(total)
        qr_img = "<img src='/static/qr.png' width='200'>"

    conn = sqlite3.connect("restaurant.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders
        (name, phone, address, table_no, items, total, payment, order_type, time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, phone, address, table_no, items, total, payment, order_type, str(datetime.now())))
    conn.commit()
    conn.close()

    generate_receipt(name, items, total, payment, order_type)

    cart.clear()

    return style + f"""
    <div class="table">
    <h2>🎉 ORDER SUCCESS</h2>

    <p>Name: {name}</p>
    <p>Table: {table_no}</p>
    <p>Items: {items}</p>
    <p>Total: RM{total}</p>

    {qr_img}

    <p>Receipt generated ✔</p>

    <a href='/'>Back Home</a>
    </div>
    """

# =========================================================
# 🚀 RUN
# =========================================================
if __name__ == "__main__":
    app.run(debug=False)
