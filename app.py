import streamlit as st
import sqlite3
import pandas as pd

# --- 1. App Configuration ---
st.set_page_config(page_title="Homzinterio Inventory", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

# --- 2. Custom CSS (The Zoho Look) ---
st.markdown("""
    <style>
    /* Zoho-style background */
    .stApp { background-color: #f4f6f8; }
    
    /* Clean up the header/footer */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    
    /* Zoho Style KPI Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e6e9ed;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    div[data-testid="metric-container"] label {
        color: #5c6ac4;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Zoho Style Action Buttons (Blue) */
    div.stButton > button:first-child {
        background-color: #0052cc;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 10px 24px;
        font-weight: 500;
    }
    div.stButton > button:hover {
        background-color: #0043a6;
        color: white;
    }
    
    /* Tabs Styling */
    .stTabs[data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #42526e;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #0052cc;
        color: #0052cc;
        font-weight: bold;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e6e9ed;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. Database Setup ---
conn = sqlite3.connect('homzinterio.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT, phone TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS vendors (id INTEGER PRIMARY KEY, company_name TEXT, contact_person TEXT, phone TEXT, gstin TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS materials (id INTEGER PRIMARY KEY, name TEXT, category TEXT, quantity REAL, unit TEXT, vendor TEXT)''')
conn.commit()

# --- 4. Sidebar Navigation ---
st.sidebar.markdown("## 🛋️ Homzinterio")
st.sidebar.markdown("<span style='color: #8792a2; font-size: 12px;'>INVENTORY SYSTEM</span>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu =["📊 Dashboard", "📦 Items & Materials", "🏢 Vendors", "👥 Team Directory", "☁️ Data Import"]
choice = st.sidebar.radio("Main Menu", menu, label_visibility="collapsed")

# --- Helper Functions ---
def get_data(query):
    return pd.read_sql_query(query, conn)

# --- 5. Application Views ---

if choice == "📊 Dashboard":
    st.markdown("### Dashboard")
    st.markdown("<p style='color: #6b778c; margin-top: -15px;'>Overview of your interior stock & suppliers.</p>", unsafe_allow_html=True)
    
    # KPIs
    mat_count = get_data("SELECT COUNT(*) FROM materials").iloc[0,0]
    ven_count = get_data("SELECT COUNT(*) FROM vendors").iloc[0,0]
    total_qty = get_data("SELECT SUM(quantity) FROM materials").iloc[0,0] or 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items (SKUs)", f"{mat_count}")
    col2.metric("Total Stock Quantity", f"{total_qty:,.0f}")
    col3.metric("Active Vendors", f"{ven_count}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts and Tables View
    col_chart, col_table = st.columns([1, 1.5])
    
    with col_chart:
        st.markdown("**Stock by Category**")
        cat_df = get_data("SELECT category, SUM(quantity) as quantity FROM materials GROUP BY category")
        if not cat_df.empty:
            cat_df.set_index('category', inplace=True)
            st.bar_chart(cat_df, color="#0052cc")
        else:
            st.info("Not enough data for chart.")
            
    with col_table:
        st.markdown("**Recently Added Items**")
        recent_df = get_data("SELECT name as 'Item Name', category as 'Category', quantity as 'Qty' FROM materials ORDER BY id DESC LIMIT 6")
        if not recent_df.empty:
            st.dataframe(recent_df, use_container_width=True, hide_index=True)
        else:
            st.info("No items in inventory.")

elif choice == "📦 Items & Materials":
    st.markdown("### Items & Materials")
    tab1, tab2 = st.tabs(["📄 All Items", "➕ New Item"])
    
    with tab1:
        df = get_data("SELECT id as 'ID', name as 'Item Name', category as 'Category', quantity as 'Stock on Hand', unit as 'Unit', vendor as 'Preferred Vendor' FROM materials")
        if df.empty:
            st.info("No items found. Add a new item in the next tab.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
            
    with tab2:
        st.markdown("<div style='background-color: white; padding: 25px; border-radius: 8px; border: 1px solid #e6e9ed;'>", unsafe_allow_html=True)
        vendors = [row[0] for row in c.execute("SELECT company_name FROM vendors").fetchall()]
        
        with st.form("add_item_form", clear_on_submit=True):
            st.markdown("##### Basic Item Details")
            c1, c2 = st.columns(2)
            name = c1.text_input("Item Name *")
            category = c2.selectbox("Category *",["Plywood", "Laminates", "Hardware", "Paint", "Adhesives", "Electrical", "Plumbing", "Other"])
            
            st.markdown("##### Stock Details")
            c3, c4 = st.columns(2)
            qty = c3.number_input("Opening Stock", min_value=0.0, step=1.0)
            unit = c4.selectbox("Unit",["Sheets", "Sq.ft", "Pieces", "Boxes", "Kg", "Liters", "Running Ft"])
            
            vendor = st.selectbox("Preferred Vendor", vendors) if vendors else st.text_input("Preferred Vendor")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Save Item"):
                if name:
                    c.execute("INSERT INTO materials (name, category, quantity, unit, vendor) VALUES (?, ?, ?, ?, ?)", (name, category, qty, unit, vendor))
                    conn.commit()
                    st.success(f"Item '{name}' saved successfully!")
                else:
                    st.error("Item Name is required.")
        st.markdown("</div>", unsafe_allow_html=True)

elif choice == "🏢 Vendors":
    st.markdown("### Vendors")
    tab1, tab2 = st.tabs(["📄 Vendor List", "➕ Add Vendor"])
    
    with tab1:
        df = get_data("SELECT company_name as 'Company Name', contact_person as 'Contact Person', phone as 'Phone', gstin as 'GSTIN' FROM vendors")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    with tab2:
        with st.form("vendor_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            company = c1.text_input("Company/Business Name *")
            person = c2.text_input("Primary Contact Person")
            phone = c1.text_input("Phone Number")
            gstin = c2.text_input("GSTIN Number (for billing)")
            
            if st.form_submit_button("Save Vendor"):
                if company:
                    c.execute("INSERT INTO vendors (company_name, contact_person, phone, gstin) VALUES (?, ?, ?, ?)", (company, person, phone, gstin))
                    conn.commit()
                    st.success("Vendor added successfully!")
                else:
                    st.error("Company Name is required.")

elif choice == "👥 Team Directory":
    st.markdown("### Team Directory")
    tab1, tab2 = st.tabs(["📄 Staff List", "➕ Add Staff"])
    
    with tab1:
        df = get_data("SELECT name as 'Name', role as 'Role', phone as 'Phone' FROM users")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    with tab2:
        with st.form("staff_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Employee Name *")
            role = c2.selectbox("Role",["Admin", "Site Supervisor", "Lead Designer", "Draftsman", "Carpenter", "Manager"])
            phone = c1.text_input("Phone Number")
            if st.form_submit_button("Save Details"):
                if name:
                    c.execute("INSERT INTO users (name, role, phone) VALUES (?, ?, ?)", (name, role, phone))
                    conn.commit()
                    st.success("Staff profile created!")
                else:
                    st.error("Employee Name is required.")

elif choice == "☁️ Data Import":
    st.markdown("### Import Data")
    st.markdown("Upload bulk inventory records via Excel or CSV.")
    
    st.info("💡 Make sure your columns are exactly: **Name**, **Category**, **Quantity**, **Unit**, **Vendor**")
    
    uploaded_file = st.file_uploader("Drop your Excel/CSV file here", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
                
            st.markdown("**Preview:**")
            st.dataframe(df.head(), use_container_width=True)
            
            if st.button("Start Import Process"):
                df.columns = df.columns.str.lower()
                expected_cols =['name', 'category', 'quantity', 'unit', 'vendor']
                
                if all(col in df.columns for col in expected_cols):
                    for index, row in df.iterrows():
                        c.execute("INSERT INTO materials (name, category, quantity, unit, vendor) VALUES (?, ?, ?, ?, ?)",
                                  (str(row['name']), str(row['category']), float(row['quantity']), str(row['unit']), str(row['vendor'])))
                    conn.commit()
                    st.success(f"✅ Successfully imported {len(df)} items!")
                else:
                    st.error(f"Format mismatch! Your file must have these headers: {', '.join(expected_cols)}")
        except Exception as e:
            st.error(f"Error processing file: {e}")
