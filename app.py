import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. गैप और कटिंग एनालिसिस (Gap Analysis) ---
def get_gap_logic(df, s_name, target_date):
    try:
        # डेटा साफ़ करना
        df_clean = df[['DATE_COL', s_name]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 20:
            return "Data Kam", "N/A"

        # A. गैप लॉजिक (Gap Logic)
        # वे नंबर जो पिछले 15-20 दिनों से बिल्कुल नहीं आए (ठंडे नंबर)
        recent_15 = df_clean[df_clean['DATE'] < target_date].tail(15)['NUM'].astype(int).tolist()
        all_nums = set(range(100))
        missing_nums = list(all_nums - set(recent_15))
        
        # B. हरुफ़ रोटेशन (Digit Rotation)
        # पिछले 3 दिनों के अंदर और बाहर के अंकों को जोड़कर अगली चाल
        last_3 = recent_15[-3:]
        andar_h = [n // 10 for n in last_3]
        bahar_h = [n % 10 for n in last_3]
        
        # सबसे ज्यादा सक्रिय हरुफ़
        best_a = Counter(andar_h).most_common(1)[0][0]
        best_b = Counter(bahar_h).most_common(1)[0][0]

        # C. क्रॉस-कटिंग (Cutting)
        # पिछले नंबर की राशि और उसका जोड़
        last_val = last_3[-1]
        mirror = (last_val + 50) % 100
        total_sum = (last_val // 10 + last_val % 10) % 10

        analysis = f"🎯 सक्रिय हरुफ़: {best_a}, {best_b} | ➕ जोड़ चाल: {total_sum} | 🪞 मिरर: {mirror:02d}"
        
        # --- टॉप 3 मास्टर रोटेशन (Top 3 Only for High Focus) ---
        # 1. बेस्ट अंदर + बेस्ट बाहर
        p1 = f"{(best_a * 10) + best_b:02d}"
        # 2. पिछले नंबर का मिरर
        p2 = f"{mirror:02d}"
        # 3. जोड़ और सक्रिय हरुफ़ का मेल
        p3 = f"{(total_sum * 10) + best_b:02d}"
        
        return analysis, f"{p1} | {p2} | {p3}"

    except Exception as e:
        return f"Processing..", "N/A"

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI Gap Master", layout="wide")
st.title("🎯 MAYA AI: Gap & Rotation Logic")

uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    try:
        df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), engine='openpyxl')
        
        # तारीख कॉलम (Index 1) सेट करना
        df['DATE_COL'] = pd.to_datetime(df.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        
        # आपकी शीट के कॉलम: DS, FD, GD, GL, DB, SG, ZA
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]

        target_date = st.date_input("📅 तारीख चुनें:", datetime.date.today())

        if st.button("🚀 रोटेशन विश्लेषण शुरू करें"):
            results_list = []
            
            # SAME DAY मिलान
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
                    "🗓️ अंकों की चाल (Rotation)": logic_info,
                    "🌟 टॉप 3 रोटेशन": top_picks
                })

            st.table(pd.DataFrame(results_list))
            
            if selected_row.empty:
                st.warning(f"⚠️ तारीख '{target_date.strftime('%d/%m/%Y')}' एक्सेल में नहीं मिली।")
            
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
    
