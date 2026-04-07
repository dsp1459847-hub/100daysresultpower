import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. रोटेशन इंजन ---
def get_gap_logic(df, s_name, target_date):
    try:
        # B कॉलम तारीख है, s_name डेटा है
        df_clean = df[['DATE_COL', s_name]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 10:
            return "Data Kam", "N/A"

        # पिछले 20 दिनों का रोटेशन
        recent_data = df_clean[df_clean['DATE'] < target_date].tail(20)
        last_nums = recent_data['NUM'].astype(int).tolist()
        
        if not last_nums:
            return "No Data", "N/A"

        last_val = last_nums[-1]
        andar_h, bahar_h = last_val // 10, last_val % 10
        mirror = (last_val + 50) % 100
        
        analysis = f"🎯 हरुफ़: {andar_h}, {bahar_h} | 🪞 मिरर: {mirror:02d}"
        
        # टॉप 3 रोटेशन
        p1 = f"{(bahar_h * 10) + andar_h:02d}" # पलटी
        p2 = f"{mirror:02d}" # मिरर
        p3 = f"{((last_val + 11) % 100):02d}" # चाल
        
        return analysis, f"{p1} | {p2} | {p3}"
    except:
        return "Calculating..", "N/A"

# --- 2. UI सेटअप (Safe Upload Fix) ---
st.set_page_config(page_title="MAYA AI Safe Master", layout="wide")
st.title("🛡️ MAYA AI: Safe Upload & Rotation")

# फाइल अपलोडर - Error फिक्स करने के लिए 'Type' सीमित किया गया है
uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'], key="safe_v11")

if uploaded_file is not None:
    try:
        # 💡 SAFE LOADING: फाइल को बाइट्स में पढ़ना
        with st.spinner('डेटा पढ़ा जा रहा है... कृपया प्रतीक्षा करें।'):
            data_bytes = uploaded_file.getvalue()
            df = pd.read_excel(io.BytesIO(data_bytes), engine='openpyxl')
            
            # तारीख कॉलम सेट करना (B = Index 1)
            df['DATE_COL'] = pd.to_datetime(df.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
            # आपकी शिफ्ट्स: DS, FD, GD, GL, DB, SG, ZA
            shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]

            target_date = st.date_input("📅 तारीख चुनें:", datetime.date.today())

            if st.button("🚀 विश्लेषण शुरू करें"):
                selected_row = df[df['DATE_COL'] == target_date]
                results_list = []

                for s in shift_cols:
                    logic_info, top_picks = get_gap_logic(df, s, target_date)
                    
                    actual_val = "--"
                    if not selected_row.empty:
                        raw_v = str(selected_row[s].values[0]).strip()
                        actual_val = f"{int(float(raw_v)):02d}" if raw_v.replace('.','',1).isdigit() else raw_v

                    results_list.append({
                        "Shift": s,
                        "📍 SAME DAY": actual_val,
                        "🗓️ अंकों की चाल": logic_info,
                        "🌟 टॉप 3 रोटेशन": top_picks
                    })

                st.table(pd.DataFrame(results_list))
                st.balloons()

    except Exception as e:
        st.error(f"❌ गड़बड़: {e}. फाइल अपलोड करते समय मोबाइल का इंटरनेट बंद न करें।")
else:
    st.info("फाइल चुनें। अगर लाल निशान आए, तो ब्राउज़र में 'Refresh' बटन दबाएँ।")
    
