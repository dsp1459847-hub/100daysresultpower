import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. अंक गणित लॉजिक (Haruf & Digit Power) ---
def get_digit_logic(nums):
    if len(nums) < 15:
        return "Data Kam", "N/A"

    # A. अंदर और बाहर के हरुफ़ का विश्लेषण (Last 20 Draws)
    last_20 = nums[-20:]
    andar_haruf = [n // 10 for n in last_20]
    bahar_haruf = [n % 10 for n in last_20]
    
    # सबसे मजबूत अंदर का हरुफ़ (Andar)
    top_andar = Counter(andar_haruf).most_common(2)
    # सबसे मजबूत बाहर का हरुफ़ (Bahar)
    top_bahar = Counter(bahar_haruf).most_common(2)
    
    # B. जोड़ (Total/Sum) का पैटर्न
    sums = [(n // 10 + n % 10) % 10 for n in last_20]
    top_sum = Counter(sums).most_common(1)[0][0]

    analysis_text = f"🎯 ANDAR: {top_andar[0][0]} | 🎯 BAHAR: {top_bahar[0][0]} | ➕ TOTAL SUM: {top_sum}"

    # --- टॉप 5 मास्टर जोड़ियां (Top 5 Pairings) ---
    # 1. सबसे हॉट अंदर + सबसे हॉट बाहर
    p1 = (top_andar[0][0] * 10) + top_bahar[0][0]
    # 2. सेकंड हॉट अंदर + सेकंड हॉट बाहर
    p2 = (top_andar[-1][0] * 10) + top_bahar[-1][0]
    # 3. पिछले नंबर की राशि/मिरर (+55)
    p3 = (nums[-1] + 55) % 100
    # 4. टॉप सम (Sum) वाली जोड़ी
    p4 = (top_sum * 10) + top_andar[0][0]
    # 5. रिपीट अंक का लॉजिक (Last number + 10)
    p5 = (nums[-1] + 10) % 100
    
    selection = f"{p1:02d} | {p2:02d} | {p3:02d} | {p4:02d} | {p5:02d}"

    return analysis_text, selection

# --- 2. UI और फ़ॉर्मेटिंग ---
st.set_page_config(page_title="MAYA AI: Haruf Master", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a73e8;'>🔮 MAYA AI: Digit & Haruf Power</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'], key="haruf_v1")

if uploaded_file:
    try:
        df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), engine='openpyxl')
        df.columns = [str(c).strip().upper() for c in df.columns]
        date_col, shift_cols = df.columns[1], list(df.columns[2:9])

        target_date = st.date_input("📅 विश्लेषण की तारीख चुनें:", datetime.date.today())

        if st.button("🚀 अंक-गणित विश्लेषण शुरू करें"):
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.date
            history_df = df[df[date_col] < target_date]
            today_df = df[df[date_col] == target_date]

            results = []
            for s in shift_cols:
                raw = history_df[s].dropna().astype(str).str.strip()
                clean = []
                for n in raw:
                    try: clean.append(int(float(n)))
                    except: continue
                
                # अंक-गणित प्राप्त करें
                logic_info, top_picks = get_digit_logic(clean)
                
                # Same Day Check
                actual = "--"
                if not today_df.empty:
                    try: actual = f"{int(float(today_df[s].values[0])):02d}"
                    except: actual = "--"

                results.append({
                    "Shift": s,
                    "📍 उस दिन आया (SAME DAY)": actual,
                    "📊 हरुफ़ लॉजिक (Haruf)": logic_info,
                    "🌟 टॉप 5 मास्टर अंक": top_picks
                })

            st.table(pd.DataFrame(results))
            
            st.write("---")
            st.info("💡 **अंक-गणित क्या है?** यह कोड अब AI के 'अंदाजे' पर नहीं, बल्कि पिछले 20 दिनों के 'अंदर' और 'बाहर' के सबसे ज्यादा आने वाले अंकों (Haruf) को आपस में जोड़कर जोड़ियां बनाता है।")
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
    
