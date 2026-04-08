import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. ताज़ा चाल इंजन (Current Pulse Logic) ---
def get_current_pulse(df, s_name, target_date):
    try:
        # डेटा क्लीनिंग
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], dayfirst=True, errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 10:
            return "Data Kam", "N/A"

        # A. पिछले 3 दिनों की ताज़ा चाल (Power of 3)
        recent_all = df_clean[df_clean['DATE'] < target_date].tail(30)
        last_3_days = recent_all.tail(3)['NUM'].astype(int).tolist()
        
        if not last_3_days:
            return "No Recent Data", "N/A"

        last_val = last_3_days[-1]
        
        # B. हरुफ़ का रोटेशन (Digit Power)
        # अंदर और बाहर के अंकों की सबसे ताज़ा फ्रीक्वेंसी
        andar_h = last_val // 10
        bahar_h = last_val % 10
        
        # C. 5-साल का वार (Day) कनेक्शन (Secondary Weight)
        t_day_name = target_date.strftime('%A')
        day_history = df_clean[df_clean['DATE'].apply(lambda x: x.strftime('%A')) == t_day_name]
        hot_day = Counter(day_history['NUM'].astype(int).tolist()[-20:]).most_common(1)[0][0]

        # लॉजिक: मिरर + पिछले 3 दिन का औसत + वार का हॉट
        mirror = (last_val + 50) % 100
        
        analysis = f"🎯 ताज़ा अंक: {last_val:02d} | 🪞 मिरर: {mirror:02d} | 📅 वार ({t_day_name}) HOT: {hot_day:02d}"
        
        # --- टॉप 3 शॉर्ट-टर्म प्रेडिक्शन ---
        p1 = f"{hot_day:02d}" # वार की ताकत
        p2 = f"{mirror:02d}" # राशि की चाल
        p3 = f"{( (andar_h * 10) + ( (bahar_h + 5) % 10 ) ):02d}" # हरुफ़ का जोड़
        
        return analysis, f"{p1} | {p2} | {p3}"
    except:
        return "Processing..", "N/A"

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI Pulse", layout="wide")
st.title("⚡ MAYA AI: Current Pulse & Gap Logic")

uploaded_file = st.file_uploader("📂 अपनी 5 साल की Excel फ़ाइल अपलोड करें", type=['xlsx'], key="v14_pulse")

if uploaded_file:
    try:
        file_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        
        # तारीख कॉलम मिलान
        df_match = df.copy()
        df_match['DATE_COL'] = pd.to_datetime(df_match.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]
        target_date = st.date_input("📅 तारीख चुनें (7 अप्रैल 2026):", datetime.date.today())

        if st.button("🚀 ताज़ा विश्लेषण शुरू करें"):
            selected_row = df_match[df_match['DATE_COL'] == target_date]
            results_list = []

            for s in shift_cols:
                logic_info, top_picks = get_current_pulse(df_match, s, target_date)
                
                # SAME DAY RESULT
                actual_val = "--"
                if not selected_row.empty:
                    raw_val = str(selected_row[s].values[0]).strip()
                    if raw_val.replace('.','',1).isdigit():
                        actual_val = f"{int(float(raw_val)):02d}"
                    else:
                        actual_val = raw_val

                results_list.append({
                    "Shift": s,
                    "📍 SAME DAY": actual_val,
                    "🗓️ ताज़ा चाल (Current Pulse)": logic_info,
                    "🌟 टॉप 3 मास्टर अंक": top_picks
                })

            st.table(pd.DataFrame(results_list))
            
            if not selected_row.empty:
                st.success(f"✅ {target_date.strftime('%d-%m-%Y')} का डेटा लोड हो गया है।")
            else:
                st.warning("⚠️ तारीख मैच नहीं हुई। कृपया अपनी एक्सेल की B कॉलम चेक करें।")
            
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("5 साल वाली एक्सेल फ़ाइल अपलोड करें।")
                    
