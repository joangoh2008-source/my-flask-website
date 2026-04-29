from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/order", methods=["POST"])
def order():
    name = request.form.get("name")
    quantity = request.form.get("quantity")
    return f"Thank you {name}, your order of {quantity} bag(s) is received!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
