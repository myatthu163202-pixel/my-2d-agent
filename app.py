import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="2D Professional Agent", page_icon="📊")
st.title("📊 2D Professional Agent (Cloud)")

conn = st.connection("gsheets", type=GSheetsConnection)

# ဒေတာဖတ်ရန် (HTTPError မတက်အောင် try-except သုံးထားသည်)
try:
    df = conn.read(worksheet="Sheet1")
except Exception:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

with st.form(key="entry_form"):
    name = st.text_input("Customer Name")
    num = st.number_input("Number", min_value=0, max_value=99, step=1)
    amt = st.number_input("Amount", min_value=100, step=100)
    submit_button = st.form_submit_button(label="Submit")

if submit_button:
    if name:
        new_data = pd.DataFrame([{
            "Customer": name,
            "Number": str(num),
            "Amount": int(amt),
            "Time": datetime.now().strftime("%I:%M %p")
        }])
        updated_df = pd.concat([df, new_data], ignore_index=True)
        # စာရင်းသွင်းရန်
        conn.update(worksheet="Sheet1", data=updated_df)
        st.success(f"Saved: {name}")
        st.rerun()
    else:
        st.error("Please enter a customer name.")

st.subheader("Current Records")
st.dataframe(df)
