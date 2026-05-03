import streamlit as st
import sqlite3
import pandas as pd

# --- 1. App Configuration ---
st.set_page_config(page_title="Homzinterio ERP", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

# --- 2. Advanced Zoho-Style Custom CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f5f8; }
    header {visibility: hidden;}
    .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem;}
    
    /* Dark Sidebar Navigation */
    [data-testid="stSidebar"] { background-color: #1e2235 !important; border-right: none; }
    [data-testid="stSidebar"] * { color: #a1a5b7 !important; }
    [data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { color: #ffffff !important; }
    
    /* Menu Styling */
    div.row-widget.stRadio > div { gap: 2px; }
    div.row-widget.stRadio > div > label { padding: 10px 15px; border-radius: 6px; background-color: transparent; cursor: pointer; transition: 0.2s; }
    div.row-widget.stRadio > div > label:hover { background-color: #2b3046 !important; color: white !important; }
    div.row-widget.stRadio > div > label > div:first-child { display: none; }
    
    /* Cards and Containers */
    .z-card { background-color: white; border-radius: 8px; border: 1px solid #eef0f4; padding: 20px; box-shadow: 0px 2px 4px rgba(0,0,0,0.02); margin-bottom: 20px; }
    .z-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f1f4; padding-bottom: 10px; margin-bottom: 15px; }
    .z-title { font-size: 15px; font-weight: 600; color: #181c32; }
    
    /* Action Buttons */
    .btn-primary { background-color: #0052cc; color: white; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-size: 14px; font-weight: 500; }
    .btn-primary:hover { background-color: #0043a6; }
    </style>
""", unsafe_allow_html=True)

# --- 3. Database & State Setup ---
conn = sqlite3.connect('homzinterio.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS erp_items (
    id INTEGER PRIMARY KEY, item_type TEXT, name TEXT, sku TEXT, unit TEXT, 
    selling_price REAL, cost_price REAL, opening_stock REAL)''')
conn.commit()

# Initialize Session State for Routing
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'Home'
if 'item_page_mode' not in st.session_state:
    st.session_state.item_page_mode = 'list' # 'list' or 'create'

# --- 4. Sidebar Navigation ---
st.sidebar.markdown("<h2 style='color: white; margin-bottom: 0;'>🛋️ Homzinterio</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 12px; letter-spacing: 1px; color: #a1a5b7; margin-bottom: 20px;'>INVENTORY OS</p>", unsafe_allow_html=True)

menu_options = ["🏠 Home", "📦 Items", "🗃️ Inventory", "🛒 Sales"]
selected_menu = st.sidebar.radio("Navigation", menu_options, label_visibility="collapsed")

# Handle navigation clicks
if selected_menu != st.session_state.current_view:
    st.session_state.current_view = selected_menu
    if selected_menu == "📦 Items":
        st.session_state.item_page_mode = 'list' # Reset to list view when clicking sidebar

# ==========================================
#               PAGE VIEWS
# ==========================================

# --- PAGE 1: HOME (DASHBOARD) ---
if st.session_state.current_view == "🏠 Home":
    st.markdown("<h2 style='color: #181c32; margin-top: 15px;'>Dashboard</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([7, 3])
    with col1:
        st.markdown("""
        <div class="z-card">
            <div class="z-header"><span class="z-title">Inventory Summary</span></div>
            <div style="display: flex; gap: 20px;">
                <div style="flex: 1; text-align: center; border-right: 1px solid #eee;">
                    <h3 style="color: #3e97ff; margin:0;">142</h3><p style="color: #7e8299; font-size: 12px;">QUANTITY IN HAND</p>
                </div>
                <div style="flex: 1; text-align: center;">
                    <h3 style="color: #f1416c; margin:0;">3</h3><p style="color: #7e8299; font-size: 12px;">LOW STOCK ITEMS</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="z-card">
            <div class="z-header"><span class="z-title">Pending Actions</span></div>
            <p style="font-size: 13px; color: #5e6278;">› <b>12</b> Items to be packed</p>
            <p style="font-size: 13px; color: #5e6278;">› <b>4</b> Invoices pending</p>
        </div>
        """, unsafe_allow_html=True)

# --- PAGE 2: ITEMS MODULE ---
elif st.session_state.current_view == "📦 Items":
    
    # VIEW A: ITEM LIST (Data Table)
    if st.session_state.item_page_mode == 'list':
        col1, col2 = st.columns([8, 2])
        col1.markdown("<h2 style='color: #181c32; margin-top: 15px;'>Active Items</h2>", unsafe_allow_html=True)
        
        # "+ New" Button Logic
        if col2.button("➕ New Item", use_container_width=True, type="primary"):
            st.session_state.item_page_mode = 'create'
            st.rerun()

        st.markdown('<div class="z-card">', unsafe_allow_html=True)
        df = pd.read_sql_query("SELECT sku as 'SKU', name as 'Item Name', unit as 'Unit', opening_stock as 'Stock on Hand', selling_price as 'Selling Price (₹)' FROM erp_items", conn)
        
        if df.empty:
            st.info("No items found. Click '+ New Item' to start adding inventory.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # VIEW B: NEW ITEM FORM
    elif st.session_state.item_page_mode == 'create':
        st.markdown("<h2 style='color: #181c32; margin-top: 15px;'>New Item</h2>", unsafe_allow_html=True)
        
        # "Back to List" Button
        if st.button("⬅ Back to Items"):
            st.session_state.item_page_mode = 'list'
            st.rerun()

        st.markdown('<div class="z-card">', unsafe_allow_html=True)
        with st.form("add_item_form", clear_on_submit=True):
            
            c1, c2 = st.columns(2)
            item_type = c1.radio("Type", ["Goods", "Service"], horizontal=True)
            name = c1.text_input("Name *")
            sku = c2.text_input("SKU")
            unit = c2.selectbox("Unit *",["Sq.ft", "Sheets", "Pieces", "Kg", "Liters"])
            
            st.markdown("<hr style='border: 1px solid #eee;'>", unsafe_allow_html=True)
            
            col_sales, col_purch = st.columns(2)
            with col_sales:
                st.markdown("<b>☑ Sales Information</b>", unsafe_allow_html=True)
                selling_price = st.number_input("Selling Price (INR)", min_value=0.0)
            with col_purch:
                st.markdown("<b>☑ Purchase Information</b>", unsafe_allow_html=True)
                cost_price = st.number_input("Cost Price (INR)", min_value=0.0)
                
            st.markdown("<hr style='border: 1px solid #eee;'>", unsafe_allow_html=True)
            opening_stock = st.number_input("Opening Stock", min_value=0.0)
            
            submit = st.form_submit_button("Save Item", type="primary")
            
            if submit:
                if name:
                    c.execute("""INSERT INTO erp_items (item_type, name, sku, unit, selling_price, cost_price, opening_stock) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                              (item_type, name, sku, unit, selling_price, cost_price, opening_stock))
                    conn.commit()
                    st.success(f"Item '{name}' saved! Click 'Back to Items' to view it.")
                else:
                    st.error("Name is required.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- OTHER PAGES ---
else:
    st.markdown(f"<h2 style='color: #181c32; margin-top: 15px;'>{st.session_state.current_view}</h2>", unsafe_allow_html=True)
    st.info("Module under construction.")
