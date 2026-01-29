import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Pro Agent", page_icon="💹", layout="wide")

# Link များ ချိတ်ဆက်ခြင်း
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

# ဒေတာဖတ်ခြင်း
try:
    df = pd.read_csv(f"{csv_url}&cachebuster={datetime.now().timestamp()}")
    df['Number'] = df['Number'].astype(str).str.zfill(2)
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# --- SIDEBAR (စီမံခန့်ခွဲမှုဇုန်) ---
st.sidebar.header("⚙️ Admin Dashboard")

# ၁။ ပေါက်ဂဏန်းစစ်ဆေးခြင်း
win_num = st.sidebar.text_input("🏆 ပေါက်ဂဏန်းရိုက်ပါ", max_chars=2, placeholder="ဥပမာ- 05")
commission = st.sidebar.slider("ကော်မရှင် (%)", 0, 20, 10)

# ၂။ အမြတ်အရှုံး တွက်ချက်ခြင်း
total_sales = df['Amount'].sum() if not df.empty else 0
net_income = total_sales * (1 - commission/100)

st.sidebar.divider()
st.sidebar.subheader("📊 စာရင်းချုပ်")
st.sidebar.write(f"စုစုပေါင်းရောင်းရငွေ: {total_sales:,.0f} Ks")
st.sidebar.write(f"ကော်မရှင်နုတ်ပြီးသား: {net_income:,.0f} Ks")

if win_num:
    winners = df[df['Number'] == win_num]
    total_payout = winners['Amount'].sum() * 80
    st.sidebar.error(f"လျော်ကြေးစုစုပေါင်း: {total_payout:,.0f} Ks")
    
    profit_loss = net_income - total_payout
    if profit_loss >= 0:
        st.sidebar.success(f"ယနေ့အမြတ်: +{profit_loss:,.0f} Ks")
    else:
        st.sidebar.error(f"ယနေ့အရှုံး: {profit_loss:,.0f} Ks")

st.sidebar.divider()
# ၃။ အကုန်ဖျက်သည့်ခလုတ်
if st.sidebar.button("🗑 စာရင်းအားလုံး ရှင်းလင်းမည်"):
    pw = st.sidebar.text_input("Password", type="password")
    if pw == "1234": # Password က 1234 ပါ
        requests.post(script_url, json={"action": "clear_all"})
        st.rerun()

# --- MAIN UI ---
st.title("💹 2D Professional Agent System")

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
    st.subheader("🔍 စာရင်းရှာဖွေခြင်း")
    search = st.text_input("🔎 နာမည်ဖြင့် ရှာရန်")
    
    display_df = df.copy()
    if search:
        display_df = display_df[display_df['Customer'].str.contains(search, case=False, na=False)]
    
    st.dataframe(display_df.iloc[::-1], use_container_width=True, height=300)

    # တစ်ခုချင်းဖျက်ရန်အပိုင်း
    st.subheader("🗑 တစ်ခုချင်းစီ ဖျက်ရန်")
    for index, row in display_df.iloc[::-1].iterrows():
        with st.expander(f"👤 {row['Customer']} | 🔢 {row['Number']} | 💵 {row['Amount']} Ks"):
            if st.button(f"🗑 ဖျက်ရန်", key=f"del_{index}"):
                del_payload = {"action": "delete", "Customer": row['Customer'], "Number": str(row['Number']), "Time": row['Time']}
                requests.post(script_url, json=del_payload)
                st.rerun()
