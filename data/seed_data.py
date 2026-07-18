"""
seed_data.py
-------------
This script creates a small SQLite database with FAKE (dummy) order data.

Why dummy data?
Real courier tracking (Delhivery, BlueDart, etc.) needs paid business accounts,
so for a portfolio project we simulate realistic order data instead. This is
completely normal for a learning/portfolio project - what matters is that the
CODE that reads and uses this data is written properly.

Run this once with: python seed_data.py
It will create a file called orders.db in the same folder.
"""

import sqlite3
import random
from datetime import datetime, timedelta

# ---- 1. Connect to (or create) the database file ----
# This creates a file named orders.db if it doesn't already exist.
connection = sqlite3.connect("orders.db")
cursor = connection.cursor()

# ---- 2. Create the "orders" table ----
# DROP TABLE IF EXISTS lets us re-run this script safely without errors.
cursor.execute("DROP TABLE IF EXISTS orders")

cursor.execute("""
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_name TEXT,
    product_name TEXT,
    order_date TEXT,
    expected_delivery TEXT,
    status TEXT,
    current_location TEXT,
    amount REAL,
    payment_method TEXT
)
""")

# ---- 3. Prepare some sample data to randomly pick from ----
products = [
    "Wireless Mouse", "Bluetooth Headphones", "Laptop Stand", "Mechanical Keyboard",
    "Running Shoes", "Cotton T-Shirt", "Smartwatch", "Yoga Mat", "Water Bottle",
    "Backpack", "Desk Lamp", "Phone Case"
]

customer_names = [
    "Ravi Kumar", "Sneha Reddy", "Arjun Rao", "Priya Sharma", "Kiran Naidu",
    "Anitha Devi", "Vikram Singh", "Meena Iyer", "Sanjay Gupta", "Divya Menon"
]

# Possible stages an order can be in, in logical order
status_options = ["Placed", "Processing", "Shipped", "Out for Delivery", "Delivered"]

locations = [
    "Hyderabad Hub", "Bengaluru Warehouse", "Chennai Sorting Center",
    "Mumbai Hub", "Delhi Warehouse", "Local Delivery Station"
]

payment_methods = ["UPI", "Credit Card", "Debit Card", "Cash on Delivery", "Net Banking"]

# ---- 4. Generate 30 fake orders ----
rows_to_insert = []

for i in range(1, 31):
    order_id = f"ORD{1000 + i}"                       # e.g. ORD1001, ORD1002...
    customer_name = random.choice(customer_names)
    product_name = random.choice(products)

    # Random order date within the last 20 days
    days_ago = random.randint(1, 20)
    order_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    # Expected delivery is 5-9 days after order date
    delivery_days = random.randint(5, 9)
    expected_delivery = (
        datetime.now() - timedelta(days=days_ago) + timedelta(days=delivery_days)
    ).strftime("%Y-%m-%d")

    status = random.choice(status_options)
    current_location = random.choice(locations)
    amount = round(random.uniform(299, 4999), 2)
    payment_method = random.choice(payment_methods)

    rows_to_insert.append((
        order_id, customer_name, product_name, order_date,
        expected_delivery, status, current_location, amount, payment_method
    ))

# ---- 5. Insert all rows into the table ----
cursor.executemany("""
INSERT INTO orders (
    order_id, customer_name, product_name, order_date,
    expected_delivery, status, current_location, amount, payment_method
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows_to_insert)

# ---- 6. Save changes and close ----
connection.commit()
connection.close()

print(f"Created orders.db with {len(rows_to_insert)} dummy orders.")
print("Sample order IDs:", [row[0] for row in rows_to_insert[:5]])
