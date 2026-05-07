import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw
import requests
import io
import os

# 确保这些文件在你的目录下
from menu import menu, images
from database import init_db, insert_order, get_sales, best_item
from qr import generate_qr, generate_pdf
import cart as cart_logic 

class LuxeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Luxe Restaurant Desktop")
        self.geometry("800x800")
        self.configure(bg="#fff5e6")
        
        init_db() 
        
        self.session = {"cart": {}, "name":"", "phone":"", "address":"", "table_no":"", "order_type":"Dine-in", "payment":"Cash"}
        self.img_cache = {}

        self.container = tk.Frame(self, bg="#fff5e6")
        self.container.pack(fill="both", expand=True)
        
        self.show_frame("HomeFrame")

    def show_frame(self, frame_name):
        for child in self.container.winfo_children(): 
            child.destroy()
        
        frames = {
            "HomeFrame": HomeFrame,
            "MenuFrame": MenuFrame,
            "CartFrame": CartFrame,
            "AdminFrame": AdminFrame
        }
        
        frame_class = frames[frame_name]
        frame = frame_class(self.container, self)
        frame.pack(fill="both", expand=True)

class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#fff5e6")
        self.controller = controller
        
        tk.Label(self, text="Luxe Restaurant", font=("Arial", 24, "bold"), bg="#fff5e6").pack(pady=20)
        
        self.entries = {}
        for f in ["Name", "Phone", "Address", "Table_no"]:
            tk.Label(self, text=f, bg="#fff5e6").pack()
            e = tk.Entry(self, width=30)
            e.pack(pady=5)
            self.entries[f.lower()] = e

        tk.Button(self, text="START", bg="#ff4d4d", fg="white", width=20, command=self.save).pack(pady=20)
        
        tk.Button(self, text="ADMIN", bg="black", fg="white", width=20, 
                  command=lambda: controller.show_frame("AdminFrame")).pack(pady=5)

    def save(self):
        for k, v in self.entries.items():
            self.controller.session[k] = v.get()
        self.controller.show_frame("MenuFrame")

class MenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#fff5e6")
        self.controller = controller
        
        tk.Label(self, text="MENU", font=("Arial", 18, "bold"), bg="#fff5e6").pack(pady=10)
        
        canvas = tk.Canvas(self, bg="#fff5e6", highlightthickness=0)
        scroll_y = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg="#fff5e6")

        for item, price in menu.items():
            card = tk.Frame(frame, bg="white", padx=10, pady=10, bd=1, relief="groove")
            card.pack(fill="x", padx=10, pady=5)

            if item in controller.img_cache:
                photo = controller.img_cache[item]
            else:
                img_path = images.get(item) # 此时拿到的是 "img/steak.jpg"
                photo = None
                
                # --- 核心修改：优先读取本地图片 ---
                try:
                    # 检查路径是否存在
                    if os.path.exists(img_path):
                        image = Image.open(img_path).convert("RGB").resize((80, 80))
                        photo = ImageTk.PhotoImage(image)
                    else:
                        raise FileNotFoundError
                except:
                    # 如果本地没找到，显示彩色占位图
                    bg_color = (220, 220, 220) 
                    if "Steak" in item or "Chop" in item: bg_color = (255, 204, 204)
                    elif "Spaghetti" in item: bg_color = (255, 255, 204)
                    elif "Coke" in item or "tea" in item: bg_color = (204, 229, 255)
                    
                    placeholder = Image.new('RGB', (80, 80), color=bg_color)
                    draw = ImageDraw.Draw(placeholder)
                    draw.text((10, 35), item[:10], fill=(0, 0, 0)) 
                    photo = ImageTk.PhotoImage(placeholder)
                
                controller.img_cache[item] = photo 

            lbl = tk.Label(card, image=photo, bg="white")
            lbl.image = photo 
            lbl.pack(side="left", padx=10)

            tk.Label(card, text=f"{item}\nRM {price}", bg="white", font=("Arial", 12), justify="left").pack(side="left", padx=10)
            tk.Button(card, text="Add", bg="#4CAF50", fg="white", 
                      command=lambda i=item: self.add_item(i)).pack(side="right", padx=10)
        
        canvas.create_window((0,0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side="top", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        
        btn_frame = tk.Frame(self, bg="#fff5e6")
        btn_frame.pack(fill="x", side="bottom")
        tk.Button(btn_frame, text="VIEW CART", bg="#ff4d4d", fg="white", 
                  font=("Arial", 12, "bold"), height=2,
                  command=lambda: controller.show_frame("CartFrame")).pack(pady=10, fill="x", padx=20)

    def add_item(self, item):
        cart_logic.add(self.controller.session, item)
        messagebox.showinfo("Success", f"Added {item} to cart")

class CartFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#fff5e6")
        self.controller = controller
        self.render()

    def render(self):
        for w in self.winfo_children(): w.destroy()
        tk.Label(self, text="YOUR CART", font=("Arial", 18, "bold"), bg="#fff5e6").pack(pady=10)
        
        s = self.controller.session
        total = 0
        items_str_list = []

        if not s["cart"]:
            tk.Label(self, text="Cart is empty", bg="#fff5e6").pack(pady=20)
        else:
            for i, q in s["cart"].items():
                p = menu[i] * q
                total += p
                items_str_list.append(f"{i}x{q}")
                f = tk.Frame(self, bg="white", pady=5); f.pack(fill="x", padx=20, pady=2)
                tk.Label(f, text=f"{i} x{q} - RM{p}", bg="white", font=("Arial", 10)).pack(side="left", padx=5)
                tk.Button(f, text="Remove", fg="red", command=lambda x=i: self.remove_item(x)).pack(side="right", padx=5)

        tk.Label(self, text=f"Total: RM{total}", font=("Arial", 14, "bold"), bg="#fff5e6").pack(pady=10)
        
        if s["cart"]:
            tk.Button(self, text="CHECKOUT", bg="green", fg="white", font=("Arial", 12, "bold"),
                      command=lambda: self.checkout(total, ", ".join(items_str_list))).pack(pady=5, fill="x", padx=100)
        
        tk.Button(self, text="Back to Menu", command=lambda: self.controller.show_frame("MenuFrame")).pack(pady=5)

    def remove_item(self, item):
        cart_logic.remove(self.controller.session, item)
        self.render()

    def checkout(self, total, items_str):
        s = self.controller.session
        data = (s["name"], s["phone"], s["address"], s["table_no"], 
                s["order_type"], s["payment"], items_str, total, str(datetime.now()))
        insert_order(data)
        
        pdf = generate_pdf(s["name"], s["phone"], s["address"], s["table_no"], 
                          s["order_type"], s["payment"], items_str, total)
        qr_path = generate_qr(items_str, total)
        
        top = tk.Toplevel(self)
        top.title("Payment QR")
        
        try:
            img = Image.open(qr_path).resize((250, 250))
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(top, image=photo)
            label.image = photo 
            label.pack(pady=20)
        except:
            tk.Label(top, text="QR Error").pack(pady=20)

        tk.Label(top, text="Scan to Pay", font=("Arial", 14)).pack(pady=10)
        messagebox.showinfo("Done", f"Order placed!\nReceipt: {pdf}")
        
        s["cart"] = {} 
        self.controller.show_frame("HomeFrame")

class AdminFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#fff5e6")

        tk.Label(self, text="ADMIN DASHBOARD", font=("Arial", 20, "bold"), bg="#fff5e6").pack(pady=20)

        sales = get_sales() or 0
        best = best_item() or "N/A"

        tk.Label(self, text=f"Total Sales: RM {sales}", font=("Arial", 14), bg="#fff5e6").pack(pady=10)
        tk.Label(self, text=f"Best Selling Item: {best}", font=("Arial", 14), bg="#fff5e6").pack(pady=10)
        
        tk.Button(self, text="BACK", width=20, command=lambda: controller.show_frame("HomeFrame")).pack(pady=20)

if __name__ == "__main__":
    app = LuxeApp()
    app.mainloop()
