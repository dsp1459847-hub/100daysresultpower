import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. प्योर नंबर लॉजिक इंजन ---
def get_logic_prediction(nums):
    if len(nums) < 15:
        return "Data Kam", "Data Kam"

    # A. हालिया ट्रेंड (Last 30 Draws)
    recent_pool = nums[-30:]
    counts = Counter(recent_pool)
    hot_res = f"{counts.most_common(1)[0][0]:02d}"

    # B. दहाई का गणित (Tens Analysis)
    tens = [n // 10 for n in nums[-15:]]
    most_active_ten = Counter(tens).most_common(1)[0][0]
    ten_pool = [n for n in nums[-50:] if n // 10 == most_active_ten]
    ten_res = f"{Counter(ten_pool).most_common(1)[0][0]:02d}" if ten_pool else f"{most_active_ten}X"

    # C. क्रॉस-लिंक (Mirror Logic)
    last_val = nums[-1]
    mirror = (last_val + 50) % 100
    
    # विश्लेषण टेक्स्ट तैयार करना
    analysis_text = f"🔥 HOT: {hot_res} | 📊 TENS: {ten_res} | 🔗 MIRROR: {mirror:02d}"

    # टॉप 5 मास्टर सिलेक्शन
    combined_counts = Counter(nums[-60:])
    # सबसे ज्यादा आने वाले टॉप 5 नंबर
    top_picks = [f"{n:02d}" for n, c in combined_counts.most_common(5)]
    selection = " | ".join(top_picks)

    return analysis_text, selection # अब यह केवल 2 वैल्यू वापस भेजेगा (Error Fix)

# --- 2. UI और डैशबोर्ड ---
st.set_page_config(page_title="MAYA AI: Logic Master", layout="wide")
st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🎯 MAYA AI: Logic Engine (Fixed)</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'], key="v_logic_v2")

if uploaded_file:
    try:
        file_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # कॉलम पहचानना
        date_col = df.columns[1] # Column B
        shift_cols = list(df.columns[2:9]) # Column C to I

        st.write("---")
        target_date = st.date_input("📅 विश्लेषण की तारीख चुनें:", datetime.date.today())

        if st.button("🚀 विश्लेषण शुरू करें (Pure Logic Mode)"):
            # डेटा को तारीख के हिसाब से सेट करना
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.date
            history_df = df[df[date_col] < target_date]
            today_df = df[df[date_col] == target_date]

            results_list = []
            for s in shift_cols:
                # डेटा साफ़ करना
                raw_nums = history_df[s].dropna().astype(str).str.strip()
                clean = []
                for n in raw_nums:
                    try:
                        val = int(float(n))
                        clean.append(val)
                    except: continue
                
                # प्रेडिक्शन प्राप्त करना (Error Handling Fix Here)
                logic_info, final_selection = get_logic_prediction(clean)
                
                # Same Day Check
                actual = "--"
                if not today_df.empty:
                    val = str(today_df[s].values[0]).strip()
                    try: actual = f"{int(float(val)):02d}"
                    except: actual = "--"

                results_list.append({
                    "Shift (शिफ्ट)": s,
                    "📍 उस दिन आया (SAME DAY)": actual,
                    "📊 विश्लेषण (Probability)": logic_info,
                    "🌟 टॉप 5 अंक (Selection)": final_selection
                })

            # टेबल डिस्प्ले
            st.table(pd.DataFrame(results_list))
            
            st.write("---")
            st.info("💡 **सुधार:** 'Expected 2, got 3' वाला एरर फिक्स कर दिया गया है। अब प्रेडिक्शन सांख्यिकीय 'दहाई' और 'मिरर' लॉजिक पर आधारित हैं।")
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
    
