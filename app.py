import streamlit as st
import pandas as pd
import gspread
from streamlit_extras.add_vertical_space import add_vertical_space
from google.oauth2.service_account import Credentials
import urllib.parse

# Page config optimized for mobile
st.set_page_config(
    page_title="المهندس لقطع غيار السيارات", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for mobile optimization and better Arabic text rendering
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    .main > div {
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Mobile-first responsive design */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    .main-title {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center !important;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    .category-separator {
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        color: white !important;
        padding: 12px 15px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 15px 0 10px 0;
        text-align: center !important;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
        border: none;
    }
    
    .subcategory-separator {
        background: linear-gradient(45deg, #fa709a 0%, #fee140 100%);
        color: #333 !important;
        padding: 8px 12px;
        margin: 8px 0;
        border-radius: 8px;
        font-weight: 600;
        font-style: italic;
        text-align: center !important;
        box-shadow: 0 2px 10px rgba(250, 112, 154, 0.3);
    }
    
    .product-row {
        background: white;
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .product-row:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .product-name {
        font-weight: 700;
        font-size: 1.1rem;
        color: #2c3e50;
        margin-bottom: 5px;
    }
    
    .product-origin {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-bottom: 5px;
    }
    
    .product-price {
        color: #e74c3c;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .summary-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .summary-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .summary-item:last-child {
        border-bottom: none;
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 10px;
        padding-top: 15px;
        border-top: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .whatsapp-button {
        background: linear-gradient(45deg, #25D366 0%, #128C7E 100%);
        color: white !important;
        padding: 15px 25px;
        border-radius: 50px;
        text-decoration: none !important;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
        text-align: center !important;
        box-shadow: 0 8px 25px rgba(37, 211, 102, 0.4);
        border: none;
        width: 100%;
        margin-top: 15px;
        transition: all 0.3s ease;
    }
    
    .whatsapp-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(37, 211, 102, 0.6);
    }
    
    /* Mobile quantity input styling */
    .stNumberInput input {
        text-align: center !important;
        font-weight: 600;
        border-radius: 8px;
        border: 2px solid #3498db;
        padding: 8px;
    }
    
    .stNumberInput input:focus {
        border-color: #2980b9;
        box-shadow: 0 0 10px rgba(52, 152, 219, 0.3);
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Hide Streamlit elements for cleaner mobile experience */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive columns for mobile */
    @media (max-width: 768px) {
        .row-widget.stHorizontal {
            flex-direction: column !important;
        }
        
        .product-row {
            padding: 12px;
        }
        
        .main-title {
            padding: 1rem;
            font-size: 1.5rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main title with enhanced styling
st.markdown('<div class="main-title"><h1>🚗 المهندس لقطع غيار السيارات</h1></div>', unsafe_allow_html=True)

# Initialize session state for cart if not exists
if 'cart_items' not in st.session_state:
    st.session_state.cart_items = []

# New Order Button
if st.button("🛒 طلبية جديدة", use_container_width=True):
    try:
        with st.spinner("جاري تحميل المنتجات..."):
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
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            df.columns = ["الفئة", "البند", "المنشأ", "السعر"]
            
            st.success("✅ تم تحميل المنتجات بنجاح!")
            add_vertical_space(2)
            
            # Product display with enhanced mobile design
            st.markdown("### 📋 قائمة المنتجات والأسعار")
            
            cart = []
            total_price = 0
            total_items = 0
            last_category = None
            
            for i, row in df.iterrows():
                category = row["الفئة"]
                item = row["البند"]
                origin = row["المنشأ"]
                price_str = str(row["السعر"]).strip()
                
                # Handle empty rows (subcategory separators)
                if pd.isna(item) or item.strip() == "":
                    st.markdown('<div class="subcategory-separator">── انتهاء مجموعة فرعية ──</div>', unsafe_allow_html=True)
                    continue
                
                # Category separator
                if category != last_category and category.strip():
                    st.markdown(f'<div class="category-separator">🏷️ {category}</div>', unsafe_allow_html=True)
                    last_category = category
                
                # Validate price
                try:
                    price = float(price_str)
                except (ValueError, TypeError):
                    continue
                
                # Product row with mobile-optimized layout
                with st.container():
                    st.markdown('<div class="product-row">', unsafe_allow_html=True)
                    
                    # Mobile-friendly layout: vertical stacking
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f'<div class="product-name">{item}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="product-origin">المنشأ: {origin}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="product-price">💰 {price} جنيه</div>', unsafe_allow_html=True)
                    
                    with col2:
                        qty_key = f"qty_{i}_{item}"
                        qty = st.number_input(
                            "الكمية", 
                            min_value=0, 
                            max_value=100,
                            step=1, 
                            key=qty_key,
                            help="اختر الكمية المطلوبة"
                        )
                        
                        if qty > 0:
                            subtotal = price * qty
                            st.success(f"الإجمالي: {subtotal:.2f} ج")
                            
                            total_items += qty
                            total_price += subtotal
                            cart.append({
                                "البند": item,
                                "المنشأ": origin,
                                "السعر": price,
                                "الكمية": qty,
                                "الإجمالي": subtotal
                            })
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    add_vertical_space(1)
            
            # Order Summary
            if cart:
                add_vertical_space(2)
                st.markdown("### 📊 ملخص الطلبية")
                
                # Enhanced summary card
                summary_html = f"""
                <div class="summary-card">
                    <div class="summary-item">
                        <span>📦 عدد الأصناف:</span>
                        <strong>{len(cart)} صنف</strong>
                    </div>
                    <div class="summary-item">
                        <span>🔢 إجمالي القطع:</span>
                        <strong>{total_items} قطعة</strong>
                    </div>
                    <div class="summary-item">
                        <span>💰 المبلغ الإجمالي:</span>
                        <strong>{total_price:.2f} جنيه</strong>
                    </div>
                </div>
                """
                st.markdown(summary_html, unsafe_allow_html=True)
                
                # Order details
                with st.expander("📋 تفاصيل الطلبية", expanded=False):
                    for idx, item in enumerate(cart, 1):
                        st.write(f"**{idx}.** {item['البند']} ({item['المنشأ']})")
                        st.write(f"   الكمية: {item['الكمية']} | السعر: {item['السعر']} ج | الإجمالي: {item['الإجمالي']:.2f} ج")
                        st.divider()
                
                # WhatsApp Integration
                add_vertical_space(2)
                st.markdown("### 📲 إرسال الطلبية")
                
                # Generate WhatsApp message
                order_message = "🛒 *طلبية جديدة من المهندس لقطع غيار السيارات*\n\n"
                order_message += "📋 *تفاصيل الطلبية:*\n"
                
                for idx, item in enumerate(cart, 1):
                    order_message += f"{idx}. *{item['البند']}* ({item['المنشأ']})\n"
                    order_message += f"   الكمية: {item['الكمية']} × {item['السعر']} ج = {item['الإجمالي']:.2f} ج\n\n"
                
                order_message += f"📊 *ملخص الطلبية:*\n"
                order_message += f"📦 عدد الأصناف: {len(cart)} صنف\n"
                order_message += f"🔢 إجمالي القطع: {total_items} قطعة\n"
                order_message += f"💰 *المبلغ الإجمالي: {total_price:.2f} جنيه*\n\n"
                order_message += "شكراً لكم 🙏"
                
                # WhatsApp link
                whatsapp_number = st.secrets["whatsapp"]["number"]
                encoded_message = urllib.parse.quote(order_message)
                whatsapp_link = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
                
                st.markdown(
                    f'<a href="{whatsapp_link}" target="_blank" class="whatsapp-button">'
                    f'📤 إرسال الطلبية عبر واتساب</a>',
                    unsafe_allow_html=True
                )
                
                st.info("💡 سيتم فتح واتساب تلقائياً مع رسالة تحتوي على تفاصيل طلبيتك")
            
            else:
                st.info("🛍️ لم يتم اختيار أي منتجات بعد. يرجى تحديد الكمية المطلوبة للمنتجات.")
        
        else:
            st.error("❌ لا توجد بيانات في الجدول")
            
    except Exception as e:
        st.error(f"❌ خطأ في تحميل البيانات: {str(e)}")
        st.info("يرجى التأكد من إعدادات الاتصال بـ Google Sheets")

else:
    # Welcome screen
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: white; border-radius: 15px; margin: 2rem 0; box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);">
        <h2 style="color: #667eea; margin-bottom: 1rem;">مرحباً بكم في متجر المهندس</h2>
        <p style="font-size: 1.1rem; color: #666; line-height: 1.6;">
            🚗 متخصصون في قطع غيار السيارات الأصلية والبديلة<br>
            🛠️ خبرة تزيد عن 15 عاماً في مجال قطع الغيار<br>
            🚚 خدمة توصيل سريعة وموثوقة<br>
            📞 دعم فني متخصص
        </p>
        <p style="color: #e74c3c; font-weight: 600; font-size: 1.1rem; margin-top: 1.5rem;">
            اضغط على "طلبية جديدة" لبدء التسوق
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
add_vertical_space(3)
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 0.9rem; padding: 1rem; border-top: 1px solid #ecf0f1;">
    💙 المهندس لقطع غيار السيارات - جودة وثقة منذ سنوات
</div>
""", unsafe_allow_html=True)
