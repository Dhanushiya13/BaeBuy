import streamlit as st
import sqlite3
import random
import json

# Connect to SQLite database
conn = sqlite3.connect("baebuy.db")
cursor = conn.cursor()

st.title("📦 Personalized Product Recommendations")

# User input (replacing input())
user_id = st.text_input("🔍 Enter a customer ID to get recommendations:")

# Only run if user_id is entered
if user_id:
    try:
        user_id = int(user_id)
        cursor.execute("SELECT * FROM customer WHERE id = ?", (user_id,))
        customer = cursor.fetchone()

        if customer:
            _, age, gender, location, purchase_history = customer
            st.write(f"Hello {gender.title()} shopper from {location}! 🛍️ Let's find your perfect picks...")

            # Convert string back to list
            try:
                purchase_history = json.loads(purchase_history)
            except:
                purchase_history = []

            category_counts = {}
            for pid in purchase_history:
                cursor.execute("SELECT category FROM products WHERE id = ?", (pid,))
                result = cursor.fetchone()
                if result:
                    category = result[0]
                    category_counts[category] = category_counts.get(category, 0) + 1

            top_categories = sorted(category_counts, key=category_counts.get, reverse=True)[:2]

            if not top_categories:
                cursor.execute("SELECT DISTINCT category FROM products")
                all_categories = [row[0] for row in cursor.fetchall()]
                top_categories = random.sample(all_categories, 2)

            recommendations = []
            for category in top_categories:
                cursor.execute("SELECT id, category, subcategory, price, attributes FROM products WHERE category = ? ORDER BY RANDOM() LIMIT 2", (category,))
                recommendations.extend(cursor.fetchall())

            for i, (pid, category, subcategory, price, attributes) in enumerate(recommendations):
                attributes = json.loads(attributes)
                reason = f"Based on your interest in {category} products like {subcategory}"
                fun_fact = random.choice([
                    "🔥 This one's trending big time!",
                    "🌟 Customer favorite pick!",
                    "🚀 Limited stock alert!",
                    "💡 AI thinks this fits your style!"
                ])
                st.markdown(f"""
                #### 🛍️ Recommendation {i+1}
                - **Product**: {subcategory}
                - **Category**: {category}
                - **Price**: ₹{price}
                - **Why?**: {reason}
                - **Fun Fact**: {fun_fact}
                """)

        else:
            st.error("⚠️ Customer ID not found. Please try another!")

    except ValueError:
        st.error("❌ Please enter a valid numeric customer ID.")
