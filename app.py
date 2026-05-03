%%app.py
import streamlit as st
import sqlite3
import pandas as pd

# --- Database Setup ---
conn = sqlite3.connect('homzinterio.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT, phone TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS vendors (id INTEGER PRIMARY KEY, company_name TEXT, contact_person TEXT, phone TEXT, gstin TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS materials (id INTEGER PRIMARY KEY, name TEXT, category TEXT, quantity REAL, unit TEXT, vendor TEXT)''')
conn.commit()

# --- App Configuration & UI ---
st.set_page_config(page_title="Homzinterio Inventory", page_icon="🛋️", layout="wide")

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #2c3e50;}
    .stMetric {background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    </style>
""", unsafe_allow_html=True)

st.title("🛋️ Homzinterio Inventory Portal")
st.markdown("---")

# --- Sidebar Navigation ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1944/1944364.png", width=100)
st.sidebar.title("Navigation")
menu =["📊 Dashboard", "📦 Manage Materials", "🏢 Vendors", "👥 Staff Directory", "📂 Bulk Excel Upload"]
choice = st.sidebar.radio("Go to", menu)

# --- 1. Dashboard ---
if choice == "📊 Dashboard":
    st.subheader("Overview")
    
    # KPIs
    mat_count = pd.read_sql_query("SELECT COUNT(*) FROM materials", conn).iloc[0,0]
    ven_count = pd.read_sql_query("SELECT COUNT(*) FROM vendors", conn).iloc[0,0]
    user_count = pd.read_sql_query("SELECT COUNT(*) FROM users", conn).iloc[0,0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Materials in Stock", mat_count)
    col2.metric("Registered Vendors", ven_count)
    col3.metric("Active Staff", user_count)
    
    st.markdown("### Current Inventory")
    materials_df = pd.read_sql_query("SELECT name as 'Material', category as 'Category', quantity as 'Qty', unit as 'Unit', vendor as 'Vendor' FROM materials", conn)
    if not materials_df.empty:
        st.dataframe(materials_df, use_container_width=True, hide_index=True)
    else:
        st.info("No materials found. Go to 'Bulk Excel Upload' to add your raw sheet.")

# --- 2. Manage Materials ---
elif choice == "📦 Manage Materials":
    st.subheader("Add Single Material")
    vendors = [row[0] for row in c.execute("SELECT company_name FROM vendors").fetchall()]
    
    with st.form("material_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Material Name")
        category = col2.selectbox("Category",["Plywood", "Laminates", "Hardware", "Paint", "Adhesives", "Electrical", "Other"])
        qty = col1.number_input("Quantity", min_value=0.0, step=1.0)
        unit = col2.selectbox("Unit",["Sheets", "Sq.ft", "Pieces", "Kg", "Liters", "Boxes"])
        vendor = st.selectbox("Vendor", vendors) if vendors else st.text_input("Vendor Name")
        
        if st.form_submit_button("Add to Stock"):
            if name:
                c.execute("INSERT INTO materials (name, category, quantity, unit, vendor) VALUES (?, ?, ?, ?, ?)", (name, category, qty, unit, vendor))
                conn.commit()
                st.success(f"Added {name}!")
            else:
                st.error("Material name is required.")

# --- 3. Bulk Excel Upload ---
elif choice == "📂 Bulk Excel Upload":
    st.subheader("Upload Raw Excel Sheet")
    st.info("⚠️ Your Excel file MUST have these exact columns: **Name, Category, Quantity, Unit, Vendor**")
    
    uploaded_file = st.file_uploader("Choose an Excel file (.xlsx) or CSV", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("Data Preview:")
            st.dataframe(df.head())
            
            if st.button("Upload to Database"):
                # Clean column names to lowercase to match logic
                df.columns = df.columns.str.lower()
                expected_cols = ['name', 'category', 'quantity', 'unit', 'vendor']
                
                if all(col in df.columns for col in expected_cols):
                    count = 0
                    for index, row in df.iterrows():
                        c.execute("INSERT INTO materials (name, category, quantity, unit, vendor) VALUES (?, ?, ?, ?, ?)",
                                  (str(row['name']), str(row['category']), float(row['quantity']), str(row['unit']), str(row['vendor'])))
                        count += 1
                    conn.commit()
                    st.success(f"✅ Successfully added {count} materials to the inventory!")
                else:
                    st.error(f"Missing columns! Ensure your sheet has: {', '.join(expected_cols)}")
        except Exception as e:
            st.error(f"Error reading file: {e}")

# --- 4. Add Vendors & Users (Combined for brevity) ---
elif choice == "🏢 Vendors":
    st.subheader("Manage Vendors")
    with st.form("vendor_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        company = c1.text_input("Company Name")
        person = c2.text_input("Contact Person")
        phone = c1.text_input("Phone Number")
        gstin = c2.text_input("GSTIN Number")
        if st.form_submit_button("Save Vendor"):
            c.execute("INSERT INTO vendors (company_name, contact_person, phone, gstin) VALUES (?, ?, ?, ?)", (company, person, phone, gstin))
            conn.commit()
            st.success("Vendor saved!")
    st.dataframe(pd.read_sql_query("SELECT * FROM vendors", conn), use_container_width=True, hide_index=True)

elif choice == "👥 Staff Directory":
    st.subheader("Homzinterio Team")
    with st.form("user_form", clear_on_submit=True):
        name = st.text_input("Employee Name")
        role = st.selectbox("Role", ["Admin", "Site Supervisor", "Designer", "Carpenter", "Manager"])
        phone = st.text_input("Phone Number")
        if st.form_submit_button("Add Team Member"):
            c.execute("INSERT INTO users (name, role, phone) VALUES (?, ?, ?)", (name, role, phone))
            conn.commit()
            st.success("Team member added!")
    st.dataframe(pd.read_sql_query("SELECT * FROM users", conn), use_container_width=True, hide_index=True)
