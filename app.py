from flask import Flask, request, redirect, url_for, session, send_file
import sqlite3
from datetime import datetime
import qrcode
import csv
import os
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.parse import unquote

app = Flask(__name__)
app.secret_key = "luxe_western"

# =========================================================
# 🎨 UI STYLE
# =========================================================
style = """
<style>
body {
    font-family: Arial;
    background: linear-gradient(to right,#fff5e6,#ffe6e6);
    margin:0;
    padding:20px;
}
.card {
    background:white;
    padding:15px;
    margin:10px;
    display:inline-block;
    width:220px;
    border-radius:12px;
    box-shadow:0 6px 15px rgba(0,0,0,0.1);
    transition:0.3s;
}
.card:hover { transform:scale(1.05); }
button,a {
    background:#ff4d4d;
    color:white;
    padding:6px 10px;
    border-radius:5px;
    text-decoration:none;
}
</style>
"""

# =========================================================
# 🍽 MENU
# =========================================================
menu = {
    "Grilled Steak":25,
    "Chicken Chop":18,
    "Lamb Chop":28,
    "Spaghetti Carbonara":16,
    "Fish & Chips":15,
    "Caesar Salad":12,
    "Chicken Burger":12,
    "Beef Burger":14,
    "Cheese Fries":9,
    "Coke":5,
    "Sprite":5,
    "Latte":9
}

images = {item:"https://source.unsplash.com/400x300/?"+item.replace(" ","") for item in menu}

# =========================================================
# 🛒 SESSION CART
# =========================================================

def get_cart():
    return session.setdefault("cart",{})

# =========================================================
# DATABASE
# =========================================================

def init_db():
    conn=sqlite3.connect("restaurant.db")
    c=conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        address TEXT,
        table_no TEXT,
        order_type TEXT,
        payment TEXT,
        items TEXT,
        total REAL,
        time TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

ADMIN_PASS="1234"

# =========================================================
# QR
# =========================================================

def qr_generate(amount):
    os.makedirs("static",exist_ok=True)
    img=qrcode.make(f"PAY RM {amount}")
    path="static/qr.png"
    img.save(path)
    return path

# =========================================================
# PDF
# =========================================================

def pdf_receipt(name,items,total,phone,address,table_no,payment,order_type):
    os.makedirs("static",exist_ok=True)
    file=f"static/receipt_{datetime.now().strftime('%H%M%S')}.pdf"
    c=canvas.Canvas(file,pagesize=letter)

    c.setFont("Helvetica-Bold",16)
    c.drawString(200,750,"LUXE RESTAURANT")

    c.setFont("Helvetica",12)
    c.drawString(50,700,f"Name: {name}")
    c.drawString(50,680,f"Phone: {phone}")
    c.drawString(50,660,f"Address: {address}")
    c.drawString(50,640,f"Table: {table_no}")
    c.drawString(50,620,f"Order Type: {order_type}")
    c.drawString(50,600,f"Payment: {payment}")
    c.drawString(50,580,f"Items: {items}")
    c.drawString(50,560,f"Total: RM{total}")
    c.drawString(50,540,f"Time: {datetime.now()}")

    c.save()
    return file

# =========================================================
# HOME
# =========================================================
@app.route("/",methods=["GET","POST"])
def home():
    if request.method=="POST":
        session["name"]=request.form["name"]
        session["phone"]=request.form["phone"]
        session["address"]=request.form["address"]
        session["table_no"]=request.form["table_no"]
        session["payment"]=request.form["payment"]
        session["order_type"]=request.form["order_type"]
        return redirect("/menu")

    return style+"""
    <h1>🍽 Luxe Western Restaurant</h1>
    <form method='post'>
    Name:<input name='name'><br><br>
    Phone:<input name='phone'><br><br>
    Address:<input name='address'><br><br>
    Table No:<input name='table_no'><br><br>

    <h3>Order Type</h3>
    <input type='radio' name='order_type' value='Dine-in' required>Dine-in
    <input type='radio' name='order_type' value='Takeaway'>Takeaway

    <h3>Payment</h3>
    <input type='radio' name='payment' value='Cash' required>Cash
    <input type='radio' name='payment' value='QR'>QR

    <br><br><button>Start</button>
    </form>
    """

# =========================================================
# MENU
# =========================================================
@app.route("/menu")
def menu_page():
    cart=get_cart()
    html=style+"<h2>Menu</h2>"

    for item,price in menu.items():
        html+=f"""
        <div class='card'>
        <img src='{images[item]}' width='200'><br>
        <b>{item}</b><br>RM{price}<br>
        <a href='/add/{item}'>Add</a>
        </div>
        """

    html+="<br><a href='/cart'>Cart</a>"
    return html

# =========================================================
# ADD
# =========================================================
@app.route("/add/<item>")
def add(item):
    item=unquote(item)
    cart=get_cart()
    cart[item]=cart.get(item,0)+1
    session["cart"]=cart
    return redirect("/menu")

# =========================================================
# REMOVE
# =========================================================
@app.route("/remove/<item>")
def remove(item):
    cart=get_cart()
    if item in cart:
        cart[item]-=1
        if cart[item]<=0:
            del cart[item]
    session["cart"]=cart
    return redirect("/cart")

# =========================================================
# CART
# =========================================================
@app.route("/cart")
def cart_page():
    cart=get_cart()
    total=0

    html=style+"<h2>Cart</h2>"

    for i,q in cart.items():
        price=menu[i]*q
        total+=price
        html+=f"<p>{i} x{q} = RM{price} <a href='/remove/{i}'>-</a></p>"

    html+=f"<h3>Total RM{total}</h3><a href='/checkout'>Checkout</a>"
    return html

# =========================================================
# CHECKOUT (FIXED FULL DATA + QR)
# =========================================================
@app.route("/checkout")
def checkout():
    cart=get_cart()
    if not cart:
        return "Empty cart"

    total=sum(menu[i]*q for i,q in cart.items())
    items=", ".join([f"{i}x{q}" for i,q in cart.items()])

    name=session.get("name","Guest")
    phone=session.get("phone","-")
    address=session.get("address","-")
    table_no=session.get("table_no","-")
    payment=session.get("payment","Cash")
    order_type=session.get("order_type","Dine-in")

    qr_html=""
    if payment=="QR":
        qr_generate(total)
        qr_html="<img src='/static/qr.png' width='200'>"

    conn=sqlite3.connect("restaurant.db")
    c=conn.cursor()
    c.execute("""
        INSERT INTO orders(name,phone,address,table_no,order_type,payment,items,total,time)
        VALUES(?,?,?,?,?,?,?,?,?)
    """,(name,phone,address,table_no,order_type,payment,items,total,str(datetime.now())))
    conn.commit()
    conn.close()

    pdf=pdf_receipt(name,items,total,phone,address,table_no,payment,order_type)

    session["cart"]={}

    return style+f"""
    <h2>Order Success 🎉</h2>
    <p>Name:{name}</p>
    <p>Phone:{phone}</p>
    <p>Address:{address}</p>
    <p>Table:{table_no}</p>
    <p>Order Type:{order_type}</p>
    <p>Payment:{payment}</p>
    <p>Items:{items}</p>
    <p>Total: RM{total}</p>
    {qr_html}
    <br><a href='/download/{pdf}'>Download PDF</a>
    """

# =========================================================
# DOWNLOAD
# =========================================================
@app.route("/download/<path:file>")
def download(file):
    return send_file(file,as_attachment=True)

# =========================================================
# ADMIN
# =========================================================
@app.route("/admin",methods=["GET","POST"])
def admin():
    if request.method=="POST":
        if request.form["pass"]==ADMIN_PASS:
            session["admin"]=True

    if not session.get("admin"):
        return """
        <form method='post'>
        Password:<input name='pass'>
        <button>Login</button>
        </form>
        """

    conn=sqlite3.connect("restaurant.db")
    c=conn.cursor()
    c.execute("SELECT total FROM orders")
    data=c.fetchall()

    values=[i[0] for i in data]

    plt.figure()
    plt.plot(values,marker='o')
    plt.title("Sales")
    plt.savefig("static/chart.png")

    return style+"<h2>Admin Dashboard</h2><img src='/static/chart.png' width='500'>"

# =========================================================
# RUN
# =========================================================
if __name__=="__main__":
    app.run(debug=False)
