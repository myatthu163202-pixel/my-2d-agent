import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Professional Agent", page_icon="📊")
st.title("📊 2D Professional Agent")

# Secrets ထဲက Link ကို ယူမယ်
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
# Link ကို CSV format ပြောင်းမယ် (ဒေတာဖတ်ဖို့)
csv_url = sheet_url.replace('/edit', '/export?format=csv')

# ဒေတာဖတ်ခြင်း
try:
    df = pd.read_csv(csv_url)
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# Input Form
with st.form(key="entry_form"):
    name = st.text_input("Customer Name")
    num = st.number_input("Number", min_value=0, max_value=99, step=1)
    amt = st.number_input("Amount", min_value=100, step=100)
    submit_button = st.form_submit_button(label="Submit")

if submit_button:
    if name:
        # ဒေတာအသစ်
        new_data = {
            "Customer": name,
            "Number": str(num),
            "Amount": int(amt),
            "Time": datetime.now().strftime("%I:%M %p")
        }
        
        st.warning("Public Link ဖြင့် ဒေတာရေးရန် Google Apps Script လိုအပ်ပါသည်။")
        st.write("ဒေတာအသစ် - ", new_data)
        st.info("မှတ်ချက် - Public Link သုံးလျှင် CRUD (Write) လုပ်ရန် Service Account JSON Key မဖြစ်မနေ လိုအပ်လာပြီ ဖြစ်ပါသည်။")
    else:
        st.error("Please enter a customer name.")

st.subheader("Current Records")
st.dataframe(df)
