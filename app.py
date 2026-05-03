import streamlit as st
import sqlite3
import pandas as pd

# --- 1. App Configuration ---
st.set_page_config(page_title="Homzinterio Inventory", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

# --- 2. Advanced Zoho-Style Custom CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #f4f5f8; }
    
    /* Hide Header/Footer */
    header {visibility: hidden;}
    .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem;}
    
    /* =========================================
       DARK SIDEBAR STYLING
       ========================================= */
    [data-testid="stSidebar"] {
        background-color: #1e2235 !important;
        border-right: none;
    }
    [data-testid="stSidebar"] * {
        color: #a1a5b7 !important;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    /* Make Radio Buttons look like Zoho Menu Items */
    div.row-widget.stRadio > div { gap: 2px; }
    div.row-widget.stRadio > div > label {
        padding: 10px 15px;
        border-radius: 6px;
        background-color: transparent;
        cursor: pointer;
        transition: 0.2s;
    }
    div.row-widget.stRadio > div > label:hover {
        background-color: #2b3046 !important;
        color: white !important;
    }
    /* Hide the actual radio circle */
    div.row-widget.stRadio > div > label > div:first-child { display: none; }
    
    /* =========================================
       DASHBOARD WIDGET STYLING
       ========================================= */
    .z-card {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #eef0f4;
        padding: 20px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    .z-header {
        display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f1f4; padding-bottom: 10px; margin-bottom: 15px;
    }
    .z-title { font-size: 15px; font-weight: 600; color: #181c32; }
    
    /* Top Selling Cards (Horizontal Flex) */
    .scroll-container { display: flex; gap: 15px; overflow-x: auto; padding-bottom: 10px; }
    .item-card {
        min-width: 160px; background: white; border: 1px solid #eef0f4; border-radius: 8px; padding: 15px; text-align: left;
    }
    .item-img { height: 70px; background: #f8f9fa; border-radius: 6px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; font-size: 24px; color: #b5b5c3; }
    .item-name { font-size: 13px; color: #3f4254; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .item-qty { font-size: 18px; font-weight: 700; color: #181c32; margin-bottom: 5px; }
    .item-growth { font-size: 12px; color: #50cd89; background: #e8fff3; padding: 2px 6px; border-radius: 4px; display: inline-block;}
    
    /* Right Panel List Items */
    .list-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed #f1f1f4; font-size: 13px;}
    .list-item:last-child { border-bottom: none; }
    .list-item-title { color: #5e6278; display: flex; align-items: center; gap: 8px;}
    .list-item-val { color: #181c32; font-weight: 600; }
    .section-lbl { font-size: 12px; font-weight: 700; color: #a1a5b7; margin-top: 15px; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;}
    </style>
""", unsafe_allow_html=True)

# --- 3. Database Setup ---
conn = sqlite3.connect('homzinterio.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT, phone TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS vendors (id INTEGER PRIMARY KEY, company_name TEXT, contact_person TEXT, phone TEXT, gstin TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS materials (id INTEGER PRIMARY KEY, name TEXT, category TEXT, quantity REAL, unit TEXT, vendor TEXT)''')
conn.commit()

# --- 4. Dark Sidebar Navigation ---
st.sidebar.markdown("<h2 style='color: white; margin-bottom: 0;'>🛋️ Homzinterio</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 12px; letter-spacing: 1px; color: #a1a5b7; margin-bottom: 20px;'>INVENTORY OS</p>", unsafe_allow_html=True)

# Main Menu (Simulating Zoho's Sidebar)
menu_options =[
    "🏠 Home", 
    "📦 Items", 
    "🗃️ Inventory", 
    "🛒 Sales", 
    "🛍️ Purchases", 
    "📊 Reports"
]
choice = st.sidebar.radio("Navigation", menu_options, label_visibility="collapsed")

# --- 5. Main Dashboard UI (Zoho Clone) ---

if choice == "🏠 Home":
    # Top Header area
    st.markdown("""
        <div style="padding: 15px 0px;">
            <h2 style="margin: 0; color: #181c32; font-size: 24px;">Hello, Homzinterio Admin</h2>
            <p style="margin: 0; color: #7e8299; font-size: 14px;">Bengaluru Org</p>
        </div>
        <div style="display: flex; gap: 20px; border-bottom: 2px solid #f1f1f4; margin-bottom: 20px;">
            <div style="border-bottom: 3px solid #3e97ff; padding-bottom: 10px; color: #3e97ff; font-weight: 600; cursor: pointer;">Dashboard</div>
            <div style="padding-bottom: 10px; color: #a1a5b7; font-weight: 500; cursor: pointer;">Getting Started</div>
            <div style="padding-bottom: 10px; color: #a1a5b7; font-weight: 500; cursor: pointer;">Recent Updates</div>
        </div>
    """, unsafe_allow_html=True)

    # Dashboard Split Layout (70% Left, 30% Right)
    col_main, col_right = st.columns([7, 3.5])

    with col_main:
        # SECTION 1: TOP SELLING ITEMS (Horizontal Scroll)
        st.markdown("""
        <div class="z-card">
            <div class="z-header">
                <span class="z-title">Top Moving Materials</span>
                <span style="color: #3e97ff; font-size: 13px; cursor: pointer;">This Month ⌄</span>
            </div>
            <div class="scroll-container">
                <div class="item-card">
                    <div class="item-img">🖼️</div>
                    <div class="item-name">18mm Gurjjan Plywood</div>
                    <div class="item-qty">394 Sheets</div>
                    <div class="item-growth">▲ 12%</div>
                </div>
                <div class="item-card">
                    <div class="item-img">🖼️</div>
                    <div class="item-name">Hettich Soft Close Hinges</div>
                    <div class="item-qty">238 Pairs</div>
                    <div class="item-growth">▲ 41%</div>
                </div>
                <div class="item-card">
                    <div class="item-img">🖼️</div>
                    <div class="item-name">Merino Laminate (White)</div>
                    <div class="item-qty">213 Sheets</div>
                    <div class="item-growth">▲ 8%</div>
                </div>
                <div class="item-card">
                    <div class="item-img">🖼️</div>
                    <div class="item-name">Fevicol SH</div>
                    <div class="item-qty">59 Kg</div>
                    <div class="item-growth">▲ 59%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Bottom Half of Main Area (Split into 2)
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            # SECTION 2: TOP STOCKED ITEMS
            st.markdown("""
            <div class="z-card" style="height: 380px;">
                <div class="z-header">
                    <span class="z-title">Top Stocked Items</span>
                    <span style="color: #3e97ff; font-size: 13px; cursor: pointer;">By Quantity ⌄</span>
                </div>
                <div class="list-item">
                    <div class="list-item-title">🖼️ &nbsp; <div style="line-height: 1.2;"><b>Wardrobe Carcass</b><br><span style="font-size:11px; color:#a1a5b7;">SKU: W-001</span></div></div>
                    <div class="list-item-val">528</div>
                </div>
                <div class="list-item">
                    <div class="list-item-title">🖼️ &nbsp; <div style="line-height: 1.2;"><b>Modular Kitchen Unit</b><br><span style="font-size:11px; color:#a1a5b7;">SKU: K-042</span></div></div>
                    <div class="list-item-val">320</div>
                </div>
                <div class="list-item">
                    <div class="list-item-title">🖼️ &nbsp; <div style="line-height: 1.2;"><b>TV Unit Panel</b><br><span style="font-size:11px; color:#a1a5b7;">SKU: T-011</span></div></div>
                    <div class="list-item-val">220</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_m2:
            # SECTION 3: SALES BY CHANNEL
            st.markdown("""
            <div class="z-card" style="height: 380px;">
                <div class="z-header">
                    <span class="z-title">Sales By Source</span>
                    <span style="color: #3e97ff; font-size: 13px; cursor: pointer;">This Month ⌄</span>
                </div>
                <p style="margin:0; font-size: 12px; color: #a1a5b7;">Total Revenue</p>
                <h2 style="margin: 0 0 20px 0; color: #181c32; font-size: 26px;">₹ 24,77,900</h2>
                
                <!-- Progress Bar -->
                <div style="width: 100%; height: 12px; display: flex; border-radius: 6px; overflow: hidden; margin-bottom: 25px;">
                    <div style="width: 85%; background-color: #ff6d00;"></div>
                    <div style="width: 15%; background-color: #3e97ff;"></div>
                </div>
                
                <div class="list-item" style="border:none;">
                    <div class="list-item-title"><div style="width:10px; height:10px; background:#ff6d00; border-radius:2px;"></div> Direct Clients</div>
                    <div class="list-item-val">₹ 21,47,716</div>
                </div>
                <div class="list-item" style="border:none;">
                    <div class="list-item-title"><div style="width:10px; height:10px; background:#3e97ff; border-radius:2px;"></div> Architect Referrals</div>
                    <div class="list-item-val">₹ 3,30,184</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        # SECTION 4: PENDING ACTIONS (Right Sidebar Area)
        st.markdown("""
        <div class="z-card" style="height: 670px;">
            <!-- Tabs -->
            <div style="display: flex; background: #f4f5f8; border-radius: 6px; padding: 4px; margin-bottom: 20px;">
                <div style="flex: 1; text-align: center; background: white; padding: 6px 0; border-radius: 4px; font-size: 13px; font-weight: 600; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">Pending Actions</div>
                <div style="flex: 1; text-align: center; padding: 6px 0; font-size: 13px; color: #7e8299;">Recent Activities</div>
            </div>
            
            <div class="section-lbl">🛒 SALES</div>
            <div class="list-item">
                <div class="list-item-title">› To Be Packed</div>
                <div class="list-item-val">12</div>
            </div>
            <div class="list-item">
                <div class="list-item-title">› To Be Shipped to Site</div>
                <div class="list-item-val">8</div>
            </div>
            <div class="list-item">
                <div class="list-item-title">› To Be Delivered</div>
                <div class="list-item-val">5</div>
            </div>
            <div class="list-item">
                <div class="list-item-title">› To Be Invoiced</div>
                <div class="list-item-val" style="color: #f1416c;">14</div>
            </div>
            
            <div class="section-lbl" style="margin-top: 30px;">🛍️ PURCHASES (VENDORS)</div>
            <div class="list-item">
                <div class="list-item-title">› To Be Received</div>
                <div class="list-item-val">24</div>
            </div>
            <div class="list-item">
                <div class="list-item-title">› Receive In Progress</div>
                <div class="list-item-val">0</div>
            </div>
            
            <div class="section-lbl" style="margin-top: 30px;">🗃️ INVENTORY</div>
            <div class="list-item">
                <div class="list-item-title">› Below Reorder Level</div>
                <div class="list-item-val" style="color: #f1416c;">3</div>
            </div>
            <div class="list-item">
                <div class="list-item-title">› Unconfirmed Items</div>
                <div class="list-item-val">0</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Fallback for other menu items to show the previous working functionality ---
elif choice == "📦 Items":
    st.markdown("<h3 style='color: #181c32;'>Item Management</h3>", unsafe_allow_html=True)
    df = pd.read_sql_query("SELECT * FROM materials", conn)
    st.dataframe(df, use_container_width=True)
else:
    st.markdown(f"<h3 style='color: #181c32;'>{choice} Module</h3>", unsafe_allow_html=True)
    st.info("This module is currently being connected to the new UI.")
