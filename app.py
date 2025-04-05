import streamlit as st
import sqlite3
import random
import re

# Title
st.title("📦 Personalized Product Recommendations")
st.write("🔍 Enter a customer ID to get recommendations:")

# Input box
user_input = st.text_input("", "")

# 🧠 Utility to get numeric ID
def extract_numeric_id(text):
    numeric = re.sub(r"\D", "", text)
    return int(numeric) if numeric.isdigit() else None

# 🌟 Fun facts
fun_facts = [
    "Did you know? This item is trending among your peers!",
    "Customers like you loved this one ❤️",
    "Hot pick of the week 🔥",
    "Pairs well with your past purchases!",
    "Based on your vibe, we knew you'd love this!"
]

# 🚀 Get recommendations
def get_recommendations(customer_id):
    conn = sqlite3.connect("ecommerce")
    cursor = conn.cursor()

    cursor.execute("SELECT purchase_history FROM customer WHERE id = ?", (customer_id,))
    row = cursor.fetchone()
    if not row:
        return []

    purchase_history = row[0].split(", ")
    if not purchase_history:
        return []

    product_list = []
    for item in purchase_history:
        cursor.execute("""
            SELECT id, category FROM products
            WHERE id = ?
        """, (item,))
        data = cursor.fetchone()
        if data:
            product_list.append(data[1])  # category

    recommended = []
    for cat in set(product_list):
        cursor.execute("""
            SELECT id, category, subcategory, price, attributes
            FROM products
            WHERE category = ?
            ORDER BY RANDOM()
            LIMIT 1
        """, (cat,))
        rec = cursor.fetchone()
        if rec:
            rec_dict = {
                "id": rec[0],
                "category": rec[1],
                "subcategory": rec[2],
                "price": f"${rec[3]:.2f}",
                "attributes": rec[4],
                "reason": f"Since you've shown interest in {cat.lower()} items.",
                "fun_fact": random.choice(fun_facts)
            }
            recommended.append(rec_dict)

    conn.close()
    return recommended[:4]

# 🖼️ Display logic
if user_input:
    customer_id = extract_numeric_id(user_input)
    if customer_id is None:
        st.error("❌ Please enter a valid numeric customer ID.")
    else:
        with st.spinner("Fetching smart picks for you..."):
            recs = get_recommendations(customer_id)
            if recs:
                for product in recs:
                    st.markdown(f"""
                    #### 🛍️ {product['subcategory']} - {product['price']}
                    - 💡 {product['reason']}
                    - ✨ {product['fun_fact']}
                    """)
            else:
                st.warning("Oops! No recommendations found for this customer.")
