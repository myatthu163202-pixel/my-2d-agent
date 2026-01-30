import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time

st.set_page_config(page_title="2D Agent Pro Dashboard", layout="wide")

# Link များ ချိတ်ဆက်ခြင်း
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

def load_data():
    try:
        url = f"{csv_url}&cachebuster={int(time.time())}"
        data = pd.read_csv(url)
        if not data.empty:
            data.columns = data.columns.str.strip()
            data['Number'] = data['Number'].astype(str).str.zfill(2)
            data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce').fillna(0)
        return data
    except:
        return pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

df = load_data()

st.title("💰 2D Agent Pro Dashboard")

st.sidebar.header("⚙️ Admin & Win Check")
win_num = st.sidebar.text_input("🎰 ပေါက်ဂဏန်းရိုက်ပါ", max_chars=2)
za_rate = st.sidebar.number_input("💰 ဇ (အဆ)", value=80)

total_in = df['Amount'].sum() if not df.empty else 0
st.info(f"💵 စုစုပေါင်းရောင်းရငွေ: {total_in:,.0f} Ks")

c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("📝 စာရင်းသွင်းရန်")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("နာမည်")
        num = st.text_input("ဂဏန်း (00-99)", max_chars=2)
        amt = st.number_input("ငွေပမာဏ", min_value=100, step=100)
        if st.form_submit_button("✅ သိမ်းဆည်းမည်"):
            if name and num:
                payload = {
                    "action": "insert", "Customer": name.strip(), 
                    "Number": str(num).zfill(2), "Amount": int(amt), 
                    "Time": datetime.now().strftime("%I:%M %p")
                }
                requests.post(script_url, json=payload)
                st.success("သိမ်းပြီးပါပြီ။")
                time.sleep(1.5)
                st.rerun()

with c2:
    st.subheader("📊 အရောင်းဇယား")
    col_a, col_b = st.columns([1, 2])
    if col_a.button("🔄 Refresh"):
        st.rerun()
    search = col_b.text_input("🔎 နာမည်ဖြင့်ရှာရန်")

    if not df.empty:
        view_df = df[df['Customer'].str.contains(search, case=False, na=False)] if search else df
        st.dataframe(view_df, use_container_width=True, hide_index=True)

        # --- ပေါက်သူစာရင်း နှင့် လျော်ကြေးတွက်ချက်ခြင်း ---
        if win_num:
            winners = df[df['Number'] == win_num].copy()
            total_out = winners['Amount'].sum() * za_rate
            balance = total_in - total_out
            
            st.divider()
            st.subheader("📈 ရလဒ်အကျဉ်းချုပ်")
            k1, k2, k3 = st.columns(3)
            k1.metric("🏆 ပေါက်သူ", f"{len(winners)} ဦး")
            k2.metric("💸 လျော်ကြေးစုစုပေါင်း", f"{total_out:,.0f} Ks")
            k3.metric("💹 အမြတ်/အရှုံး", f"{balance:,.0f} Ks", delta=balance)
            
            if not winners.empty:
                st.write("🎊 **ပေါက်သူများစာရင်း နှင့် လျော်ရမည့်ငွေ -**")
                # လျော်ကြေးကော်လံအသစ် ထည့်တွက်ပြခြင်း
                winners['လျော်ရမည့်ငွေ'] = winners['Amount'] * za_rate
                # ပြချင်တဲ့ column တွေကိုပဲ ရွေးပြမယ်
                st.table(winners[['Customer', 'Number', 'Amount', 'လျော်ရမည့်ငွေ']])
    else:
        st.info("လက်ရှိတွင် စာရင်းမရှိသေးပါ။")

# တစ်ခုချင်းဖျက်ရန်
if not df.empty:
    st.divider()
    st.subheader("🗑 စာရင်းဖျက်ရန်")
    with st.expander("တစ်ခုချင်းစီ ဖျက်ရန် ဤနေရာကိုနှိပ်ပါ"):
        for i in range(len(df)-1, -1, -1):
            r = df.iloc[i]
            col_x, col_y = st.columns([4, 1])
            col_x.write(f"👤 {r['Customer']} | 🔢 {r['Number']} | 💵 {r['Amount']} Ks")
            
            if col_y.button("ဖျက်", key=f"del_{i}"):
                requests.post(script_url, json={"action": "delete", "row_index": i + 1})
                st.toast(f"ဖျက်ပြီးပါပြီ။")
                time.sleep(1.5)
                st.rerun()

st.sidebar.divider()
if st.sidebar.button("⚠️ စာရင်းအားလုံးဖျက်မည်"):
    requests.post(script_url, json={"action": "clear_all"})
    time.sleep(1.5)
    st.rerun()
