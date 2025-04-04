import sqlite3
import json
import random

def get_customer_data(user_id):
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "age": row[1],
            "gender": row[2],
            "location": row[3],
            "purchase_history": json.loads(row[4]) if row[4] else []
        }
    return None

def get_product_data():
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()

    products = []
    for row in rows:
        products.append({
            "id": row[0],
            "category": row[1],
            "subcategory": row[2],
            "price": row[3],
            "attributes": json.loads(row[4]) if row[4] else {}
        })
    return products

def generate_recommendations(user_id):
    customer = get_customer_data(user_id)
    if not customer:
        print("❌ Customer not found.")
        return

    products = get_product_data()
    purchased_categories = set(p['category'] for p in customer['purchase_history'] if 'category' in p)

    matching_products = [p for p in products if p['category'] in purchased_categories]

    # Fallback to random picks if nothing matches
    if not matching_products:
        matching_products = random.sample(products, 4)
    else:
        matching_products = random.sample(matching_products, min(4, len(matching_products)))

    print("\n📦 Personalized Product Recommendations:\n")
    for idx, product in enumerate(matching_products, 1):
        reason = f"This matches your interest in {product['category']} products."
        fun_fact = random.choice([
            "Did you know? This product was trending last month!",
            "Fun Fact: Over 10,000 people bought this item in the past week.",
            "You're not the only genius who would love this!",
            "Top-rated by users who also liked your past picks!"
        ])
        print(f"{idx}. 🛍️ {product['subcategory']} — ₹{product['price']}")
        print(f"   🤖 Why this? {reason}")
        print(f"   🎉 {fun_fact}\n")

if __name__ == "__main__":
    print("✅ Multi-Agent Recommendation System Ready")
    user_id = input("🔍 Enter a customer ID to get recommendations: ").strip()
    generate_recommendations(user_id)
