import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. एक्सट्रीम प्रोबेबिलिटी इंजन (Extreme Logic) ---
def get_extreme_logic(df, s_name, target_date):
    try:
        # डेटा साफ़ करना (B=Index 1, s_name=Shift)
        df_clean = df[['DATE_COL', s_name]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 30:
            return "Data Kam", "N/A"

        # A. ताज़ा चाल (Current Pulse)
        recent_all = df_clean[df_clean['DATE'] < target_date]['NUM'].astype(int).tolist()
        if not recent_all: return "No Data", "N/A"
        
        last_val = recent_all[-1]
        
        # B. ऐतिहासिक मिलान (Historical Hit Rate)
        # पिछले 5 सालों में जब-जब 'last_val' आया, उसके अगले दिन क्या आया?
        next_day_hits = []
        for i in range(len(recent_all) - 1):
            if recent_all[i] == last_val:
                next_day_hits.append(recent_all[i+1])
        
        # सबसे ज्यादा आने वाला अगला नंबर (Historical Probability)
        if next_day_hits:
            prob_num = Counter(next_day_hits).most_common(1)[0][0]
        else:
            # अगर सीधा मैच न मिले तो 'राशि' (Family) का सबसे हॉट नंबर
            prob_num = Counter(recent_all[-50:]).most_common(1)[0][0]

        # C. हरुफ़ का जोड़ (Sum Logic)
        last_sum = (last_val // 10 + last_val % 10) % 10
        
        analysis = f"🎯 पिछले अंक ({last_val:02d}) की अगली चाल: {prob_num:02d} | ➕ जोड़: {last_sum}"
        
        # --- टॉप 3 सुपर सिलेक्शन ---
        p1 = f"{prob_num:02d}" # सबसे ज्यादा संभावित
        p2 = f"{(last_val + 50) % 100:02d}" # मिरर (Mirror)
        p3 = f"{(last_sum * 10) + (last_val % 10):02d}" # जोड़ + बाहर का हरुफ़
        
        return analysis, f"{p1} | {p2} | {p3}"
    except:
        return "Analyzing..", "N/A"

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI Extreme", layout="wide")
st.title("🔥 MAYA AI: Extreme Probability Mapping")

uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'], key="extreme_v12")

if uploaded_file is not None:
    try:
        data_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(data_bytes), engine='openpyxl')
        
        # तारीख कॉलम (Index 1 = B)
        df['DATE_COL'] = pd.to_datetime(df.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        # शिफ्ट्स: DS, FD, GD, GL, DB, SG, ZA
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]

        target_date = st.date_input("📅 विश्लेषण की तारीख चुनें:", datetime.date.today())

        if st.button("🚀 एक्सट्रीम विश्लेषण शुरू करें"):
            selected_row = df[df['DATE_COL'] == target_date]
            results_list = []

            for s in shift_cols:
                logic_info, top_picks = get_extreme_logic(df, s, target_date)
                
                actual_val = "--"
                if not selected_row.empty:
                    raw_v = str(selected_row[s].values[0]).strip()
                    actual_val = f"{int(float(raw_v)):02d}" if raw_v.replace('.','',1).isdigit() else raw_v

                results_list.append({
                    "Shift": s,
                    "📍 SAME DAY": actual_val,
                    "🗓️ प्रोबेबिलिटी एनालिसिस": logic_info,
                    "🌟 टॉप 3 प्रेडिक्शन": top_picks
                })

            st.table(pd.DataFrame(results_list))
            st.balloons()

    except Exception as e:
        st.error(f"❌ गड़बड़: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
    
