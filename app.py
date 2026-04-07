import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. एनालिसिस इंजन (Heavy Data Optimized) ---
def get_gap_logic(df, s_name, target_date):
    try:
        # केवल ज़रूरी कॉलम ही प्रोसेस करना (Memory बचाने के लिए)
        df_clean = df[['DATE_COL', s_name]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 15:
            return "Data Kam", "N/A"

        # रोटेशन लॉजिक
        recent_data = df_clean[df_clean['DATE'] < target_date].tail(20)
        last_nums = recent_data['NUM'].astype(int).tolist()
        
        if not last_nums:
            return "No Recent Data", "N/A"

        # हरुफ़ रोटेशन
        last_val = last_nums[-1]
        andar_h = last_val // 10
        bahar_h = last_val % 10
        
        # Mirror & Family
        mirror = (last_val + 50) % 100
        
        analysis = f"🎯 पिछला हरुफ़: {andar_h}, {bahar_h} | 🪞 मिरर चाल: {mirror:02d}"
        
        # टॉप 3 रोटेशन (High Accuracy)
        p1 = f"{(bahar_h * 10) + andar_h:02d}" # पलटी लॉजिक
        p2 = f"{mirror:02d}"
        p3 = f"{( (andar_h + 1)%10 * 10) + bahar_h:02d}" # दहाई बढ़ाकर
        
        return analysis, f"{p1} | {p2} | {p3}"

    except Exception:
        return "Calculating..", "N/A"

# --- 2. UI सेटअप (High Speed) ---
st.set_page_config(page_title="MAYA AI Gap Master", layout="wide")
st.title("🎯 MAYA AI: Optimized Gap Logic")

# फाइल अपलोडर को 'Clear' करने का विकल्प दिया गया है
uploaded_file = st.file_uploader("📂 अपनी 5 साल की Excel फ़ाइल अपलोड करें", type=['xlsx'], help="अगर एरर आए तो फाइल दोबारा चुनें")

if uploaded_file:
    try:
        # भारी फाइल को तेजी से पढ़ने के लिए engine='openpyxl' का सही इस्तेमाल
        file_bytes = uploaded_file.read()
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        
        # कॉलम सेटअप
        df['DATE_COL'] = pd.to_datetime(df.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]

        target_date = st.date_input("📅 विश्लेषण की तारीख चुनें:", datetime.date.today())

        if st.button("🚀 रोटेशन विश्लेषण शुरू करें"):
            results_list = []
            selected_row = df[df['DATE_COL'] == target_date]

            for s in shift_cols:
                logic_info, top_picks = get_gap_logic(df, s, target_date)
                
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
                    "🗓️ अंकों की चाल": logic_info,
                    "🌟 टॉप 3 रोटेशन": top_picks
                })

            st.table(pd.DataFrame(results_list))
            st.balloons()

    except Exception as e:
        st.error(f"फाइल पढ़ने में दिक्कत: {e}. कृपया फाइल का साइज चेक करें।")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें। अगर लाल एरर आए, तो पेज रिफ्रेश (Refresh) करके दोबारा फाइल चुनें।")
    
