import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. सुप्रीम लॉजिक इंजन (Mirror & Family Logic) ---
def get_supreme_prediction(nums):
    if len(nums) < 10:
        return "Data Kam", "N/A"

    # A. मिरर और राशि लॉजिक (Mirror & Family)
    # 0=5, 1=6, 2=7, 3=8, 4=9
    def get_mirror(n):
        return (n + 5) % 10 if n < 10 else ((n // 10 + 5) % 10) * 10 + (n % 10 + 5) % 10

    last_val = nums[-1]
    mirror_val = get_mirror(last_val) % 100
    
    # B. दहाई की चाल (Tens Movement)
    last_5 = nums[-5:]
    most_common_ten = Counter([n // 10 for n in last_5]).most_common(1)[0][0]
    
    # C. जो़ड़ का गणित (Sum/Total)
    last_sum = (last_val // 10 + last_val % 10) % 10
    
    analysis_text = f"🪞 MIRROR: {mirror_val:02d} | 🔢 TENS: {most_active_ten if 'most_active_ten' in locals() else most_common_ten}X | ➕ SUM: {last_sum}"

    # --- टॉप 5 मास्टर सिलेक्शन (High Probability Picks) ---
    # 1. पिछला नंबर का मिरर
    # 2. सबसे ज्यादा आने वाला (Hot)
    # 3. दहाई का सबसे मजबूत अंक
    # 4. पिछले नंबर + 11 (Sequence)
    # 5. पिछले नंबर - 11 (Reverse Sequence)
    
    hot_num = Counter(nums[-50:]).most_common(1)[0][0]
    p1 = mirror_val
    p2 = hot_num
    p3 = (most_common_ten * 10) + (nums[-2] % 10) # दहाई + पिछले का हरुफ़
    p4 = (last_val + 11) % 100
    p5 = (last_val + 89) % 100 # -11 logic
    
    selection = f"{p1:02d} | {p2:02d} | {p3:02d} | {p4:02d} | {p5:02d}"

    return analysis_text, selection

# --- 2. UI और डैशबोर्ड ---
st.set_page_config(page_title="MAYA AI: Supreme Logic", layout="wide")
st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🎯 MAYA AI: Supreme Logic Engine</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'], key="supreme_v1")

if uploaded_file:
    try:
        file_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        date_col = df.columns[1] # B
        shift_cols = list(df.columns[2:9]) # C to I

        target_date = st.date_input("📅 विश्लेषण की तारीख चुनें:", datetime.date.today())

        if st.button("🚀 सुप्रीम विश्लेषण शुरू करें"):
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
                
                # लॉजिक प्राप्त करें
                logic_info, top_selection = get_supreme_prediction(clean)
                
                # Same Day Check
                actual = "--"
                if not today_df.empty:
                    try: actual = f"{int(float(today_df[s].values[0])):02d}"
                    except: actual = "--"

                results.append({
                    "Shift": s,
                    "📍 SAME DAY": actual,
                    "📊 LOGIC ANALYSIS": logic_info,
                    "🌟 TOP 5 PICKS": top_selection
                })

            st.table(pd.DataFrame(results))
            
            st.write("---")
            st.info("💡 **नया सुप्रीम लॉजिक:** यह कोड अब AI के बजाय 'मिरर', 'राशि' और 'दहाई' के पुराने पक्के सूत्रों पर काम करता है। 'Top 5 Picks' में वे अंक हैं जो पिछले अंक से सीधे जुड़े हुए हैं।")
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
                
