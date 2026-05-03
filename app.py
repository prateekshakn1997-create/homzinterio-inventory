import streamlit as st
import sqlite3
import pandas as pd

# --- 1. App Configuration ---
st.set_page_config(page_title="Homzinterio OS", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

# --- 2. Advanced Zoho-Style Custom CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f5f8; }
    header {visibility: hidden;}
    .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem;}
    
    /* Dark Sidebar Navigation */
    [data-testid="stSidebar"] { background-color: #1e2235 !important; border-right: none; }[data-testid="stSidebar"] * { color: #a1a5b7 !important; }[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #ffffff !important; }
    
    div.row-widget.stRadio > div { gap: 2px; }
    div.row-widget.stRadio > div > label { padding: 10px 15px; border-radius: 6px; background-color: transparent; cursor: pointer; transition: 0.2s; }
    div.row-widget.stRadio > div > label:hover { background-color: #2b3046 !important; color: white !important; }
    div.row-widget.stRadio > div > label > div:first-child { display: none; }
    
    /* Item Form Specific Styling */
    .section-title { font-size: 16px; font-weight: 600; color: #181c32; margin-bottom: 10px; margin-top: 15px;}
    .help-text { font-size: 12px; color: #7e8299; margin-bottom: 10px; }
    hr { margin-top: 15px; margin-bottom: 15px; border-color: #eef0f4; }
    
    /* Style the Form Submit Button to look like Zoho's Blue Save Button */
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #3e97ff; color: white; border: none; padding: 5px 25px; border-radius: 4px; font-weight: 500;
    }
    div[data-testid="stFormSubmitButton"] > button:hover { background-color: #2884f2; }
    </style>
""", unsafe_allow_html=True)

# --- 3. Database Setup (Expanded for New Item Form) ---
conn = sqlite3.connect('homzinterio.db', check_same_thread=False)
c = conn.cursor()

# Expanded table for advanced items
c.execute('''CREATE TABLE IF NOT EXISTS erp_items (
    id INTEGER PRIMARY KEY, item_type TEXT, name TEXT, sku TEXT, unit TEXT, returnable BOOLEAN, 
    dimensions TEXT, weight TEXT, manufacturer TEXT, brand TEXT, 
    selling_price REAL, sales_account TEXT, sales_desc TEXT, 
    cost_price REAL, purchase_account TEXT, purchase_desc TEXT, preferred_vendor TEXT,
    inventory_account TEXT, opening_stock REAL, stock_rate REAL, reorder_point REAL
)''')
conn.commit()

# --- 4. Sidebar Navigation ---
st.sidebar.markdown("<h2 style='color: white; margin-bottom: 0;'>🛋️ Homzinterio</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 12px; letter-spacing: 1px; color: #a1a5b7; margin-bottom: 20px;'>INVENTORY OS</p>", unsafe_allow_html=True)

menu_options =["🏠 Home", "📦 Items", "🗃️ Inventory", "🛒 Sales", "🛍️ Purchases", "📊 Reports"]
choice = st.sidebar.radio("Navigation", menu_options, label_visibility="collapsed", index=1) # Set index=1 to default to Items page

# --- 5. Application Views ---

if choice == "📦 Items":
    # Header
    st.markdown("<h2 style='color: #181c32; margin-top: 15px; margin-bottom: 20px; font-weight: 500;'>New Item</h2>", unsafe_allow_html=True)
    
    # White background container for the form
    with st.container():
        st.markdown('<div style="background-color: white; padding: 30px; border-radius: 8px; border: 1px solid #eef0f4; box-shadow: 0px 2px 4px rgba(0,0,0,0.02);">', unsafe_allow_html=True)
        
        with st.form("new_item_form", clear_on_submit=True):
            # --- TOP SECTION (Basic Info & Image) ---
            col_left, col_right = st.columns([1.5, 1])
            
            with col_left:
                item_type = st.radio("Type", ["Goods", "Service"], horizontal=True)
                name = st.text_input("Name *")
                sku = st.text_input("SKU")
                unit = st.selectbox("Unit *",["Select or type to add", "Sq.ft", "Sheets", "Pieces", "Boxes", "Kg", "Liters", "Running Ft"])
                returnable = st.checkbox("Returnable Item")
            
            with col_right:
                # Image Uploader simulating Zoho's dashed box
                st.file_uploader("Drag image(s) here or Browse images", accept_multiple_files=True, help="You can add up to 15 images, each not exceeding 5 MB.")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # --- MIDDLE SECTION (Dimensions, Brand, etc.) ---
            c1, c2 = st.columns(2)
            with c1:
                dimensions = st.text_input("Dimensions (Length X Width X Height)")
                manufacturer = st.selectbox("Manufacturer",["Select or Add Manufacturer", "Hettich", "Greenply", "Merino", "Asian Paints"])
                upc = st.text_input("UPC")
                ean = st.text_input("EAN")
            with c2:
                weight = st.text_input("Weight")
                brand = st.selectbox("Brand",["Select or Add Brand", "Homzinterio Signature", "Standard"])
                mpn = st.text_input("MPN")
                isbn = st.text_input("ISBN")
                
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # --- SALES & PURCHASE INFORMATION SECTION ---
            col_sales, col_purch = st.columns(2)
            
            with col_sales:
                st.markdown("<div class='section-title'>☑ Sales Information</div>", unsafe_allow_html=True)
                selling_price = st.number_input("Selling Price * (INR)", min_value=0.0, step=1.0)
                sales_account = st.selectbox("Account *", ["[ 33547 ] Sales", "[ 33548 ] Services Revenue", "[ 33549 ] Discount"])
                sales_desc = st.text_area("Description", height=100)
            
            with col_purch:
                st.markdown("<div class='section-title'>☑ Purchase Information</div>", unsafe_allow_html=True)
                cost_price = st.number_input("Cost Price * (INR)", min_value=0.0, step=1.0)
                purch_account = st.selectbox("Account * (Purchase)", ["[ 28967 ] Cost of Goods Sold", "[ 28968 ] Raw Materials", "[ 28969 ] Hardware Assets"])
                purch_desc = st.text_area("Description (Purchase)", height=100)
                preferred_vendor = st.selectbox("Preferred Vendor", ["Select Vendor", "Plywood Distributors Inc.", "Hardware Hub BLR"])
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # --- INVENTORY TRACKING SECTION ---
            st.markdown("<div class='section-title'>☑ Track Inventory for this item</div>", unsafe_allow_html=True)
            st.markdown("<div class='help-text'>You cannot enable/disable inventory tracking once you've created transactions for this item</div>", unsafe_allow_html=True)
            
            inv_col1, inv_col2 = st.columns(2)
            with inv_col1:
                inv_account = st.selectbox("Inventory Account *", ["[ 65990 ] Inventory Asset", "[ 65991 ] Finished Goods"])
                opening_stock = st.number_input("Opening Stock", min_value=0.0, step=1.0)
                reorder_point = st.number_input("Reorder Point", min_value=0.0, step=1.0)
            with inv_col2:
                st.write("") # Spacer
                st.write("") # Spacer
                st.write("") # Spacer
                st.write("") # Spacer
                stock_rate = st.number_input("Opening Stock Rate per Unit", min_value=0.0, step=1.0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- FOOTER BUTTONS ---
            submit = st.form_submit_button("Save Item")
            
            if submit:
                if name and unit != "Select or type to add":
                    c.execute("""INSERT INTO erp_items 
                                 (item_type, name, sku, unit, returnable, dimensions, weight, manufacturer, brand, 
                                 selling_price, sales_account, sales_desc, cost_price, purchase_account, purchase_desc, 
                                 preferred_vendor, inventory_account, opening_stock, stock_rate, reorder_point) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                              (item_type, name, sku, unit, returnable, dimensions, weight, manufacturer, brand,
                               selling_price, sales_account, sales_desc, cost_price, purch_account, purch_desc,
                               preferred_vendor, inv_account, opening_stock, stock_rate, reorder_point))
                    conn.commit()
                    st.success(f"✅ Successfully saved '{name}' to Homzinterio Inventory!")
                else:
                    st.error("⚠️ Please fill in all mandatory fields marked with an asterisk (*).")

        st.markdown('</div>', unsafe_allow_html=True)

elif choice == "🏠 Home":
    st.markdown("<h3 style='color: #181c32; margin-top: 20px;'>Dashboard</h3>", unsafe_allow_html=True)
    st.info("Navigate to the 'Items' menu on the left to see your new Zoho-style Item Creation Form!")

else:
    st.markdown(f"<h3 style='color: #181c32; margin-top: 20px;'>{choice} Module</h3>", unsafe_allow_html=True)
    st.info("This section is under construction.")
