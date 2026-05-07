import sqlite3

def init_db():
    conn=sqlite3.connect("restaurant.db")
    c=conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY,
        name TEXT, phone TEXT, address TEXT,
        table_no TEXT, order_type TEXT, payment TEXT,
        items TEXT, total REAL, time TEXT)
    """)
    conn.commit(); conn.close()

def insert_order(data):
    conn=sqlite3.connect("restaurant.db")
    c=conn.cursor()
    c.execute("""INSERT INTO orders
    (name,phone,address,table_no,order_type,payment,items,total,time)
    VALUES(?,?,?,?,?,?,?,?,?)""",data)
    conn.commit(); conn.close()

def get_sales():
    conn=sqlite3.connect("restaurant.db")
    c=conn.cursor()
    c.execute("SELECT total FROM orders")
    data=c.fetchall()
    conn.close()
    return [i[0] for i in data]

def best_item():
    conn=sqlite3.connect("restaurant.db")
    c=conn.cursor()
    c.execute("SELECT items FROM orders")
    data=c.fetchall()
    conn.close()

    counter={}
    for row in data:
        items=row[0].split(", ")
        for i in items:
            name=i.split("x")[0]
            counter[name]=counter.get(name,0)+1

    return max(counter,key=counter.get) if counter else "None"
