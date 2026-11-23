"""
Data Generator for CloudMart: Generates mock raw JSON order streams & customer updates
Simulates source REST API / Event Stream landing in S3 Bronze layer.
"""

import json
import os
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")

def generate_mock_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    customers = [
        {"customer_id": "CUST101", "name": "Alice Johnson", "city": "Seattle", "state": "WA", "email": "alice@example.com"},
        {"customer_id": "CUST102", "name": "Bob Smith", "city": "Austin", "state": "TX", "email": "bob@example.com"},
        {"customer_id": "CUST103", "name": "Charlie Brown", "city": "New York", "state": "NY", "email": "charlie@example.com"},
        {"customer_id": "CUST104", "name": "Diana Prince", "city": "San Francisco", "state": "CA", "email": "diana@example.com"},
    ]
    
    products = [
        {"product_id": "PROD01", "name": "Wireless Noise-Cancelling Headphones", "category": "Electronics", "price": 199.99},
        {"product_id": "PROD02", "name": "Ergonomic Office Chair", "category": "Furniture", "price": 349.50},
        {"product_id": "PROD03", "name": "Stainless Steel Water Bottle", "category": "Accessories", "price": 29.99},
        {"product_id": "PROD04", "name": "Mechanical Gaming Keyboard", "category": "Electronics", "price": 129.00},
        {"product_id": "PROD05", "name": "Organic Fair-Trade Coffee Beans", "category": "Grocery", "price": 18.50},
    ]

    orders = []
    base_time = datetime(2026, 10, 1, 9, 0, 0)
    
    # Generate 50 realistic order events with occasional duplicates & edge cases
    for i in range(1, 51):
        order_time = base_time + timedelta(hours=random.randint(1, 400), minutes=random.randint(0, 59))
        cust = random.choice(customers)
        prod = random.choice(products)
        qty = random.randint(1, 4)
        subtotal = round(prod["price"] * qty, 2)
        tax = round(subtotal * 0.08, 2)
        status = random.choices(["COMPLETED", "SHIPPED", "RETURNED", "CANCELLED"], weights=[0.7, 0.15, 0.1, 0.05])[0]

        order = {
            "order_id": f"ORD-{1000 + i}",
            "customer_id": cust["customer_id"],
            "product_id": prod["product_id"],
            "product_name": prod["name"],
            "product_category": prod["category"],
            "unit_price": prod["price"],
            "quantity": qty,
            "subtotal": subtotal,
            "tax": tax,
            "order_timestamp": order_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "payment_method": random.choice(["CREDIT_CARD", "PAYPAL", "UPI", "APPLE_PAY"])
        }
        orders.append(order)

    # Save to JSON
    orders_file = os.path.join(DATA_DIR, "orders_raw.json")
    with open(orders_file, "w") as f:
        json.dump(orders, f, indent=2)
        
    customers_file = os.path.join(DATA_DIR, "customers_raw.json")
    with open(customers_file, "w") as f:
        json.dump(customers, f, indent=2)

    print(f"Generated {len(orders)} orders in {orders_file}")
    print(f"Generated {len(customers)} customers in {customers_file}")

if __name__ == "__main__":
    generate_mock_data()
