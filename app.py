import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. अल्टीमेट हीटमैप इंजन (Anti-Failure Logic) ---
def get_ultimate_heatmap(df, s_name, target_date):
    try:
        # डेटा को साफ़ करना (B=Index 1, s_name=Shift)
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], dayfirst=True, errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 30:
            return "Data Kam", "N/A"

        # A. आज के 'वार' (Day) का 5 साल का इतिहास
        t_day_name = target_date.strftime('%A')
        day_history = df_clean[df_clean['DATE'].apply(lambda x: x.strftime('%A')) == t_day_name]
        
        # B. ताज़ा 15 दिनों की 'दूरी' (Gap)
        recent_15 = df_clean[df_clean['DATE'] < target_date].tail(15)['NUM'].astype(int).tolist()
        last_val = recent_15[-1] if recent_15 else 0
        
        # C. मास्टर रोटेशन (Top 3)
        # लॉजिक: आज के वार का सबसे 'हॉट' नंबर + पिछले 30 दिन का सबसे 'सक्रिय' नंबर
        recent_30 = df_clean[df_clean['DATE'] < target_date].tail(30)['NUM'].astype(int).tolist()
        combined_pool = day_history['NUM'].astype(int).tolist()[-50:] + recent_30
        
        counts = Counter(combined_pool)
        top_3_list = [f"{n:02d}" for n, c in counts.most_common(3)]
        
        # हरुफ़ की चाल (Digit Trend)
        andar_h, bahar_h = last_val // 10, last_val % 10
        mirror = (last_val + 55) % 100 # राशि चाल
        
        analysis = f"🎯 आज ({t_day_name}) का HOT: {top_3_list[0]} | 🪞 राशि चाल: {mirror:02d}"
        
        # टॉप 3 प्रेडिक्शन
        p1 = top_3_list[0] # वार का राजा
        p2 = f"{mirror:02d}" # राशि का राजा
        p3 = f"{( (last_val // 10) * 10 ) + ( (last_val + 1) % 10 ):02d}" # हरुफ़ रोटेशन
        
        return analysis, f"{p1} | {p2} | {p3}"
    except:
        return "Analyzing..", "N/A"

# --- 2. UI सेटअप (Fast Loading) ---
st.set_page_config(page_title="MAYA AI Heatmap", layout="wide")
st.title("🔥 MAYA AI: 5-Year Deep Heatmap Engine")

uploaded_file = st.file_uploader("📂 अपनी 5 साल की Excel फ़ाइल अपलोड करें", type=['xlsx'], key="v13_heatmap")

if uploaded_file:
    try:
        # भारी फाइल को तेजी से लोड करना
        data_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(data_bytes), engine='openpyxl')
        
        # तारीख कॉलम (Index 1) और शिफ्ट्स पहचानना
        df['DATE_COL'] = pd.to_datetime(df.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]

        target_date = st.date_input("📅 विश्लेषण की तारीख चुनें (आज 7 अप्रैल है):", datetime.date.today())

        if st.button("🚀 अल्टीमेट डीप स्कैन शुरू करें"):
            # SAME DAY मिलान
            selected_row = df[df['DATE_COL'] == target_date]
            results_list = []

            for s in shift_cols:
                logic_info, top_picks = get_ultimate_heatmap(df, s, target_date)
                
                # 'SAME DAY' वैल्यू निकालना
                actual_val = "--"
                if not selected_row.empty:
                    raw_v = str(selected_row[s].values[0]).strip()
                    if raw_v.replace('.','',1).isdigit():
                        actual_val = f"{int(float(raw_v)):02d}"
                    else:
                        actual_val = raw_val

                results_list.append({
                    "Shift": s,
                    "📍 SAME DAY": actual_val,
                    "🗓️ 5-साल का हीटमैप (History)": logic_info,
                    "🌟 टॉप 3 मास्टर अंक": top_picks
                })

            st.table(pd.DataFrame(results_list))
            
            if not selected_row.empty:
                st.success(f"✅ 7 तारीख का डेटा मिल गया है! आप 'SAME DAY' में अपना रिजल्ट देख सकते हैं।")
            else:
                st.warning(f"⚠️ तारीख '{target_date.strftime('%d-%m-%Y')}' अभी एक्सेल में नहीं मिली।")

            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("5 साल वाली एक्सेल फ़ाइल अपलोड करें।")
    
