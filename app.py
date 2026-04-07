import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. पावरफुल एनालिसिस इंजन ---
def get_advanced_analysis(df, s_name, target_date):
    try:
        # डेटा को साफ़ करना (B=तारीख, Shift Column=डेटा)
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        
        # तारीखों को साफ़ करना ताकि मैच हो सके
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 15:
            return "Data Kam", "N/A"

        # साप्ताहिक वार (Monday, Tuesday...)
        target_day_name = target_date.strftime('%A')
        hindi_days = {'Monday': 'सोमवार', 'Tuesday': 'मंगलवार', 'Wednesday': 'बुधवार', 'Thursday': 'वीरवार', 'Friday': 'शुक्रवार', 'Saturday': 'शनिवार', 'Sunday': 'रविवार'}
        day_in_hindi = hindi_days.get(target_day_name, target_day_name)

        # उस 'वार' का हॉट नंबर
        day_data = df_clean[df_clean['DATE'].apply(lambda x: x.strftime('%A')) == target_day_name]
        hot_day_num = Counter(day_data['NUM'].astype(int)).most_common(1)[0][0] if not day_data.empty else 0
        
        # पकड़ नंबर (Pakad) - पिछले 30 दिनों का डेटा
        recent_30 = df_clean[df_clean['DATE'] < target_date].tail(30)['NUM'].astype(int).tolist()
        last_5 = df_clean[df_clean['DATE'] < target_date].tail(5)['NUM'].astype(int).tolist()
        hot_list = [n for n, c in Counter(recent_30).most_common(10)]
        pakad_nums = [n for n in hot_list if n not in last_5][:2]
        pakad_display = ", ".join([f"{n:02d}" for n in pakad_nums]) if pakad_nums else "--"

        analysis = f"📅 **{day_in_hindi}** का HOT: {hot_day_num:02d} | 🔥 पकड़: {pakad_display}"
        
        # टॉप मास्टर अंक (02d फॉर्मेट)
        p1 = f"{hot_day_num:02d}"
        p2 = f"{(hot_day_num+50)%100:02d}"
        p3 = f"{(int(last_5[-1] if last_5 else 0)+11)%100:02d}"
        
        return analysis, f"{p1} | {p2} | {p3}"

    except Exception as e:
        return f"Error: {str(e)}", "N/A"

# --- 2. UI सेटअप (डिफ़ॉल्ट फॉर्मेट के लिए) ---
st.set_page_config(page_title="MAYA AI Master", layout="wide")
st.title("🎯 MAYA AI: 5-Year Default Format Engine")

uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें (B=Date Format)", type=['xlsx'])

if uploaded_file:
    try:
        file_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        
        # C से I कॉलम की शिफ्ट्स (Column Index 2 to 8)
        shift_cols = list(df.columns[2:9]) 

        # यूजर से तारीख इनपुट (कैलेंडर)
        target_date = st.date_input("📅 तारीख चुनें:", datetime.date.today())

        if st.button("🚀 विश्लेषण शुरू करें"):
            # --- SAME DAY MATCH LOGIC ---
            df_match = df.copy()
            # B कॉलम (Index 1) की तारीखों को साफ़ करना
            df_match.iloc[:, 1] = pd.to_datetime(df_match.iloc[:, 1], errors='coerce').dt.date
            
            # चुनी हुई तारीख का मिलान
            selected_row = df_match[df_match.iloc[:, 1] == target_date]

            results_list = []
            for s in shift_cols:
                logic_info, top_picks = get_advanced_analysis(df, s, target_date)
                
                # 'SAME DAY' वैल्यू निकालना
                actual_val = "--"
                if not selected_row.empty:
                    val = str(selected_row[s].values[0]).strip()
                    # अगर नंबर है तो 02d फॉर्मेट, वरना जैसा है (XX)
                    if val.replace('.','',1).isdigit():
                        actual_val = f"{int(float(val)):02d}"
                    else:
                        actual_val = val

                results_list.append({
                    "Shift": s,
                    "📍 SAME DAY": actual_val,
                    "🗓️ साप्ताहिक व पकड़ विश्लेषण": logic_info,
                    "🌟 टॉप मास्टर अंक": top_picks
                })

            st.table(pd.DataFrame(results_list))
            
            if selected_row.empty:
                st.warning(f"⚠️ सूचना: आपकी एक्सेल में तारीख '{target_date}' का डेटा अभी नहीं मिला।")
            
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("कृपया अपनी 5 साल की एक्सेल फ़ाइल अपलोड करें।")
    
