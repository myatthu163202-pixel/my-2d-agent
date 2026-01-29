import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time

# Page configuration
st.set_page_config(page_title="2D Agent Pro", layout="wide")

# Secrets ထဲက Link များကို ခေါ်ယူခြင်း
try:
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    script_url = st.secrets["connections"]["gsheets"]["script_url"]
    # CSV format ပြောင်းလဲခြင်း
    csv_url = sheet_url.replace('/edit', '/export?format=csv')
except:
    st.error("Secrets ထဲမှာ Link တွေ မထည့်ရသေးပါဘူး။")
    st.stop()

# ဒေတာကို အတင်းအကျပ် အသစ်ဆွဲယူသည့် Function
def fetch_data():
    # Cache ကို လုံးဝအလုပ်မလုပ်အောင် timestamp ဖြင့် အမြဲပြောင်းလဲပေးသည်
    fresh_url = f"{csv_url}&gid=0&cache={int(time.time())}"
    try:
        data = pd.read_csv(fresh_url)
        # Column အမည်များ မှန်မမှန် စစ်ဆေးခြင်း
        if not data.empty:
            data['Number'] = data['Number'].astype(str).str.zfill(2)
            data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce').fillna(0)
        return data
    except Exception as e:
        return pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# App ကို စတင်တိုင်း ဒေတာအသစ်ယူမည်
df = fetch_data()

st.title("💰 2D Agent Pro Dashboard")

# အရောင်းစုစုပေါင်း ပြသရန်
total_amt = df['Amount'].sum() if not df.empty else 0
st.metric("💵 စုစုပေါင်းရောင်းရငွေ", f"{total_amt:,.0f} Ks")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 စာရင်းသွင်းရန်")
    with st.form("input_form", clear_on_submit=True):
        c_name = st.text_input("နာမည်")
        c_num = st.text_input("ဂဏန်း", max_chars=2)
        c_amt = st.number_input("ငွေပမာဏ", min_value=100, step=100)
        
        if st.form_submit_button("✅ သိမ်းဆည်းမည်"):
            if c_name and c_num:
                data_to_send = {
                    "action": "insert",
                    "Customer": c_name,
                    "Number": str(c_num).zfill(2),
                    "Amount": int(c_amt),
                    "Time": datetime.now().strftime("%I:%M %p")
                }
                # Google Sheet သို့ ပေးပို့ခြင်း
                res = requests.post(script_url, json=data_to_send)
                if res.status_code == 200:
                    st.success("သိမ်းပြီးပါပြီ။ ဇယားကို Update လုပ်နေသည်...")
                    time.sleep(2) # Google ဘက်က update ဖြစ်အောင် ခဏစောင့်ပေးရသည်
                    st.rerun()
            else:
                st.warning("နာမည်နှင့် ဂဏန်း ပြည့်စုံစွာ ဖြည့်ပါ")

with col2:
    st.subheader("📊 အရောင်းဇယား")
    # Manual Refresh ခလုတ်
    if st.button("🔄 စာရင်းအသစ်များကို ဆွဲယူရန်"):
        st.rerun()

    if not df.empty:
        # Search Feature
        search_query = st.text_input("🔎 နာမည်ဖြင့်ရှာဖွေရန်")
        display_df = df[df['Customer'].str.contains(search_query, case=False, na=False)] if search_query else df
        
        # ဇယားပုံစံ (Multi-selection အလုပ်လုပ်ရန်)
        selected_data = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="multi_rows"
        )
        
        # Select မှတ်ပြီး ဖျက်ခြင်း
        rows_to_del = selected_data.selection.rows
        if rows_to_del:
            if st.button(f"🗑 ရွေးချယ်ထားသော ({len(rows_to_del)}) ခုကိုဖျက်မည်"):
                for r_idx in rows_to_del:
                    row_data = display_df.iloc[r_idx]
                    requests.post(script_url, json={
                        "action": "delete",
                        "Customer": row_data['Customer'],
                        "Number": str(row_data['Number']),
                        "Time": row_data['Time']
                    })
                time.sleep(1.5)
                st.rerun()
    else:
        st.info("လက်ရှိတွင် စာရင်းမရှိသေးပါ။ (သို့မဟုတ်) Sheet ကို Share မထားပါ။")

# Admin Sidebar
st.sidebar.header("⚙️ Settings")
win_val = st.sidebar.text_input("🎰 ပေါက်ဂဏန်း", max_chars=2)
za = st.sidebar.number_input("💰 ဇ (အဆ)", value=80)

if win_val and not df.empty:
    wins = df[df['Number'] == win_val]
    payout = wins['Amount'].sum() * za
    st.sidebar.divider()
    st.sidebar.write(f"🏆 ပေါက်သူ: {len(wins)} ဦး")
    st.sidebar.write(f"💸 လျော်ကြေး: {payout:,.0f} Ks")
