import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import urllib.parse
import json
import hashlib
from typing import Dict, List
import math
from datetime import datetime
from collections import defaultdict

# Configure page
st.set_page_config(
    page_title="شركة المهندس لقطع غيار السيارات",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern design and Arabic support
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    * {
        font-family: 'Cairo', sans-serif !important;
    }
    
    .main-header {
        text-align: center;
        color: #1e40af; 
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .category-separator {
        height: 40px;
        background: linear-gradient(90deg, transparent 0%, #e3f2fd 20%, #e3f2fd 80%, transparent 100%);
        position: relative;
        margin: 20px 0;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .sub-category-separator {
        height: 15px;
        background: linear-gradient(90deg, transparent 0%, #cfd8dc 20%, #cfd8dc 80%, transparent 100%);
        position: relative;
        margin: 10px 0;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .summary-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .whatsapp-btn {
        background: #25d366;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
        text-decoration: none;
        display: inline-block;
        text-align: center;
    }
    
    .whatsapp-btn:hover {
        background: #128c7e;
        transform: translateY(-2px);
        color: white;
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }
        
        .product-card {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            margin-bottom: 1rem;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .product-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        .product-name {
            font-weight: 700;
            font-size: 1.1rem;
            color: #1e293b;
            text-align: right;
            flex: 1;
        }
        
        .product-origin {
            background: #f8fafc;
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-size: 0.85rem;
            color: #64748b;
            border: 1px solid #e2e8f0;
            margin-right: 0.5rem;
        }
        
        .price-section {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem;
            margin-top: 0.5rem;
        }
        
        .quantity-controls {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        
        .qty-btn {
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 8px;
            width: 36px;
            height: 36px;
            cursor: pointer;
            font-weight: bold;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
        }
        
        .qty-display {
            background: #ffffff;
            border: 2px solid #3b82f6;
            border-radius: 8px;
            padding: 0.5rem;
            text-align: center;
            font-weight: 700;
            color: #1e293b;
            font-size: 1.1rem;
            min-width: 50px;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .subtotal-section {
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid #f1f5f9;
            text-align: center;
        }
        
        .subtotal-label {
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 0.25rem;
            font-weight: 500;
        }
        
        .subtotal-value {
            font-size: 1.2rem;
            font-weight: 700;
            color: #dc2626;
            background: #fef2f2;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            border: 2px solid #f87171;
            display: inline-block;
            min-width: 100px;
        }
        
        .summary-card {
            margin: 0.5rem 0;
            padding: 1rem;
        }
        
        .summary-title {
            font-size: 1.1rem;
        }
        
        .stat-number {
            font-size: 1.8rem;
        }
        
        .whatsapp-btn {
            padding: 0.8rem 1.5rem;
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'show_order_form' not in st.session_state:
    st.session_state.show_order_form = False
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

@st.cache_data
def load_google_sheet():
    """Load data from Google Sheets with new structure: الفئة, البند, المنشأ, السعر"""
    try:
        # Get credentials from Streamlit secrets
        credentials_dict = dict(st.secrets["gcp_service_account"])
        # Define the required scopes for Google Sheets
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly', 
            'https://www.googleapis.com/auth/drive.readonly' 
        ]
        # Create credentials with proper scopes
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        # Connect to Google Sheets
        gc = gspread.authorize(credentials)
        sheet_id = st.secrets["google"]["sheet_id"]
        sheet = gc.open_by_key(sheet_id).sheet1
        
        # Get all values, including empty rows
        all_values = sheet.get_all_values()
        headers = all_values[0]
        data_rows = all_values[1:]
        
        processed_data = []
        global_product_index = 0
        
        for row in data_rows:
            if not any(cell.strip() for cell in row):
                processed_data.append({
                    'type': 'sub_category_separator',
                    'category': ''
                })
            else:
                product_data = {}
                for i, header in enumerate(headers):
                    value = row[i]
                    if header == 'السعر':
                        try:
                            value = float(value)
                        except ValueError:
                            value = 0.0
                    product_data[header] = value
                
                processed_data.append({
                    'type': 'product',
                    'data': product_data,
                    'global_id': global_product_index
                })
                global_product_index += 1
        
        df = pd.DataFrame([item['data'] for item in processed_data if item['type'] == 'product'])
        required_columns = ['الفئة', 'البند', 'المنشأ', 'السعر']
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Missing required column: {col}")
                return pd.DataFrame()
                
        df = df.dropna(subset=['البند'])
        df = df[df['البند'] != '']
        df = df.sort_values(['الفئة', 'البند'])
        
        return processed_data
    except Exception as e:
        st.error(f"Error loading Google Sheet: {str(e)}")
        return []

def group_products_by_category(data_list):
    """Group products by category and add separators, handling sub-category separators"""
    if not data_list:
        return []
        
    grouped_products = []
    current_category = None
    
    for item in data_list:
        if item['type'] == 'product':
            product = item['data']
            category = product['الفئة']
            
            if current_category is not None and category != current_category:
                grouped_products.append({
                    'type': 'category_separator',
                    'category': category
                })
                
            grouped_products.append(item)
            current_category = category
            
        elif item['type'] == 'sub_category_separator':
            grouped_products.append(item)
            
    return grouped_products

def update_quantity(product_name: str, change: int):
    """Update product quantity in cart"""
    if product_name not in st.session_state.cart:
        st.session_state.cart[product_name] = {'quantity': 0, 'price': 0.0}
        
    new_quantity = st.session_state.cart[product_name]['quantity'] + change
    st.session_state.cart[product_name]['quantity'] = max(0, new_quantity)
    
    if st.session_state.cart[product_name]['quantity'] == 0:
        del st.session_state.cart[product_name]

def get_cart_summary():
    """Get cart summary statistics"""
    total_items = sum(item['quantity'] for item in st.session_state.cart.values())
    total_cost = sum(item['quantity'] * item['price'] for item in st.session_state.cart.values())
    return total_items, total_cost

def generate_whatsapp_message():
    """Generate WhatsApp message with proper Arabic formatting"""
    if not st.session_state.cart:
        return ""
        
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_lines = [
        "🌟 *شركة المهندس لقطع غيار السيارات* 🌟",
        "",
        f"📅 *تاريخ الطلب:* {now}",
        "",
        "📋 *تفاصيل الطلبية:*",
        ""
    ]
    
    for product_name, details in st.session_state.cart.items():
        qty = details['quantity']
        price = details['price']
        subtotal = qty * price
        message_lines.append(f"🔹 *{product_name}*")
        message_lines.append(f"   - الكمية: {qty}")
        message_lines.append(f"   - السعر: {price} ج.م")
        message_lines.append(f"   - الإجمالي: *{subtotal} ج.م*")
        message_lines.append("")
        
    total_items, total_cost = get_cart_summary()
    message_lines.extend([
        "📊 *ملخص الطلبية:*",
        f"   - عدد الأصناف: {total_items}",
        f"   - الإجمالي النهائي: *{total_cost} ج.م*",
        "",
        "شكراً لثقتكم بنا!",
        "سيتم التواصل معكم قريباً لتأكيد الطلبية."
    ])
    
    message = "\n".join(message_lines)
    return urllib.parse.quote(message)

def display_products_table(grouped_products):
    """Display products in a responsive format optimized for mobile"""
    if not grouped_products:
        st.warning("لا توجد منتجات للعرض")
        return
        
    for i, item in enumerate(grouped_products):
        if item['type'] == 'category_separator':
            st.markdown('<div class="category-separator"></div>', unsafe_allow_html=True)
        elif item['type'] == 'sub_category_separator':
            st.markdown('<div class="sub-category-separator"></div>', unsafe_allow_html=True)
        elif item['type'] == 'product':
            product = item['data']
            unique_key_base = item['global_id']
            product_name = product['البند']
            origin = product['المنشأ']
            price = product['السعر']
            
            current_qty = st.session_state.cart.get(product_name, {}).get('quantity', 0)
            subtotal = current_qty * price if current_qty > 0 else 0
            
            # Update cart with current price
            if product_name in st.session_state.cart:
                st.session_state.cart[product_name]['price'] = price
                
            # Product card container
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            
            # Product header with name and origin
            st.markdown('<div class="product-header">', unsafe_allow_html=True)
            st.markdown(f'<div class="product-name">{product_name}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="product-origin">{origin}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Price section
            st.markdown('<div class="price-section">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("السعر")
                st.markdown(f"<strong>{price} ج.م</strong>")
            with col2:
                st.markdown("الإجمالي الجزئي")
                st.markdown(f"<strong>{subtotal} ج.م</strong>")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Quantity controls
            st.markdown('<div class="quantity-controls">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("➖", key=f"minus_{unique_key_base}", help="تقليل الكمية", use_container_width=True):
                    update_quantity(product_name, -1)
                    st.rerun()
                    
            with col2:
                st.markdown(f'<div class="qty-display">{current_qty}</div>', unsafe_allow_html=True)
                
            with col3:
                if st.button("➕", key=f"plus_{unique_key_base}", help="زيادة الكمية", use_container_width=True):
                    if product_name not in st.session_state.cart:
                        st.session_state.cart[product_name] = {'quantity': 0, 'price': price}
                    update_quantity(product_name, 1)
                    st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

def display_order_details():
    """Display order details in a responsive format"""
    if not st.session_state.cart:
        return
        
    st.markdown("### 📋 تفاصيل الطلبية")
    
    for product_name, details in st.session_state.cart.items():
        qty = details['quantity']
        price = details['price']
        subtotal = qty * price
        
        st.markdown(f'''
        <div class="product-card">
            <div class="product-header">
                <div class="product-name">{product_name}</div>
            </div>
            <div class="price-section">
                <div style="text-align: center;">
                    <div class="subtotal-label">الكمية</div>
                    <div class="subtotal-value">{qty} قطعة</div>
                </div>
                <div style="text-align: center;">
                    <div class="subtotal-label">السعر</div>
                    <div class="subtotal-value">{price} ج.م</div>
                </div>
                <div style="text-align: center;">
                    <div class="subtotal-label">الإجمالي</div>
                    <div class="subtotal-value">{subtotal} ج.م</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

def navigate_to_page(new_page):
    """Navigate to a new page"""
    st.session_state.current_page = new_page
    st.rerun()

def main():
    # Main header
    st.markdown('<h1 class="main-header rtl">شركة المهندس لقطع غيار السيارات 🚗</h1>', unsafe_allow_html=True)
    
    # New Order button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🛒 طلبية جديدة", use_container_width=True, type="primary"):
            st.session_state.show_order_form = True
            st.session_state.cart = {}
            st.session_state.current_page = 1
            st.rerun()
    
    if st.session_state.show_order_form:
        processed_data_list = load_google_sheet()
        
        if not processed_data_list:
            st.error("لا يمكن تحميل البيانات من Google Sheets")
            return
            
        # Convert to DataFrame for filtering
        df_for_filtering = pd.DataFrame([item['data'] for item in processed_data_list if item['type'] == 'product'])
        
        # Search functionality with filter options
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input("🔍 البحث في المنتجات", 
                                       value=st.session_state.search_query, 
                                       placeholder="ابحث عن قطعة غيار...")
        
        with col2:
            origin_filter = st.selectbox("تصفية حسب المنشأ", 
                                       ["الكل"] + list(df_for_filtering['المنشأ'].unique()))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Filter data based on search and origin
        filtered_products_list = []
        for item in processed_data_list:
            if item['type'] == 'product':
                product = item['data']
                match_search = True
                match_origin = True
                
                if search_query:
                    if search_query.lower() not in product['البند'].lower():
                        match_search = False
                        
                if origin_filter and origin_filter != "الكل":
                    if product['المنشأ'] != origin_filter:
                        match_origin = False
                        
                if match_search and match_origin:
                    filtered_products_list.append(item)
            elif item['type'] == 'sub_category_separator':
                filtered_products_list.append(item)
                
        # Group products by category with separators
        grouped_products = group_products_by_category(filtered_products_list)
        
        # Show results count
        product_count = len([item for item in grouped_products if item['type'] == 'product'])
        st.markdown(f"**عدد النتائج: {product_count} منتج**")
        
        # Pagination settings
        items_per_page = 15
        total_items = len(grouped_products)
        total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1
        
        if total_items == 0:
            st.warning("لا توجد منتجات تطابق البحث")
            return
            
        # Ensure current page is valid
        st.session_state.current_page = min(st.session_state.current_page, total_pages)
        st.session_state.current_page = max(st.session_state.current_page, 1)
        
        # Calculate pagination
        start_idx = (st.session_state.current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        current_items = grouped_products[start_idx:end_idx]
        
        # Display products
        st.markdown(f"### المنتجات ( {st.session_state.current_page}/{total_pages})")
        display_products_table(current_items)
        
        # Pagination controls
        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            with col1:
                if st.button("⏮️ الأولى", disabled=st.session_state.current_page == 1, use_container_width=True):
                    navigate_to_page(1)
            with col2:
                if st.button("⬅️ السابقة", disabled=st.session_state.current_page == 1, use_container_width=True):
                    navigate_to_page(st.session_state.current_page - 1)
            with col3:
                st.markdown(f'<div style="background: #bfdbfe; border-radius: 0.5rem; padding: 0.5rem; text-align: center;">{st.session_state.current_page}/{total_pages}</div>', 
                          unsafe_allow_html=True)
            with col4:
                if st.button("التالية ➡️", disabled=st.session_state.current_page == total_pages, use_container_width=True):
                    navigate_to_page(st.session_state.current_page + 1)
            with col5:
                if st.button("الأخيرة ⏭️", disabled=st.session_state.current_page == total_pages, use_container_width=True):
                    navigate_to_page(total_pages)
        
        # Order summary and review
        if st.session_state.cart:
            st.markdown("---")
            total_items, total_cost = get_cart_summary()
            
            # Summary cards
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="summary-card">
                    <div class="summary-title">📦 عدد الأصناف</div>
                    <div class="stat-number">{total_items}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="summary-card">
                    <div class="summary-title">💰 الإجمالي</div>
                    <div class="stat-number">{total_cost}</div>
                    <div class="stat-label">جنيه مصري</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Order details
            display_order_details()
            
            # WhatsApp send button
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                whatsapp_number = st.secrets["whatsapp"]["number"]
                whatsapp_message = generate_whatsapp_message()
                whatsapp_url = f"https://wa.me/{whatsapp_number}?text={whatsapp_message}"
                st.markdown(
                    f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">📱 إرسال الطلبية عبر واتساب</a>',
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    main()
