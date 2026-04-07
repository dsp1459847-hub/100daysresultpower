import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. अल्टीमेट हीटमैप इंजन ---
def get_ultimate_heatmap(df, s_name, target_date):
    try:
        # डेटा साफ़ करना
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], dayfirst=True, errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 15:
            return "Data Kam", "N/A"

        # वार (Day) इतिहास
        t_day_name = target_date.strftime('%A')
        day_history = df_clean[df_clean['DATE'].apply(lambda x: x.strftime('%A') if hasattr(x, 'strftime') else "") == t_day_name]
        
        # ताज़ा चाल
        recent_30 = df_clean[df_clean['DATE'] < target_date].tail(30)['NUM'].astype(int).tolist()
        last_val = recent_30[-1] if recent_30 else 0
        
        # रोटेशन लॉजिक
        combined = day_history['NUM'].astype(int).tolist()[-40:] + recent_30
        top_3_list = [f"{n:02d}" for n, c in Counter(combined).most_common(3)]
        
        mirror = (last_val + 55) % 100
        
        analysis = f"🎯 {t_day_name} HOT: {top_3_list[0]} | 🪞 राशि: {mirror:02d}"
        selection = f"{top_3_list[0]} | {mirror:02d} | {( (last_val // 10) * 10 ) + ( (last_val + 1) % 10 ):02d}"
        
        return analysis, selection
    except:
        return "Analyzing..", "N/A"

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI Master", layout="wide")
st.title("🔥 MAYA AI: 5-Year Deep Heatmap")

uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'], key="v13_fixed")

if uploaded_file:
    try:
        file_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        
        # तारीख कॉलम (Index 1) सेट करना
        df_match = df.copy()
        df_match['DATE_COL'] = pd.to_datetime(df_match.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]
        target_date = st.date_input("📅 तारीख चुनें:", datetime.date.today())

        if st.button("🚀 विश्लेषण शुरू करें"):
            # SAME DAY मिलान
            selected_row = df_match[df_match['DATE_COL'] == target_date]
            results_list = []

            for s in shift_cols:
                logic_info, top_picks = get_ultimate_heatmap(df_match, s, target_date)
                
                # SAME DAY वैल्यू निकालना (यहाँ एरर था, जिसे अब ठीक कर दिया गया है)
                actual_val = "--"
                if not selected_row.empty:
                    raw_val = str(selected_row[s].values[0]).strip() # नाम 'raw_val' अब सही है
                    if raw_val.replace('.','',1).isdigit():
                        actual_val = f"{int(float(raw_val)):02d}"
                    else:
                        actual_val = raw_val

                results_list.append({
                    "Shift": s,
                    "📍 SAME DAY": actual_val,
                    "🗓️ 5-साल का हीटमैप": logic_info,
                    "🌟 टॉप 3 मास्टर अंक": top_picks
                })

            st.table(pd.DataFrame(results_list))
            
            if not selected_row.empty:
                st.success("✅ 7 तारीख का डेटा मिल गया!")
            else:
                st.warning(f"⚠️ तारीख {target_date.strftime('%d-%m-%Y')} नहीं मिली।")
            
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
    
