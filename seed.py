import sqlite3

products = [
    ("Creatine Monohydrate", "Boost muscle power and recovery", 15000, "creatine.jpg"),
    ("Whey Protein", "High-quality protein for muscle growth", 30000, "whey.jpg"),
    ("BCAA", "Essential amino acids for recovery", 18000, "bcaa.jpg")
]

with sqlite3.connect("database.db") as conn:
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)", products)
    conn.commit()
