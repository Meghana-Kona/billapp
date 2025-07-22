from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Sample products
products = [
    {"id": 1, "name": "T-Shirt", "price": 250, "image": "https://via.placeholder.com/100", "category": "Fashion"},
    {"id": 2, "name": "Burger", "price": 120, "image": "https://via.placeholder.com/100", "category": "Food"},
    {"id": 3, "name": "Teddy Bear", "price": 300, "image": "https://via.placeholder.com/100", "category": "Toys"},
    {"id": 4, "name": "Jeans", "price": 600, "image": "https://via.placeholder.com/100", "category": "Fashion"},
    {"id": 5, "name": "Pizza", "price": 180, "image": "https://via.placeholder.com/100", "category": "Food"},
    {"id": 6, "name": "Lego Set", "price": 800, "image": "https://via.placeholder.com/100", "category": "Toys"},
]

# Create the database and table if not exist
def init_db():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer TEXT,
                    items TEXT,
                    total INTEGER
                )''')
    conn.commit()
    conn.close()

init_db()

# In-memory cart
cart = []

@app.route('/')
def home():
    categories = sorted(set(p['category'] for p in products))
    return render_template('index.html', categories=categories)

@app.route('/category/<category>')
def category_view(category):
    category_products = [p for p in products if p['category'] == category]
    return render_template('category.html', products=category_products, category=category)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        cart.append(product)
    return redirect('/cart')

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    global cart
    cart = [p for p in cart if p['id'] != product_id]
    return redirect('/cart')

@app.route('/cart')
def view_cart():
    total = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/confirm', methods=['POST'])
def confirm_bill():
    customer_name = request.form.get('customer_name')
    total = sum(item['price'] for item in cart)
    item_names = ", ".join(item['name'] for item in cart)

    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute("INSERT INTO bills (customer, items, total) VALUES (?, ?, ?)", (customer_name, item_names, total))
    conn.commit()
    conn.close()

    confirmed_items = list(cart)
    cart.clear()

    return render_template('confirm.html', items=confirmed_items, total=total, customer_name=customer_name)

@app.route('/history')
def view_history():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bills")
    bills = c.fetchall()
    conn.close()
    return render_template('history.html', bills=bills)

if __name__ == '__main__':
    app.run(debug=True)
