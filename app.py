import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# Page Configuration
st.set_page_config(page_title="2D Professional Agent", page_icon="💰", layout="wide")

# Link များ ချိတ်ဆက်ခြင်း
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

# ဒေတာဖတ်ခြင်း (Cachebuster ပါမှ ဖျက်လိုက်ရင် ချက်ချင်းပျောက်မှာပါ)
try:
    df = pd.read_csv(f"{csv_url}&cachebuster={datetime.now().timestamp()}")
    df['Number'] = df['Number'].astype(str).str.zfill(2)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# --- SIDEBAR (စီမံခန့်ခွဲမှုနှင့် အမြတ်အရှုံး) ---
st.sidebar.header("⚙️ Dashboard Controls")

# ၁။ အမြတ်အရှုံးတွက်ချက်ခြင်း
st.sidebar.subheader("📊 Profit & Loss")
comm_rate = st.sidebar.slider("ကော်မရှင် (%)", 0, 20, 10)
win_num = st.sidebar.text_input("🏆 ပေါက်ဂဏန်းရိုက်ပါ", max_chars=2, placeholder="ဥပမာ- 05")

total_sales = df['Amount'].sum()
net_sales = total_sales * (1 - comm_rate/100)

st.sidebar.write(f"စုစုပေါင်းရောင်းရငွေ: {total_sales:,.0f} Ks")
st.sidebar.write(f"ကော်မရှင်နုတ်ပြီး: {net_sales:,.0f} Ks")

if win_num:
    winners = df[df['Number'] == win_num]
    total_payout = winners['Amount'].sum() * 80
    profit_loss = net_sales - total_payout
    
    st.sidebar.divider()
    st.sidebar.write(f"လျော်ကြေးစုစုပေါင်း: {total_payout:,.0f} Ks")
    if profit_loss >= 0:
        st.sidebar.success(f"ယနေ့အမြတ်: +{profit_loss:,.0f} Ks")
    else:
        st.sidebar.error(f"ယနေ့အရှုံး: {profit_loss:,.0f} Ks")

st.sidebar.divider()

# ၂။ အကုန်ဖျက်သည့်ခလုတ် (Delete All)
st.sidebar.subheader("⚠️ အန္တရာယ်ရှိဇုန်")
del_pw = st.sidebar.text_input("Admin Password ရိုက်ပါ", type="password", key="admin_pw")
if st.sidebar.button("🗑 စာရင်းအားလုံး အကုန်ဖျက်မည်"):
    if del_pw == "1632022": # သင်တောင်းဆိုထားသော Password သို့ ပြောင်းလဲထားပါသည်
        with st.spinner('စာရင်းအားလုံးကို အကုန်ပြောင်အောင် ဖျက်နေပါသည်...'):
            requests.post(script_url, json={"action": "clear_all"})
            st.rerun()
    else:
        st.sidebar.error("Password မှားနေပါသည်။")

# --- MAIN UI ---
st.title("💰 2D Professional Agent System")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 စာရင်းသွင်းရန်")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("Customer Name")
        num = st.text_input("Number", max_chars=2)
        amt = st.number_input("Amount", min_value=100, step=100)
        if st.form_submit_button("✅ သိမ်းမည်"):
            if name and num:
                new_data = {"action": "insert", "Customer": name, "Number": str(num).zfill(2), "Amount": int(amt), "Time": datetime.now().strftime("%I:%M %p")}
                requests.post(script_url, json=new_data)
                st.rerun()

with col2:
    st.subheader("🔍 စာရင်းကြည့်ရန် နှင့် တစ်ခုချင်းဖျက်ရန်")
    search_query = st.text_input("🔎 နာမည်ဖြင့် ရှာရန်")
    
    display_df = df.copy()
    if search_query:
        display_df = display_df[display_df['Customer'].str.contains(search_query, case=False, na=False)]
    
    # စာရင်းတစ်ခုချင်းစီကို ဖျက်ရန်
    if not display_df.empty:
        for index, row in display_df.iloc[::-1].iterrows():
            with st.expander(f"👤 {row['Customer']} | 🔢 {row['Number']} | 💵 {row['Amount']} Ks"):
                st.write(f"⏰ အချိန်: {row['Time']}")
                if st.button(f"🗑 ဤစာရင်းကို ဖျက်ရန်", key=f"del_{index}"):
                    del_data = {"action": "delete", "Customer": row['Customer'], "Number": str(row['Number']), "Time": row['Time']}
                    requests.post(script_url, json=del_data)
                    st.rerun()
    else:
        st.info("လက်ရှိတွင် စာရင်းမရှိသေးပါ။")
