import streamlit as st
import sqlite3
import json

st.set_page_config(page_title="BaeBuy 💖", page_icon="💖", layout="centered")

st.markdown(
    """
    <style>
        body {
            background: linear-gradient(135deg, #4b0082, #fcd34d);
            background-size: 400% 400%;
            color: #f472b6;
        }
        .title {
            font-family: 'Noelan', cursive;
            font-size: 3em;
            color: #ff1493;
            text-align: center;
        }
        .subtitle {
            font-size: 1.2em;
            color: #7c3aed;
            font-family: 'Great Vibes', italic serif ;
            text-align: center;
        }
        .recommendation-card {
            border-radius: 2em;
            background-color: #ffffff10;
            padding: 1em;
            margin-bottom: 1em;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
    </style>
    """,
    unsafe_allow_html=True
)



# --- Title and Tagline ---
st.markdown("<div class='title'>BaeBuy 💖</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Because Shopping Should Feel Like a Love Story! 💕</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.subheader("🌟Your Digital Stylist is In👗!")

# --- Input ---
customer_id = st.text_input("📇 Let’s look you up! What’s your code? 🎟")

# --- Recommend Button ---
if st.button("Show my picks🎀"):
    if not customer_id:
        st.warning("Please Enter Valid Customer ID.")
    else:
        try:
            conn = sqlite3.connect("ecommerce.db")
            cursor = conn.cursor()

            # Fetch customer data
            cursor.execute("SELECT age, gender, purchase_history FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()

            if not row:
                st.error("🦥 That ID’s giving “do not disturb” energy. Let’s try another!")
            else:
                age, gender, purchase_history_str = row
                purchase_history = json.loads(purchase_history_str)

                # Favorite category detection
                category_counts = {}
                for pid in purchase_history:
                    cursor.execute("SELECT category FROM products WHERE id = ?", (pid,))
                    result = cursor.fetchone()
                    if result:
                        cat = result[0]
                        category_counts[cat] = category_counts.get(cat, 0) + 1

                # Age group logic
                if age < 25:
                    age_group_pref = ["Tech", "Fashion", "Skincare"]
                elif 25 <= age < 40:
                    age_group_pref = ["Home Decor", "Fitness", "Gourmet"]
                else:
                    age_group_pref = ["Books", "Wellness", "Kitchen"]

                gender_pref = []
                if gender.lower() == "female":
                    gender_pref = ["Beauty", "Skincare", "Fashion"]
                elif gender.lower() == "male":
                    gender_pref = ["Tech", "Fitness", "Grooming"]

                # Combine all preferences
                favorite_categories = sorted(category_counts, key=category_counts.get, reverse=True)
                preferred_categories = list(set(favorite_categories + age_group_pref + gender_pref))

                if not purchase_history:
                    st.info("No purchase history found. Recommending based on age and gender profile ✨")

                # Fetch candidate products
                if purchase_history:
                    placeholders = ','.join(['?'] * len(purchase_history))
                    query = f"SELECT id, category, subcategory, price, attributes FROM products WHERE id NOT IN ({placeholders})"
                    cursor.execute(query, tuple(purchase_history))
                else:
                    query = "SELECT id, category, subcategory, price, attributes FROM products"
                    cursor.execute(query)
                all_products = cursor.fetchall()

                # --- Improved Recommendation Scoring ---
                recommendations = []

                for pid, cat, subcat, price, attrs in all_products:
                    match_score = 0

                    # Give score based on matching category
                    if cat in favorite_categories:
                        match_score += 3
                    elif cat in age_group_pref:
                        match_score += 2
                    elif cat in gender_pref:
                        match_score += 1

                    # Parse attributes safely
                    try:
                        attributes = json.loads(attrs) if attrs else {}
                    except:
                        attributes = {}

                    if match_score > 0:
                        reason = f"Why you might love this: {cat} is a favorite among shoppers like you!"
                        fun_fact = f"🛍 Top choice for {gender.title()}s aged around {age}!"
                        recommendations.append({
                            "product_name": subcat,
                            "price": round(price, 2),
                            "reason": reason,
                            "fun_fact": fun_fact,
                            "score": match_score
                        })

                # Sort by match score (high to low)
                recommendations = sorted(recommendations, key=lambda x: -x['score'])

                if recommendations:
                    st.markdown("## 🛍 Smarter Picks, Just for You")
                    for rec in recommendations[:4]:
                        st.markdown(f"""
                        <div class='recommendation-card'>
                            <strong>{rec['product_name']}</strong><br>
                            💸 Price: ₹{rec['price']}<br>
                            ✨ {rec['reason']}<br>
                            💡 {rec['fun_fact']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No personalized recommendations found. Please check your customer ID or purchase history.")

            conn.close()
        except Exception as e:
            st.error(f"Oops! Something went wrong: {e}")
