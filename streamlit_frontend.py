import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time

# --- CONFIGURATION ---
# 1. USER VM (Consultants & Hours)
API_URL = "http://48.222.8.224:5000" 

# 2. ADMIN VM (The Report Trigger)
TRIGGER_URL = "http://20.123.92.154:5000" 
# ---------------------

st.set_page_config(page_title="CONTI", layout="wide")

# === CUSTOM STYLING START ===
st.markdown("""
    <style>
        /* Main Backgrounds */
        .stApp {
            background-color: #1e2a38;
        }
        [data-testid="stSidebar"] {
            background-color: #3a5068;
        }

        /* Global Text */
        h1, h2, h3 {
            color: #92d0c1 !important;
        }
        p, label, span, div {
            color: #f5f7fa !important;
        }

        /* Buttons (Standard & Form Submit) */
        .stButton > button, [data-testid="stFormSubmitButton"] > button {
            background-color: #92d0c1 !important;
            color: #1e2a38 !important;
            font-weight: bold;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
            background-color: #7ab8a8 !important;
            color: #1e2a38 !important;
            box-shadow: 0px 4px 15px rgba(146, 208, 193, 0.4);
        }

        /* Inputs (Text, Number, Date, Time) */
        div[data-baseweb="input"], div[data-baseweb="base-input"] {
            background-color: #151e29 !important;
            border: 1px solid #3a5068 !important;
            border-radius: 5px;
        }
        input {
            color: #f5f7fa !important;
        }

        /* Radio Buttons & Checkboxes */
        [data-testid="stRadio"] label, [data-testid="stCheckbox"] label {
            color: #f5f7fa !important;
        }
        /* Force specific background for radio/checkbox containers if needed */
        [data-testid="stRadio"] > div {
            background-color: transparent !important;
        }

        /* Dataframes & Tables */
        [data-testid="stDataFrame"] {
            border: 1px solid #3a5068;
        }

        /* Form Containers */
        [data-testid="stForm"] {
            background-color: #243447;
            border: 1px solid #3a5068;
            padding: 20px;
            border-radius: 10px;
        }

        /* Alerts/Info Boxes */
        .stAlert {
            background-color: #2b3b4e;
            border: 1px solid #92d0c1;
        }
    </style>
""", unsafe_allow_html=True)
# === CUSTOM STYLING END ===

st.title("CONTI")

# Sidebar for Navigation
menu = st.sidebar.radio("Navigate", ["Consultants", "Hours Log", "Reports"])


# === PAGE 1: CONSULTANTS ===

if menu == "Consultants":
    st.header("Manage Consultants")
    st.info(f"Connected to Remote Engine: {API_URL}")

    # --- Section: View Consultants (GET) ---
    st.subheader("Current Consultants")
    if st.button("Refresh List"):
        try:
            response = requests.get(f"{API_URL}/consultants")
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No consultants found.")
            else:
                st.error("Failed to fetch data.")
        except Exception as e:
            st.error(f"Connection Error: {e}")

    st.divider()

    # --- Section: Add Consultant (POST) ---
    st.subheader("Add New Consultant")
    with st.form("add_consultant_form"):
        new_name = st.text_input("Consultant Name")
        submitted = st.form_submit_button("Add Consultant")
        
        if submitted and new_name:
            payload = {"consultant_name": new_name}
            try:
                res = requests.post(f"{API_URL}/consultants", json=payload)
                if res.status_code == 201:
                    st.success(f"Added {new_name} successfully!")
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# === PAGE 2: HOURS LOG ===

elif menu == "Hours Log":
    st.header("Hours Tracking")
    st.info(f"Connected to Remote Engine: {API_URL}")

    # --- Section: View Hours (GET) ---
    st.subheader("View Logged Hours")
    if st.button("Load Hours"):
        try:
            response = requests.get(f"{API_URL}/hours")
            if response.status_code == 200:
                data = response.json()
                st.dataframe(pd.DataFrame(data), use_container_width=True)
            else:
                st.error("Failed to fetch hours.")
        except Exception as e:
            st.error(f"Connection Error: {e}")

    st.divider()

    # --- Section: Add Hours (POST) ---
    st.subheader("Log Work Hours")
    
    # We need a form to handle the inputs
    with st.form("add_hours_form"):
        c_id = st.number_input("Consultant ID", min_value=1, step=1)
        customer = st.text_input("Customer Name")
        lunch = st.checkbox("Lunch Break Taken?", value=True)
        
        # Date & Time Pickers
        col1, col2 = st.columns(2)
        with col1:
            date_val = st.date_input("Date", datetime.today())
            start_t = st.time_input("Start Time", time(8, 0))
        with col2:
            # End date usually same as start, but good to handle
            end_t = st.time_input("End Time", time(16, 0))

        submit_hours = st.form_submit_button("Submit Hours")

        if submit_hours:
            # 1. Format Datetime for Flask (YYYY-MM-DD HH:MM:SS)
            start_str = f"{date_val} {start_t}"
            end_str = f"{date_val} {end_t}"

            # 2. Build Payload
            payload = {
                "consultant_id": c_id,
                "starttime": start_str,
                "endtime": end_str,
                "lunchbreak": lunch,
                "customername": customer
            }

            # 3. Send Request
            try:
                res = requests.post(f"{API_URL}/hours", json=payload)
                if res.status_code == 201:
                    st.success("Hours logged successfully!")
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    st.divider()

    # --- Section: Update Hours (PUT) ---
    st.subheader("Update Existing Log")
    st.caption("Enter the ID of the record you want to modify.")
    
    with st.form("update_hours_form"):
        # We need the ID to put in the URL
        row_id = st.number_input("Enter Record ID to Update", min_value=1, step=1)
        
        st.write("New Details:")
        u_customer = st.text_input("New Customer Name")
        u_lunch = st.checkbox("New Lunch Status", value=True)
        
        col1, col2 = st.columns(2)
        with col1:
            u_date = st.date_input("New Date", datetime.today(), key="u_date")
            u_start = st.time_input("New Start", time(8, 0), key="u_start")
        with col2:
            u_end = st.time_input("New End", time(16, 0), key="u_end")

        update_submitted = st.form_submit_button("Update Record")

        if update_submitted:
            # 1. Format String
            u_start_str = f"{u_date} {u_start}"
            u_end_str   = f"{u_date} {u_end}"
            
            # 2. Build Payload (Notice: No consultant_id is sent, per your JSON spec)
            payload = {
                "starttime": u_start_str,
                "endtime": u_end_str,
                "lunchbreak": u_lunch,
                "customername": u_customer
            }
            
            # 3. Send PUT Request to /hours/ID
            try:
                # The ID goes in the URL: f"{API_URL}/hours/{row_id}"
                res = requests.put(f"{API_URL}/hours/{row_id}", json=payload)
                
                if res.status_code == 200:
                    st.success(f"Record {row_id} updated successfully!")
                elif res.status_code == 404:
                    st.error(f"Error: Record ID {row_id} not found.")
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")


# === PAGE 3: REPORTS (Remote VM) ===

elif menu == "Reports":
    st.header("Report Generation System")
    st.info(f"Connected to Remote Engine: {TRIGGER_URL}")

    st.write("Click below to trigger the manual report generation process on the remote VM.")
    
    if st.button("Trigger Report Generation"):
        with st.spinner("Talking to remote server..."):
            try:
                # Assuming no payload is needed based on your Flask code, 
                # but sending empty dict {} just in case.
                res = requests.post(f"{TRIGGER_URL}/trigger-report", json={})
                
                if res.status_code == 200:
                    st.success("Report generated and uploaded!")
                    st.json(res.json())
                else:
                    st.error(f"Remote Server Error: {res.text}")
            except Exception as e:
                st.error(f"Could not connect to Remote VM: {e}")