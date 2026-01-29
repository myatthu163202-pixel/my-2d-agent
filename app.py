import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Page Setting
st.set_page_config(page_title="2D Pro Cloud", page_icon="💰", layout="wide")

st.markdown("<h2 style='text-align: center; color: #2E86C1;'>📊 2D Professional Agent (Cloud)</h2>", unsafe_allow_html=True)

# Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Read existing data
try:
    df = conn.read(worksheet="Sheet1", usecols=[0, 1, 2, 3])
    df = df.dropna(how="all")
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# --- Sidebar Input Section ---
with st.sidebar:
    st.header("📝 စာရင်းအသစ်သွင်းရန်")
    name = st.text_input("ဝယ်သူအမည်")
    num = st.text_input("ဂဏန်း (ဥပမာ- 85)")
    amt = st.number_input("ထိုးကြေး (ကျပ်)", min_value=0, step=500)
    
    if st.button("✅ စာရင်းသိမ်းမည်", use_container_width=True):
        if name and num and amt > 0:
           new_data = pd.DataFrame([{
            "Customer": name,
            "Number": str(num),
            "Amount": int(amt),
            "Time": datetime.now().strftime("%I:%M %p")
        }])
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success(f"{name} အတွက် သိမ်းပြီးပါပြီ!")
            st.rerun()
        else:
            st.error("အချက်အလက် အကုန်ဖြည့်ပါ!")

# --- Main Dashboard ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 ယနေ့ရောင်းရငွေစာရင်း")
    search = st.text_input("🔍 ရှာဖွေရန် (အမည် သို့မဟုတ် ဂဏန်း)")
    
    if search:
        filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
    else:
        filtered_df = df
    
    st.dataframe(filtered_df, use_container_width=True, height=400)

with col2:
    st.subheader("💰 အကျဉ်းချုပ်")
    total_amt = df["Amount"].astype(float).sum() if not df.empty else 0
    st.metric(label="စုစုပေါင်း ရောင်းရငွေ", value=f"{total_amt:,.0f} MMK")
    
    st.divider()
    st.subheader("🏆 ပေါက်ဂဏန်းတိုက်ရန်")
    win_num = st.text_input("ပေါက်ဂဏန်း ထည့်ပါ")
    if win_num:
        winners = df[df["Number"] == str(win_num)]
        if not winners.empty:
            st.balloons()
            st.success(f"ဂဏန်း {win_num} ပေါက်သူ ရှိပါတယ်!")
            st.table(winners[["Customer", "Amount"]])
        else:
            st.warning("ပေါက်သူမရှိပါ။")


st.info("💡 ဤစနစ်သည် Cloud ပေါ်တွင် အလုပ်လုပ်သဖြင့် ဖုန်းနှင့် Laptop ဒေတာ အတူတူပင်ဖြစ်ပါသည်။")










