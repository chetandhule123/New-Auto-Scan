import streamlit as st
import threading
import time
from datetime import datetime, timedelta
import pandas as pd
from stock_scanner import StockScanner
from data_manager import DataManager

# Initialize session state
if 'scanner_initialized' not in st.session_state:
    st.session_state.scanner_initialized = False
    st.session_state.data_manager = DataManager()
    st.session_state.scanner = StockScanner(st.session_state.data_manager)

# Initialize background scanner on first run
if not st.session_state.scanner_initialized:
    st.session_state.scanner.start_background_scanning()
    st.session_state.scanner_initialized = True

# Page configuration
st.set_page_config(
    page_title="Enhanced NSE Stock Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("📈 Enhanced NSE Stock Screener")
st.markdown("*Continuous server-side scanning every 15 minutes*")

# Create columns for layout
col1, col2, col3 = st.columns([2, 1, 1])

# Status indicators
with col1:
    data_manager = st.session_state.data_manager
    last_scan = data_manager.get_last_scan_time()
    next_scan = data_manager.get_next_scan_time()
    
    if last_scan:
        st.success(f"🟢 Scanner Active - Last scan: {last_scan.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("🔄 Scanner starting...")

with col2:
    if next_scan:
        time_to_next = next_scan - datetime.now()
        if time_to_next.total_seconds() > 0:
            minutes_left = int(time_to_next.total_seconds() / 60)
            st.info(f"⏰ Next scan in: {minutes_left} min")
        else:
            st.info("⏰ Scanning now...")

with col3:
    if st.button("🔄 Manual Refresh", type="primary"):
        st.session_state.scanner.trigger_manual_scan()
        st.rerun()

# Sidebar for filters and settings
st.sidebar.header("📊 Scanner Settings")

# Connection status
scanner_status = st.session_state.scanner.get_status()
if scanner_status['running']:
    st.sidebar.success("🟢 Background Scanner: Active")
else:
    st.sidebar.error("🔴 Background Scanner: Inactive")

st.sidebar.metric("Total Scans", scanner_status['total_scans'])
st.sidebar.metric("Scan Interval", "15 minutes")

# Filter options
st.sidebar.subheader("🔍 Filters")
market_cap_filter = st.sidebar.selectbox(
    "Market Cap",
    ["All", "Large Cap", "Mid Cap", "Small Cap"],
    index=0
)

sector_filter = st.sidebar.selectbox(
    "Sector",
    ["All", "Banking", "IT", "Pharma", "Auto", "FMCG", "Energy"],
    index=0
)

price_range = st.sidebar.slider(
    "Price Range (₹)",
    min_value=0,
    max_value=10000,
    value=(0, 10000),
    step=100
)

# Main content area
st.header("📋 Current Scan Results")

# Get latest scan data
scan_data = data_manager.get_latest_scan_data()

if scan_data is not None and not scan_data.empty:
    # Apply filters
    filtered_data = scan_data.copy()
    
    if market_cap_filter != "All":
        filtered_data = filtered_data[filtered_data['market_cap'] == market_cap_filter]
    
    if sector_filter != "All":
        filtered_data = filtered_data[filtered_data['sector'] == sector_filter]
    
    # Apply price range filter
    filtered_data = filtered_data[
        (filtered_data['price'] >= price_range[0]) & 
        (filtered_data['price'] <= price_range[1])
    ]
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Stocks", len(filtered_data))
    
    with col2:
        if len(filtered_data) > 0:
            gainers = len(filtered_data[filtered_data['change_percent'] > 0])
            st.metric("Gainers", gainers)
        else:
            st.metric("Gainers", 0)
    
    with col3:
        if len(filtered_data) > 0:
            losers = len(filtered_data[filtered_data['change_percent'] < 0])
            st.metric("Losers", losers)
        else:
            st.metric("Losers", 0)
    
    with col4:
        if len(filtered_data) > 0:
            avg_volume = filtered_data['volume'].mean()
            st.metric("Avg Volume", f"{avg_volume:,.0f}")
        else:
            st.metric("Avg Volume", 0)
    
    # Display data table
    if len(filtered_data) > 0:
        st.subheader("🔍 Filtered Results")
        
        # Format the dataframe for display
        display_df = filtered_data.copy()
        display_df['change_percent'] = display_df['change_percent'].round(2)
        display_df['price'] = display_df['price'].round(2)
        display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,.0f}")
        
        # Color coding for change percentage
        def color_change(val):
            if val > 0:
                return 'color: green'
            elif val < 0:
                return 'color: red'
            else:
                return 'color: black'
        
        styled_df = display_df.style.applymap(color_change, subset=['change_percent'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "symbol": "Symbol",
                "name": "Company Name",
                "price": "Price (₹)",
                "change_percent": "Change %",
                "volume": "Volume",
                "market_cap": "Market Cap",
                "sector": "Sector",
                "scan_time": "Scan Time"
            }
        )
    else:
        st.info("No stocks match the current filters.")
        
else:
    st.info("🔄 Waiting for scan data... The background scanner is running and will provide results shortly.")

# Scan history
st.header("📈 Scan History")
scan_history = data_manager.get_scan_history()

if scan_history:
    history_df = pd.DataFrame(scan_history)
    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "scan_time": "Scan Time",
            "total_stocks": "Total Stocks",
            "gainers": "Gainers",
            "losers": "Losers",
            "status": "Status"
        }
    )
else:
    st.info("No scan history available yet.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    Enhanced NSE Stock Screener - Continuous background scanning ensures data is always up-to-date
    </div>
    """,
    unsafe_allow_html=True
)

# Auto-refresh the page every 30 seconds to show updated data
time.sleep(1)  # Small delay to prevent excessive CPU usage
st.rerun()
