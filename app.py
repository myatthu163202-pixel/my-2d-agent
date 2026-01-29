import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="2D Professional Agent", page_icon="📊")
st.title("📊 2D Professional Agent (Cloud)")

# Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Read existing data
try:
    df = conn.read(worksheet="Sheet1")
except Exception:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# Input Form
with st.form(key="entry_form"):
    name = st.text_input("Customer Name")
    num = st.number_input("Number", min_value=0, max_value=99, step=1)
    amt = st.number_input("Amount", min_value=100, step=100)
    submit_button = st.form_submit_button(label="Submit")

if submit_button:
    if name:
        # Create new entry
        new_data = pd.DataFrame([{
            "Customer": name,
            "Number": str(num),
            "Amount": int(amt),
            "Time": datetime.now().strftime("%I:%M %p")
        }])
        
        # Combine and Update
        updated_df = pd.concat([df, new_data], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_df)
        
        st.success(f"Saved: {name} - {num} - {amt}")
        st.balloons()
        st.rerun()
    else:
        st.error("Please enter a customer name.")

# Display Data
st.subheader("Current Records")
st.dataframe(df)
