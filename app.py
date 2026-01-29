import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Professional Agent", page_icon="📊")
st.title("📊 2D Professional Agent")

# Secrets ထဲက Link များ ယူခြင်း
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

# ဒေတာဖတ်ခြင်း
try:
    # Cache မကျန်အောင် URL နောက်မှာ အချိန်ထည့်ပြီး ဖတ်ပါမည်
    df = pd.read_csv(f"{csv_url}&cachebuster={datetime.now().timestamp()}")
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# Input Form
with st.form("entry_form", clear_on_submit=True):
    name = st.text_input("Customer Name")
    num = st.number_input("Number", min_value=0, max_value=99, step=1)
    amt = st.number_input("Amount", min_value=100, step=100)
    
    if st.form_submit_button("Submit"):
        if name:
            new_data = {
                "Customer": name, 
                "Number": str(num),
                "Amount": int(amt), 
                "Time": datetime.now().strftime("%I:%M %p")
            }
            # Apps Script ဆီ ဒေတာပို့ခြင်း
            with st.spinner('သိမ်းဆည်းနေပါသည်...'):
                response = requests.post(script_url, json=new_data)
                if response.status_code == 200:
                    st.success(f"{name} အတွက် စာရင်းသွင်းပြီးပါပြီ!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Error: ဒေတာပေးပို့မှု မအောင်မြင်ပါ။")
        else:
            st.error("Customer Name ထည့်ပေးပါ။")

st.subheader("ယနေ့စာရင်းများ")
st.dataframe(df, use_container_width=True)
