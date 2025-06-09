import streamlit as st
import pandas as pd
import gspread
from streamlit_extras.add_vertical_space import add_vertical_space
from google.oauth2.service_account import Credentials
import urllib.parse

# Page config for mobile
st.set_page_config(page_title="المهندس لقطع غيار السيارات", layout="wide")

st.markdown(
    """
    <style>
    body {
        background-color: #f9f9f9;
        color: #333;
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .separator {
        background-color: #ddd;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        margin: 10px 0;
    }
    .subcategory {
        background-color: #f1f1f1;
        padding: 5px;
        margin: 5px 0;
        border-radius: 3px;
        font-style: italic;
    }
    .summary-box {
        background-color: #fff;
        border: 2px solid #aaa;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📦 المهندس لقطع غيار السيارات")
add_vertical_space()

if st.button("📋 طلبية جديدة"):
    # Load from Google Sheet using credentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(st.secrets["google"]["sheet_id"])
    worksheet = sh.sheet1
    data = worksheet.get_all_values()

    # Convert to DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])
    df.columns = ["الفئة", "البند", "المنشأ", "السعر"]

    # UI Table with separators
    st.markdown("### 🛒 قائمة المنتجات")
    cart = []
    total_price = 0
    total_items = 0

    last_category = None
    sub_index = 0

    for i, row in df.iterrows():
        category = row["الفئة"]
        item = row["البند"]
        origin = row["المنشأ"]
        price = row["السعر"]

        if pd.isna(item) or item.strip() == "":
            st.markdown('<div class="subcategory">-- نهاية مجموعة فرعية --</div>', unsafe_allow_html=True)
            continue

        if category != last_category:
            st.markdown(f'<div class="separator">🧾 {category}</div>', unsafe_allow_html=True)
            last_category = category
            sub_index = 0

        # Unique key per row
        qty_key = f"qty_{i}"
        col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 2])
        with col1:
            st.markdown(f"**{item}**")
        with col2:
            st.markdown(f"{origin}")
        with col3:
            st.markdown(f"{price} ج")
        with col4:
            qty = st.number_input("الكمية", min_value=0, step=1, key=qty_key)
        with col5:
            subtotal = float(price) * qty
            if qty > 0:
                total_items += qty
                total_price += subtotal
                cart.append({
                    "البند": item,
                    "المنشأ": origin,
                    "السعر": price,
                    "الكمية": qty,
                    "الإجمالي": subtotal
                })
            st.markdown(f"{subtotal:.2f} ج")

    if cart:
        st.markdown("### 🧾 ملخص الطلب")
        with st.container():
            st.markdown('<div class="summary-box">', unsafe_allow_html=True)
            st.write(f"📦 عدد العناصر: **{total_items}**")
            st.write(f"💰 المجموع: **{total_price:.2f} ج**")
            st.markdown('</div>', unsafe_allow_html=True)

        # WhatsApp message
        st.markdown("### 📲 إرسال الطلب عبر واتساب")
        order_message = "طلبية جديدة:\n\n"
        for c in cart:
            order_message += f"- {c['البند']} ({c['المنشأ']}): {c['الكمية']} × {c['السعر']} = {c['الإجمالي']:.2f} ج\n"
        order_message += f"\n📦 الإجمالي: {total_price:.2f} ج"

        whatsapp_number = st.secrets["whatsapp"]["number"]
        whatsapp_link = f"https://wa.me/{whatsapp_number}?text={urllib.parse.quote(order_message)}"
        st.markdown(f"[📤 إرسال إلى واتساب]({whatsapp_link})", unsafe_allow_html=True)
