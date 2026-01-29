import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Agent Pro Plus", layout="wide")

# Link များ ချိတ်ဆက်ခြင်း
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

# ဒေတာ ဖတ်ယူခြင်း (Cache ကို အမြဲ Update ဖြစ်အောင် လုပ်ထားသည်)
try:
    df = pd.read_csv(f"{csv_url}&cachebuster={datetime.now().timestamp()}")
    df['Number'] = df['Number'].astype(str).str.zfill(2)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

st.title("💰 2D Pro Agent Dashboard")

# Dashboard - စုစုပေါင်းရောင်းရငွေ
total_in = df['Amount'].sum()
st.info(f"💵 စုစုပေါင်းရောင်းရငွေ: {total_in:,.0f} Ks")

# Sidebar - Admin နှင့် ပေါက်ဂဏန်းစစ်ရန်
st.sidebar.header("⚙️ Admin Control")
win_num = st.sidebar.text_input("🎰 ပေါက်ဂဏန်းရိုက်ပါ", max_chars=2)
za_rate = st.sidebar.number_input("💰 ဇ (အဆ)", value=80)

# Layout ခွဲခြင်း
c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("📝 စာရင်းသွင်းရန်")
    # Enter မခေါက်ဘဲ သိမ်းရန် Form ကို သုံးသည်
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("နာမည်")
        num = st.text_input("ဂဏန်း (ဥပမာ- 05)", max_chars=2)
        amt = st.number_input("ငွေပမာဏ", min_value=100, step=100)
        # အောက်က ခလုတ်ကို နှိပ်မှသာ သိမ်းဆည်းမည် (Enter ခေါက်စရာမလို)
        submit = st.form_submit_button("✅ စာရင်းသိမ်းမည်")
        
        if submit:
            if name and num:
                payload = {
                    "action": "insert", 
                    "Customer": name, 
                    "Number": str(num).zfill(2), 
                    "Amount": int(amt), 
                    "Time": datetime.now().strftime("%I:%M %p")
                }
                requests.post(script_url, json=payload)
                st.rerun()
            else:
                st.warning("နာမည်နှင့် ဂဏန်း အပြည့်အစုံ ဖြည့်ပါ")

with c2:
    st.subheader("📊 အရောင်းဇယား")
    if not df.empty:
        # နာမည်စစ်ရန် (Search)
        search = st.text_input("🔎 နာမည်ဖြင့်ရှာရန်")
        filtered_df = df[df['Customer'].str.contains(search, case=False, na=False)] if search else df
        
        # ဇယားပုံစံဖြင့် ပြသခြင်း (Select လုပ်ပြီး ဖျက်နိုင်သည်)
        event = st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "Amount": st.column_config.NumberColumn("ငွေပမာဏ", format="%d Ks"),
                "Time": "အချိန်"
            },
            hide_index=True,
            on_select="rerun",
            selection_mode="multi_rows"
        )
        
        # Select မှတ်ပြီး ဖျက်ခြင်း
        selected_rows = event.selection.rows
        if selected_rows:
            if st.button(f"🗑 ရွေးချယ်ထားသော ({len(selected_rows)}) ခုကိုဖျက်မည်"):
                for idx in selected_rows:
                    target = filtered_df.iloc[idx]
                    requests.post(script_url, json={
                        "action": "delete",
                        "Customer": target['Customer'],
                        "Number": str(target['Number']),
                        "Time": target['Time']
