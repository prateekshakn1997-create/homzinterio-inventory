import streamlit as st
import sqlite3
import pandas as pd

# --- 1. App Configuration ---
st.set_page_config(page_title="Homzinterio ERP", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

# --- 2. Custom CSS (Zoho-Style Enterprise Look) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f8; }
    header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    
    /* KPI Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff; border: 1px solid #e6e9ed; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    div[data-testid="metric-container"] label { color: #5c6ac4; font-weight: 600; font-size: 14px; }
    
    /* Action Buttons */
    div.stButton > button:first-child {
        background-color: #0052cc; color: white; border-radius: 4px; border: none; padding: 5px 20px; font-weight: 500;
    }
    div.stButton > button:hover { background-color: #0043a6; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] { height: 50px; border-radius: 4px 4px 0px 0px; color: #42526e; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #0052cc; color: #0052cc; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. Database Setup (Expanded for ERP) ---
conn = sqlite3.connect('homzinterio.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT, phone TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS vendors (id INTEGER PRIMARY KEY, company_name TEXT, contact_person TEXT, phone TEXT, gstin TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS materials (id INTEGER PRIMARY KEY, name TEXT, category TEXT, quantity REAL, unit TEXT, vendor TEXT)''')
# New Table for Sales
c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, email TEXT, address TEXT, type TEXT)''')
conn.commit()

def get_data(query):
    return pd.read_sql_query(query, conn)

# --- 4. Sidebar Multi-Level Navigation ---
st.sidebar.markdown("## 🛋️ Homzinterio ERP")
st.sidebar.markdown("<span style='color: #8792a2; font-size: 12px;'>OPERATING SYSTEM</span>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Main Menu
main_menu = st.sidebar.radio("Main Menu",["🏠 Home", "📦 Items", "🗃️ Inventory", "💰 Sales", "🏢 Vendors & Team", "☁️ Data Import"])
st.sidebar.markdown("---")

# Sub Menus logic
sub_menu = ""
if main_menu == "📦 Items":
    sub_menu = st.sidebar.radio("Items Menu", ["Items", "Composite Items", "Price List", "Item Groups"])
elif main_menu == "🗃️ Inventory":
    sub_menu = st.sidebar.radio("Inventory Menu", ["Assemblies", "Inventory Adjustments", "Packages", "Shipments"])
elif main_menu == "💰 Sales":
    sub_menu = st.sidebar.radio("Sales Menu",["Customers", "Sales Orders", "Invoices"])
elif main_menu == "🏢 Vendors & Team":
    sub_menu = st.sidebar.radio("Directory", ["Vendors", "Staff Directory"])

# --- Helper UI Function for Placeholders ---
def coming_soon_ui(title, description):
    st.markdown(f"### {title}")
    st.markdown(f"<div style='background-color: white; padding: 40px; text-align: center; border-radius: 8px; border: 1px dashed #c1c7d0; margin-top: 20px;'>"
                f"<h4 style='color: #42526e;'>🚀 {title} Module</h4>"
                f"<p style='color: #7a869a;'>{description}</p>"
                f"<p style='color: #0052cc; font-size: 14px;'>Currently in development for Homzinterio.</p>"
                f"</div>", unsafe_allow_html=True)

# ==========================================
#               ROUTING LOGIC
# ==========================================

# --- HOME ---
if main_menu == "🏠 Home":
    st.markdown("### Dashboard")
    mat_count = get_data("SELECT COUNT(*) FROM materials").iloc[0,0]
    cust_count = get_data("SELECT COUNT(*) FROM customers").iloc[0,0]
    total_qty = get_data("SELECT SUM(quantity) FROM materials").iloc[0,0] or 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items in Stock", f"{mat_count}")
    col2.metric("Total Material Quantity", f"{total_qty:,.0f}")
    col3.metric("Registered Customers", f"{cust_count}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Recent Inventory Additions**")
    recent_df = get_data("SELECT name as 'Item', category as 'Category', quantity as 'Qty' FROM materials ORDER BY id DESC LIMIT 5")
    if not recent_df.empty:
        st.dataframe(recent_df, use_container_width=True, hide_index=True)

# --- ITEMS ---
elif main_menu == "📦 Items":
    if sub_menu == "Items":
        st.markdown("### Items & Materials")
        tab1, tab2 = st.tabs(["📄 All Items", "➕ New Item"])
        with tab1:
            df = get_data("SELECT id as 'ID', name as 'Item Name', category as 'Category', quantity as 'Stock', unit as 'Unit', vendor as 'Vendor' FROM materials")
            st.dataframe(df, use_container_width=True, hide_index=True)
        with tab2:
            st.markdown("<div style='background-color: white; padding: 25px; border-radius: 8px; border: 1px solid #e6e9ed;'>", unsafe_allow_html=True)
            vendors = [row[0] for row in c.execute("SELECT company_name FROM vendors").fetchall()]
            with st.form("add_item_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                name = c1.text_input("Item Name *")
                category = c2.selectbox("Category *",["Plywood", "Laminates", "Hardware", "Paint", "Adhesives", "Electrical", "Plumbing", "Other"])
                c3, c4 = st.columns(2)
                qty = c3.number_input("Opening Stock", min_value=0.0, step=1.0)
                unit = c4.selectbox("Unit",["Sheets", "Sq.ft", "Pieces", "Boxes", "Kg", "Liters", "Running Ft"])
                vendor = st.selectbox("Preferred Vendor", vendors) if vendors else st.text_input("Preferred Vendor")
                if st.form_submit_button("Save Item"):
                    c.execute("INSERT INTO materials (name, category, quantity, unit, vendor) VALUES (?, ?, ?, ?, ?)", (name, category, qty, unit, vendor))
                    conn.commit()
                    st.success(f"Item '{name}' saved successfully!")
            st.markdown("</div>", unsafe_allow_html=True)
            
    elif sub_menu == "Composite Items":
        coming_soon_ui("Composite Items", "Bundle multiple raw materials (e.g., Plywood + Laminate + Fevicol) into a single final unit like 'Wardrobe Door'.")
    elif sub_menu == "Price List":
        coming_soon_ui("Price List", "Manage custom pricing structures for different clients or wholesale vs retail.")
    elif sub_menu == "Item Groups":
        coming_soon_ui("Item Groups", "Group variations of the same item (e.g., 18mm Plywood in different wood grains).")

# --- INVENTORY ---
elif main_menu == "🗃️ Inventory":
    if sub_menu == "Assemblies":
        coming_soon_ui("Assemblies", "Track the process of converting raw items (Wood, Hardware) into finished goods (Cabinets).")
    elif sub_menu == "Inventory Adjustments":
        coming_soon_ui("Inventory Adjustments", "Adjust stock levels for damage, theft, or physical counting discrepancies.")
    elif sub_menu == "Packages":
        coming_soon_ui("Packages", "Group finished items together for shipping to the interior project site.")
    elif sub_menu == "Shipments":
        coming_soon_ui("Shipments", "Track delivery of materials from your warehouse to the client's home/project site.")

# --- SALES ---
elif main_menu == "💰 Sales":
    if sub_menu == "Customers":
        st.markdown("### Customers & Clients")
        tab1, tab2 = st.tabs(["📄 Customer List", "➕ Add Customer"])
        with tab1:
            df = get_data("SELECT name as 'Client Name', phone as 'Phone', email as 'Email', type as 'Project Type' FROM customers")
            st.dataframe(df, use_container_width=True, hide_index=True)
        with tab2:
            st.markdown("<div style='background-color: white; padding: 25px; border-radius: 8px; border: 1px solid #e6e9ed;'>", unsafe_allow_html=True)
            with st.form("customer_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                name = c1.text_input("Customer / Project Name *")
                proj_type = c2.selectbox("Project Type",["Residential (2BHK/3BHK)", "Commercial", "Renovation", "Individual Furniture"])
                phone = c1.text_input("Phone Number")
                email = c2.text_input("Email ID")
                address = st.text_area("Site Address")
                if st.form_submit_button("Save Customer"):
                    if name:
                        c.execute("INSERT INTO customers (name, phone, email, address, type) VALUES (?, ?, ?, ?, ?)", (name, phone, email, address, proj_type))
                        conn.commit()
                        st.success(f"Customer '{name}' added successfully!")
                    else:
                        st.error("Customer Name is required.")
            st.markdown("</div>", unsafe_allow_html=True)
            
    elif sub_menu == "Sales Orders":
        coming_soon_ui("Sales Orders", "Draft contracts and orders for clients detailing the interior work to be done.")
    elif sub_menu == "Invoices":
        coming_soon_ui("Invoices", "Generate GST-compliant invoices and track payments from your customers.")

# --- VENDORS & TEAM ---
elif main_menu == "🏢 Vendors & Team":
    if sub_menu == "Vendors":
        st.markdown("### Vendors")
        with st.form("vendor_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            company = c1.text_input("Company Name")
            person = c2.text_input("Contact Person")
            if st.form_submit_button("Save Vendor"):
                c.execute("INSERT INTO vendors (company_name, contact_person, phone, gstin) VALUES (?, ?, '', '')", (company, person))
                conn.commit()
                st.success("Vendor saved!")
        st.dataframe(get_data("SELECT company_name as 'Company Name', contact_person as 'Contact' FROM vendors"), use_container_width=True, hide_index=True)
        
    elif sub_menu == "Staff Directory":
        st.markdown("### Team Directory")
        with st.form("staff_form", clear_on_submit=True):
            name = st.text_input("Employee Name")
            role = st.selectbox("Role",["Site Supervisor", "Lead Designer", "Carpenter", "Manager"])
            if st.form_submit_button("Save Details"):
                c.execute("INSERT INTO users (name, role, phone) VALUES (?, ?, '')", (name, role))
                conn.commit()
                st.success("Staff profile created!")
        st.dataframe(get_data("SELECT name as 'Name', role as 'Role' FROM users"), use_container_width=True, hide_index=True)

# --- DATA IMPORT ---
elif main_menu == "☁️ Data Import":
    st.markdown("### Import Data")
    uploaded_file = st.file_uploader("Upload Excel/CSV for Materials", type=["xlsx", "csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.dataframe(df.head(), use_container_width=True)
            if st.button("Start Import"):
                df.columns = df.columns.str.lower()
                if all(col in df.columns for col in['name', 'category', 'quantity', 'unit', 'vendor']):
                    for _, row in df.iterrows():
                        c.execute("INSERT INTO materials (name, category, quantity, unit, vendor) VALUES (?, ?, ?, ?, ?)",
                                  (str(row['name']), str(row['category']), float(row['quantity']), str(row['unit']), str(row['vendor'])))
                    conn.commit()
                    st.success("✅ Items imported!")
                else:
                    st.error("Format mismatch! Missing columns.")
        except Exception as e:
            st.error(f"Error: {e}")
