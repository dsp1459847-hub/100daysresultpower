import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. एनालिसिस इंजन ---
def get_advanced_analysis(df, s_name, target_date):
    try:
        # डेटा को साफ़ करना (B=Index 1)
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        
        # तारीखों को 'Universal' फॉर्मेट में बदलना
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 10:
            return "Data Kam", "N/A"

        # वार (Day)
        target_day_name = target_date.strftime('%A')
        hindi_days = {'Monday': 'सोमवार', 'Tuesday': 'मंगलवार', 'Wednesday': 'बुधवार', 'Thursday': 'वीरवार', 'Friday': 'शुक्रवार', 'Saturday': 'शनिवार', 'Sunday': 'रविवार'}
        
        day_data = df_clean[df_clean['DATE'].apply(lambda x: x.strftime('%A') if hasattr(x, 'strftime') else "") == target_day_name]
        hot_day_num = Counter(day_data['NUM'].astype(int)).most_common(1)[0][0] if not day_data.empty else 0
        
        recent_30 = df_clean[df_clean['DATE'] < target_date].tail(30)['NUM'].astype(int).tolist()
        last_5 = df_clean[df_clean['DATE'] < target_date].tail(5)['NUM'].astype(int).tolist()
        hot_list = [n for n, c in Counter(recent_30).most_common(10)]
        pakad_nums = [n for n in hot_list if n not in last_5][:2]
        pakad_display = ", ".join([f"{n:02d}" for n in pakad_nums]) if pakad_nums else "--"

        analysis = f"📅 **{hindi_days.get(target_day_name)}** HOT: {hot_day_num:02d} | 🔥 पकड़: {pakad_display}"
        selection = f"{hot_day_num:02d} | {(hot_day_num+50)%100:02d} | {(int(last_5[-1] if last_5 else 0)+11)%100:02d}"
        
        return analysis, selection

    except Exception as e:
        return f"Error: {str(e)}", "N/A"

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI Master", layout="wide")
st.title("🎯 MAYA AI: Same-Day Final Fix")

uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'], key="final_fix_v7")

if uploaded_file:
    try:
        file_bytes = uploaded_file.getvalue()
        # एक्सेल लोड करना
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        
        # B=Date (1), C-I=Shifts (2-8)
        shift_cols = list(df.columns[2:9]) 

        # कैलेंडर
        target_date = st.date_input("📅 तारीख चुनें:", datetime.date.today())

        if st.button("🚀 विश्लेषण शुरू करें"):
            # --- 💡 SAME DAY MATCHING LOGIC (The Fix) ---
            df_match = df.copy()
            
            # तारीख के कॉलम को स्ट्रिंग (String) से असली तारीख में बदलना
            # दिन, महीना, साल - किसी भी क्रम में हो, ये उसे पहचान लेगा
            df_match.iloc[:, 1] = pd.to_datetime(df_match.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
            
            # तारीख का मिलान करना
            selected_row = df_match[df_match.iloc[:, 1] == target_date]

            results_list = []
            for s in shift_cols:
                logic_info, top_picks = get_advanced_analysis(df, s, target_date)
                
                # 'SAME DAY' वैल्यू निकालना
                actual_val = "--"
                if not selected_row.empty:
                    # सेल से वैल्यू उठाना
                    raw_val = str(selected_row[s].values[0]).strip()
                    # अगर नंबर है तो 02d फॉर्मेट, वरना जैसा है (जैसे XX)
                    if raw_val.replace('.','',1).isdigit():
                        actual_val = f"{int(float(raw_val)):02d}"
                    else:
                        actual_val = raw_val

                results_list.append({
                    "Shift": s,
                    "📍 SAME DAY": actual_val,
                    "🗓️ साप्ताहिक व पकड़ विश्लेषण": logic_info,
                    "🌟 टॉप मास्टर अंक": top_picks
                })

            st.table(pd.DataFrame(results_list))
            
            # अगर फिर भी नहीं मिला तो ये मैसेज दिखेगा
            if selected_row.empty:
                st.warning(f"⚠️ चेतावनी: एक्सेल की दूसरी (B) कॉलम में '{target_date.strftime('%d-%m-%Y')}' तारीख नहीं मिली।")
                st.write("आपके एक्सेल के पहले 5 तारीखें ये हैं:", df_match.iloc[:5, 1].values)

            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
    
