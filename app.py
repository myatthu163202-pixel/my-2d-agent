import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time

st.set_page_config(page_title="2D Agent Pro", layout="wide")

# Link များ ချိတ်ဆက်ခြင်း
try:
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    script_url = st.secrets["connections"]["gsheets"]["script_url"]
    csv_url = sheet_url.replace('/edit', '/export?format=csv')
except:
    st.error("Secrets link များ မမှန်ကန်ပါ။")
    st.stop()

# ဒေတာကို အသစ်ရအောင် ဆွဲယူသည့် Function
def load_data():
    try:
        # Cache မကျန်အောင် Timestamp ဖြင့် အတင်းဆွဲယူသည်
        url = f"{csv_url}&cachebuster={int(time.time())}"
        data = pd.read_csv(url)
        if not data.empty:
            data['Number'] = data['Number'].astype(str).str.zfill(2)
            data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce').fillna(0)
        return data
    except:
        return pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

df = load_data()

st.title("💰 2D Pro Agent Dashboard")

# Dashboard - စုစုပေါင်းရောင်းရငွေ
total_in = df['Amount'].sum() if not df.empty else 0
st.info(f"💵 စုစုပေါင်းရောင်းရငွေ: {total_in:,.0f} Ks")

# Sidebar - ပေါက်ဂဏန်းစစ်ရန်
st.sidebar.header("⚙️ Admin Control")
win_num = st.sidebar.text_input("🎰 ပေါက်ဂဏန်းရိုက်ပါ", max_chars=2)
za_rate = st.sidebar.number_input("💰 ဇ (အဆ)", value=80)

c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("📝 စာရင်းသွင်းရန်")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("နာမည်")
        num = st.text_input("ဂဏန်း (ဥပမာ- 05)", max_chars=2)
        amt = st.number_input("ငွေပမာဏ", min_value=100, step=100)
        submit = st.form_submit_button("✅ သိမ်းဆည်းမည်")
        
        if submit:
            if name and num:
                payload = {
                    "action": "insert", 
                    "Customer": name, 
                    "Number": str(num).zfill(2), 
                    "Amount": int(amt), 
                    "Time": datetime.now().strftime("%I:%M %p")
                }
                res = requests.post(script_url, json=payload)
                if res.status_code == 200:
                    st.success("သိမ်းပြီးပါပြီ။")
                    time.sleep(1.5) # Google Sheet Update ဖြစ်ချိန် စောင့်သည်
                    st.rerun()
            else:
                st.warning("အချက်အလက် ပြည့်စုံအောင် ဖြည့်ပါ")

with c2:
    st.subheader("📊 အရောင်းဇယား")
    if st.button("🔄 စာရင်းအသစ်ကြည့်မည်"):
        st.rerun()

    if not df.empty:
        search = st.text_input("🔎 နာမည်ဖြင့်ရှာရန်")
        filtered_df = df[df['Customer'].str.contains(search, case=False, na=False)] if search else df
        
        # ဇယားပုံစံ (Multi-row selection ပါဝင်သည်)
        event = st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={"Amount": st.column_config.NumberColumn("ငွေပမာဏ", format="%d Ks")},
            hide_index=True,
            on_select="rerun",
            selection_mode="multi_rows"
        )
        
        # Select မှတ်ပြီးဖျက်ခြင်း
        selected_rows = event.selection.rows
        if selected_rows:
            if st.button(f"🗑 ရွေးထားသော ({len(selected_rows)}) ခုကိုဖျက်မည်"):
                for idx in selected_rows:
                    target = filtered_df.iloc[idx]
                    requests.post(script_url, json={
                        "action": "delete",
                        "Customer": target['Customer'],
                        "Number": str(target['Number']),
                        "Time": target['Time']
                    })
                time.sleep(1.5)
                st.rerun()
        
        # အမြတ်/အရှုံး တွက်ချက်ခြင်း (Metric ဖြင့်ပြသည်)
        if win_num:
            winners = df[df['Number'] == win_num]
            total_out = winners['Amount'].sum() * za_rate
            balance = total_in - total_out
            st.divider()
            st.metric("💸 လျော်ကြေးစုစုပေါင်း", f"{total_out:,.0f} Ks")
            st.metric("📈 အသားတင် အမြတ်/အရှုံး", f"{balance:,.0f} Ks", delta=balance)
    else:
        st.info("လက်ရှိတွင် စာရင်းမရှိသေးပါ။")

# Admin Password
st.sidebar.divider()
del_pw = st.sidebar.text_input("Admin Password", type="password")
if st.sidebar.button("⚠️ စာရင်းအားလုံး ရှင်းလင်းမည်"):
    if del_pw == "1632022":
        requests.post(script_url, json={"action": "clear_all"})
        time.sleep(1.5)
        st.rerun()
