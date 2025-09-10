from flask import Flask, render_template, request, g, url_for, redirect, flash
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Needed for flash messages

DATABASE = 'database.db'  # adapt if your DB filename differs
WHATSAPP_NUMBER = '8615677099760'  # <-- your Chinese number (no +, no spaces)

# --- Email settings ---
EMAIL_ADDRESS = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_app_password'  # Use Gmail App Password

# --- Database helpers ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Routes ---

@app.route('/')
def home():
    category = request.args.get('category')
    search = request.args.get('search')
    db = get_db()
    cursor = db.cursor()

    if search:
        cursor.execute("SELECT * FROM products WHERE name LIKE ? OR description LIKE ?",
                       ('%' + search + '%', '%' + search + '%'))
    elif category:
        cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT * FROM products WHERE COALESCE(featured, 0) = 1")
    products = cursor.fetchall()

    cursor.execute("SELECT DISTINCT category FROM products")
    categories = [row['category'] for row in cursor.fetchall() if row['category']]

    return render_template('home.html',
                           products=products,
                           category=category,
                           categories=categories,
                           search=search,
                           whatsapp_number=WHATSAPP_NUMBER)

@app.route('/product/<int:pid>')
def product_detail(pid):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (pid,))
    product = cursor.fetchone()
    if not product:
        return redirect(url_for('home'))
    return render_template('product_detail.html', product=product, whatsapp_number=WHATSAPP_NUMBER)

@app.route('/category/<name>')
def category(name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ?", (name,))
    products = cursor.fetchall()

    cursor.execute("SELECT DISTINCT category FROM products")
    categories = [row['category'] for row in cursor.fetchall() if row['category']]

    return render_template('home.html',
                           products=products,
                           category=name,
                           categories=categories,
                           whatsapp_number=WHATSAPP_NUMBER)

@app.route('/about')
def about():
    return render_template('about.html')

# --- Contact page and form handling ---
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash("Please fill in all fields.")
            return redirect(url_for('home') + "#contact-form")

        # --- Send email ---
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = EMAIL_ADDRESS  # send to yourself
            msg['Subject'] = f"New Contact Form Message from {name}"

            body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()

            flash("Message sent successfully!")
            return redirect(url_for('home') + "#contact-form")

        except Exception as e:
            print("Error sending email:", e)
            flash("Failed to send message. Try again later.")
            return redirect(url_for('home') + "#contact-form")

    return redirect(url_for('home') + "#contact-form")

# --- Run the app ---
if __name__ == '__main__':
    app.run(debug=True)
