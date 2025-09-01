from flask import Flask, render_template, request, g, url_for, redirect
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'database.db'  # adapt if your DB filename differs
WHATSAPP_NUMBER = '8615677099760'  # <-- your Chinese number (no +, no spaces)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # <<-- lets us use product['name'] in templates
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    category = request.args.get('category')
    search = request.args.get('search')
    db = get_db()
    cursor = db.cursor()

    # Prioritize search, then category. If neither provided, show featured only.
    if search:
        cursor.execute("SELECT * FROM products WHERE name LIKE ? OR description LIKE ?", 
                       ('%'+search+'%', '%'+search+'%'))
    elif category:
        cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    else:
        # show featured (if you have a 'featured' column) or show empty list by default
        # If you want nothing until a category is selected, uncomment the next line:
        # products = []
        cursor.execute("SELECT * FROM products WHERE COALESCE(featured, 0) = 1")
    products = cursor.fetchall()

    # build list of categories dynamically (unique categories from DB)
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = [row['category'] for row in cursor.fetchall() if row['category']]

    return render_template('home.html',
                           products=products,
                           category=category,
                           categories=categories,
                           search=search,
                           whatsapp_number=WHATSAPP_NUMBER)

# Optional route: single product detail (used by quick view fallback)
@app.route('/product/<int:pid>')
def product_detail(pid):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (pid,))
    product = cursor.fetchone()
    if not product:
        return redirect(url_for('home'))
    return render_template('product_detail.html', product=product, whatsapp_number=WHATSAPP_NUMBER)
@app.route('/about')
def about():
    return render_template('about.html')



if __name__ == '__main__':
    app.run(debug=True)
