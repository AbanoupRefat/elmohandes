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

# Custom CSS for modern design and Arabic support with improved mobile responsiveness
st.markdown("""
<style>
    @import url(\'https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap\');
    
    * {
        font-family: \'Cairo\', sans-serif !important;
        
    }
    
    .main-header {
        text-align: center;
        color: #1e40af;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Category separator styling */
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
    
    .category-separator::before {
        content: \'\';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 80%;
        height: 3px;
        background: linear-gradient(90deg, transparent 0%, #2196f3 50%, transparent 100%);
        border-radius: 2px;
    }
    
    .category-separator::after {
        content: \'✨\';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 5px 10px;
        border-radius: 50%;
        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
        font-size: 1.2rem;
    }
    
    /* Sub-category separator styling */
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
    
    .sub-category-separator::before {
        content: \'\';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 60%;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #607d8b 50%, transparent 100%);
        border-radius: 1px;
    }
    
    /* Mobile-first responsive table container */
    .mobile-table-container {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    .products-table {
        min-width: 800px; /* Minimum width to maintain table structure, enable scrolling */
        width: 100%;
        background: white;
        border-radius: 12px;
        overflow: hidden;
    }
    
    .table-header {
        gap: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 1rem;
        direction: rtl;
        text-align: center;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .table-row {
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #f1f5f9;
        transition: background-color 0.2s ease;
        direction: rtl;
        align-items: center;
        min-height: 60px;
    }
    
    .table-row:last-child {
        border-bottom: none;
    }
    
    .product-name-cell {
        font-weight: 600;
        color: #fffff;
        font-size: 0.95rem;
        text-align: right;
        word-wrap: break-word;
        line-height: 1.4;
    }
    
    .origin-cell {
        color: #fffff;
        font-size: 0.9rem;
        text-align: center;
    }
    
    .price-cell {
        color: #2f855a;
        font-weight: 600;
        font-size: 0.95rem;
        text-align: center;
    }
    
    .qty-display {
        background: #ffffff;
        border: 2px solid #3b82f6;
        border-radius: 6px;
        padding: 0.25rem;
        text-align: center;
        font-weight: 700;
        color: #000000;
        font-size: 0.9rem;
        min-width: 40px;
    }
    
    .control-buttons {
        display: flex;
        gap: 0.25rem;
        justify-content: center;
        align-items: center;
    }
    
    .qty-btn {
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 4px;
        width: 24px;
        height: 24px;
        cursor: pointer;
        font-weight: bold;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background-color 0.2s;
    }
    
    .qty-btn:hover {
        background: #2563eb;
    }
    
    .subtotal-cell {
        color: #c53030;
        font-weight: 700;
        font-size: 0.95rem;
        text-align: center;
        background: #fed7d7;
        padding: 0.25rem;
        border-radius: 4px;
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
    
    .summary-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        display: block;
        color: white !important;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        color: white !important;
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
    
    .search-container {
        margin: 2rem 0;
        text-align: center;
    }
    
    .page-info {
        text-align: center; 
        padding: 0.5rem;
        background: #ffffff;
        border: 2px solid #3b82f6;
        border-radius: 8px;
        font-weight: 600;
        color: #1e293b;
    }
    
    .rtl {
        direction: rtl;
        text-align: right;
    }
    
    /* Scroll target styling */
    .scroll-target {
        scroll-margin-top: 20px;
    }
    
    /* Mobile responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }
        
        /* Switch to card layout for mobile instead of table */
        .mobile-table-container {
            margin: 0.5rem 0;
            border-radius: 8px;
            overflow: visible; /* Remove horizontal scroll */
        }
        
        .products-table {
            min-width: unset; /* Remove minimum width constraint */
            display: block; /* Switch from table to block layout */
        }
        
        /* Hide the table header on mobile */
        .table-header {
            display: none;
        }
        
        /* Convert table rows to card layout */
        .table-row {
            display: block;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            margin-bottom: 1rem;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            direction: rtl;
        }
        
        /* Product card styling */
        .mobile-product-card {
            display: grid;
            grid-template-columns: 1fr;
            gap: 0.75rem;
            width: 100%;
        }
        
        .mobile-product-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        .mobile-product-name {
            font-weight: 700;
            font-size: 1.1rem;
            color: #1e293b;
            flex: 1;
            text-align: right;
            line-height: 1.3;
        }
        
        .mobile-product-origin {
            background: #f8fafc;
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-size: 0.85rem;
            color: #64748b;
            border: 1px solid #e2e8f0;
            margin-right: 0.5rem;
        }
        
        .mobile-product-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
            align-items: center;
        }
        
        .mobile-price-section {
            text-align: center;
        }
        
        .mobile-price-label {
            font-size: 0.8rem;
            color: #64748b;
            margin-bottom: 0.25rem;
            font-weight: 500;
        }
        
        .mobile-price-value {
            font-size: 1.1rem;
            font-weight: 700;
            color: #059669;
            background: #ecfdf5;
            padding: 0.5rem;
            border-radius: 8px;
            border: 2px solid #10b981;
        }
        
        .mobile-quantity-section {
            text-align: center;
        }
        
        .mobile-quantity-label {
            font-size: 0.8rem;
            color: #64748b;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .mobile-quantity-controls {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
        }
        
        .mobile-qty-btn {
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
        
        .mobile-qty-btn:hover {
            background: #2563eb;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4);
        }
        
        .mobile-qty-display {
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
        
        .mobile-subtotal-section {
            grid-column: 1 / -1;
            text-align: center;
            margin-top: 0.5rem;
            padding-top: 0.75rem;
            border-top: 1px solid #f1f5f9;
        }
        
        .mobile-subtotal-label {
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 0.25rem;
            font-weight: 500;
        }
        
        .mobile-subtotal-value {
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
        
        /* Category and sub-category separators remain the same */
        .category-separator {
            margin: 1.5rem 0;
            height: 35px;
        }
        
        .sub-category-separator {
            margin: 1rem 0;
            height: 12px;
        }
        
        /* Summary cards */
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
        
        /* Order details for mobile */
        .order-detail-row {
            display: block;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            padding: 0.75rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .order-detail-item {
            font-size: 1rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.5rem;
            text-align: right;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 0.5rem;
        }
        
        .mobile-order-details {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 0.5rem;
            text-align: center;
        }
        
        .mobile-order-detail-item {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .mobile-order-detail-label {
            font-size: 0.75rem;
            color: #64748b;
            margin-bottom: 0.25rem;
        }
        
        .mobile-order-detail-value {
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .mobile-order-detail-qty {
            color: #1e293b;
        }
        
        .mobile-order-detail-price {
            color: #059669;
        }
        
        .mobile-order-detail-subtotal {
            color: #dc2626;
            background: #fef2f2;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
        }
    }

    @media (max-width: 480px) {
        .main-header {
            font-size: 1.5rem;
        }
        
        .mobile-product-name {
            font-size: 1rem;
        }
        
        .mobile-product-origin {
            font-size: 0.8rem;
            padding: 0.2rem 0.4rem;
        }
        
        .mobile-price-value {
            font-size: 1rem;
            padding: 0.4rem;
        }
        
        .mobile-qty-btn {
            width: 32px;
            height: 32px;
            font-size: 1rem;
        }
        
        .mobile-qty-display {
            font-size: 1rem;
            padding: 0.4rem;
            min-width: 45px;
        }
        
        .mobile-subtotal-value {
            font-size: 1.1rem;
            padding: 0.4rem 0.8rem;
        }
        
        .summary-card {
            padding: 0.75rem;
        }
        
        .stat-number {
            font-size: 1.5rem;
        }
        
        .whatsapp-btn {
            padding: 0.7rem 1rem;
            font-size: 0.9rem;
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
        
        # Determine headers from the first row
        headers = all_values[0]
        data_rows = all_values[1:]
        
        processed_data = []
        global_product_index = 0 # Initialize a global index for products
        for row in data_rows:
            # Check if the row is completely empty (or contains only whitespace)
            if not any(cell.strip() for cell in row):
                processed_data.append({
                    'type': 'sub_category_separator',
                    'category': ''
                }) # Placeholder for sub-category separator
            else:
                # Create a dictionary for the product row
                product_data = {}
                for i, header in enumerate(headers):
                    value = row[i]
                    if header == 'السعر':
                        try:
                            value = float(value) # Convert price to float
                        except ValueError:
                            value = 0.0 # Default to 0.0 if conversion fails
                    product_data[header] = value
                processed_data.append({
                    'type': 'product',
                    'data': product_data,
                    'global_id': global_product_index # Add a unique global ID
                })
                global_product_index += 1
        
        # Convert to DataFrame for easier processing later
        # We'll create a dummy DataFrame for now, and process the actual data later
        df = pd.DataFrame([item['data'] for item in processed_data if item['type'] == 'product'])
        
        # Ensure required columns exist for new structure
        required_columns = ['الفئة', 'البند', 'المنشأ', 'السعر']
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Missing required column: {col}")
                return pd.DataFrame()
        
        # Remove empty rows from the actual product data (they are now separators)
        df = df.dropna(subset=['البند'])
        df = df[df['البند'] != '']
        
        # Sort by category to group products together
        df = df.sort_values(['الفئة', 'البند'])
        
        return processed_data # Return the processed list with separators
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
            
            # Add main category separator when category changes
            if current_category is not None and category != current_category:
                grouped_products.append({
                    'type': 'category_separator',
                    'category': category
                })
            
            grouped_products.append(item) # Add the product
            current_category = category
            
        elif item['type'] == 'sub_category_separator':
            # Add sub-category separator
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
    
    # Add products with proper formatting
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
    """Display products in a responsive table format with category and sub-category separators"""
    if not grouped_products:
        st.warning("لا توجد منتجات للعرض")
        return
    
    # Create mobile-responsive table container with scroll target
    st.markdown('<div class="mobile-table-container scroll-target">', unsafe_allow_html=True)
    st.markdown('<div class="products-table">', unsafe_allow_html=True)
    
    # Table header using columns (hidden on mobile via CSS)
    header_cols = st.columns([3, 1.5, 1.2, 1, 1.5, 1.2])
    header_style = 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; text-align: center; font-weight: 600; border-radius: 8px; margin: 2px;'

    with header_cols[0]:
        st.markdown(f'<div class="table-header" style="{header_style}">البند</div>', unsafe_allow_html=True)
    with header_cols[1]:
        st.markdown(f'<div class="table-header" style="{header_style}">المنشأ</div>', unsafe_allow_html=True)
    with header_cols[2]:
        st.markdown(f'<div class="table-header" style="{header_style}">السعر</div>', unsafe_allow_html=True)
    with header_cols[3]:
        st.markdown(f'<div class="table-header" style="{header_style}">الكمية</div>', unsafe_allow_html=True)
    with header_cols[4]:
        st.markdown(f'<div class="table-header" style="{header_style}">التحكم</div>', unsafe_allow_html=True)
    with header_cols[5]:
        st.markdown(f'<div class="table-header" style="{header_style}">الإجمالي</div>', unsafe_allow_html=True)
    
    # Display each item (product or separator)
    for i, item in enumerate(grouped_products):
        if item['type'] == 'category_separator':
            # Display main category separator
            st.markdown('<div class="category-separator"></div>', unsafe_allow_html=True)
        
        elif item['type'] == 'sub_category_separator':
            # Display sub-category separator
            st.markdown('<div class="sub-category-separator"></div>', unsafe_allow_html=True)
        
        elif item['type'] == 'product':
            product = item['data']
            unique_key_base = item['global_id']
            
            product_name = product['البند']
            origin = product['المنشأ']
            price = product['السعر']
            
            # Get current quantity from cart
            current_qty = st.session_state.cart.get(product_name, {}).get('quantity', 0)
            subtotal = current_qty * price if current_qty > 0 else 0
            
            # Update cart with current price
            if product_name in st.session_state.cart:
                st.session_state.cart[product_name]['price'] = price
            
            # Create mobile card layout
            st.markdown(f'''
            <div class="table-row">
                <div class="mobile-product-card">
                    <div class="mobile-product-header">
                        <div class="mobile-product-name">{product_name}</div>
                        <div class="mobile-product-origin">{origin}</div>
                    </div>
                    <div class="mobile-product-details">
                        <div class="mobile-price-section">
                            <div class="mobile-price-label">السعر</div>
                            <div class="mobile-price-value">{price} ج.م</div>
                        </div>
                        <div class="mobile-quantity-section">
                            <div class="mobile-quantity-label">الكمية والتحكم</div>
                            <div class="mobile-quantity-controls">
            ''', unsafe_allow_html=True)
            
            # Create control buttons using Streamlit columns within the card
            btn_container = st.container()
            with btn_container:
                btn_cols = st.columns([1, 2, 1])
                with btn_cols[0]:
                    if st.button("➖", key=f"minus_{unique_key_base}", help="تقليل الكمية", use_container_width=True):
                        update_quantity(product_name, -1)
                        st.rerun()
                with btn_cols[1]:
                    st.markdown(f'<div class="mobile-qty-display">{current_qty}</div>', unsafe_allow_html=True)
                with btn_cols[2]:
                    if st.button("➕", key=f"plus_{unique_key_base}", help="زيادة الكمية", use_container_width=True):
                        if product_name not in st.session_state.cart:
                            st.session_state.cart[product_name] = {'quantity': 0, 'price': price}
                        update_quantity(product_name, 1)
                        st.rerun()
            
            # Close the mobile card and add subtotal
            subtotal_display = f"{subtotal} ج.م" if subtotal > 0 else "0 ج.م"
            st.markdown(f'''
                            </div>
                        </div>
                    </div>
                    <div class="mobile-subtotal-section">
                        <div class="mobile-subtotal-label">الإجمالي الجزئي</div>
                        <div class="mobile-subtotal-value">{subtotal_display}</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def display_order_details():
    """Display order details in a responsive format"""
    if not st.session_state.cart:
        return
    
    st.markdown("### 📋 تفاصيل الطلبية")
    
    # Header row (hidden on mobile via CSS)
    st.markdown("""
    <div class="order-detail-row" style="background: #f7fafc; font-weight: 700; display: none;">
        <div>المنتج</div>
        <div>الكمية</div>
        <div>السعر</div>
        <div>الإجمالي</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Product rows with mobile-friendly layout
    for product_name, details in st.session_state.cart.items():
        qty = details['quantity']
        price = details['price']
        subtotal = qty * price
        
        # Desktop version (table row)
        st.markdown(f'''
        <div class="order-detail-row">
            <div class="order-detail-item">{product_name}</div>
            <div class="mobile-order-details">
                <div class="mobile-order-detail-item">
                    <div class="mobile-order-detail-label">الكمية</div>
                    <div class="mobile-order-detail-value mobile-order-detail-qty">{qty} قطعة</div>
                </div>
                <div class="mobile-order-detail-item">
                    <div class="mobile-order-detail-label">السعر</div>
                    <div class="mobile-order-detail-value mobile-order-detail-price">{price} ج.م</div>
                </div>
                <div class="mobile-order-detail-item">
                    <div class="mobile-order-detail-label">الإجمالي</div>
                    <div class="mobile-order-detail-value mobile-order-detail-subtotal">{subtotal} ج.م</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

def navigate_to_page(new_page):
    """Navigate to a new page"""
    st.session_state.current_page = new_page
    # Scroll to the top of the products container after pagination
    st.markdown("<script>document.querySelector('.scroll-target').scrollIntoView({ behavior: 'smooth' });</script>", unsafe_allow_html=True)
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
        # Load data
        # df = load_google_sheet()
        processed_data_list = load_google_sheet()
        
        if not processed_data_list:
            st.error("لا يمكن تحميل البيانات من Google Sheets")
            return
        
        # Convert processed_data_list to a DataFrame for filtering
        # Only include product rows for filtering
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
                # Include sub-category separators in filtered list
                filtered_products_list.append(item)
        
        # Group products by category with separators (now including sub-category separators)
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
        
        # Display products with scroll target
        st.markdown(f"### المنتجات ( {st.session_state.current_page}/{total_pages})")
        
        # Create container for products table that will be scrolled to
        products_container = st.container()
        with products_container:
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
                st.markdown(f'<div class="page-info">{st.session_state.current_page}/{total_pages}</div>', 
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
            
            # Order details using the new responsive display
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
