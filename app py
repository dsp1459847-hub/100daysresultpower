import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from collections import Counter
import datetime
import io

# --- 1. एनालिसिस इंजन (Performance Tracker) ---

def get_best_prediction(clean_nums, target_date, shift_name):
    if len(clean_nums) < 30:
        return "Data Kam", "N/A"

    # पिछले 100 दिनों के डेटा का विश्लेषण
    data_pool = clean_nums[-100:] if len(clean_nums) > 100 else clean_nums
    
    # A. AI Pattern (Random Forest)
    try:
        X, y = [], []
        lookback = 5
        for i in range(lookback, len(data_pool)):
            X.append(data_pool[i-lookback:i])
            y.append(data_pool[i])
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)
        last_feat = np.array(data_pool[-lookback:]).reshape(1, -1)
        ai_res = f"{int(rf.predict(last_feat)[0]):02d}"
    except: ai_res = "--"

    # B. Frequency (Most Common)
    freq_res = f"{Counter(data_pool[-50:]).most_common(1)[0][0]:02d}"

    # C. Markov (Sequence Logic)
    last_val = data_pool[-1]
    trans = [data_pool[i+1] for i in range(len(data_pool)-1) if data_pool[i] == last_val]
    markov_res = f"{Counter(trans).most_common(1)[0][0]:02d}" if trans else "--"

    # --- विश्लेषण (कि कौन सा मेथड बेस्ट है) ---
    # यहाँ हम 'Weighted Logic' लगा रहे हैं
    # अगर दो मेथड एक ही नंबर दिखा रहे हैं, तो वो 'Super Select' है
    combined = [ai_res, freq_res, markov_res]
    counts = Counter(combined)
    most_common_num, freq = counts.most_common(1)[0]
    
    if freq >= 2 and most_common_num != "--":
        final_selection = f"🔥 {most_common_num} (Double Match)"
    else:
        final_selection = f"🎯 {ai_res} (AI Best)"

    display_text = f"🤖 AI: {ai_res}\n📈 Freq: {freq_res}\n🔗 Markov: {markov_res}"
    return display_text, final_selection

# --- 2. UI और डैशबोर्ड ---
st.set_page_config(page_title="MAYA AI: Performance Analyzer", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a73e8;'>🔮 MAYA AI: 100-Day Hit-Rate Analyzer</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'], key="v100_final")

if uploaded_file:
    try:
        df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), engine='openpyxl')
        df.columns = [str(c).strip().upper() for c in df.columns]
        date_col = df.columns[1]
        shift_cols = list(df.columns[2:9])

        target_date = st.date_input("📅 विश्लेषण की तारीख चुनें:", datetime.date.today())

        if st.button("🚀 100-Day Performance Analysis शुरू करें"):
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
                
                methods_text, final_pick = get_best_prediction(clean, target_date, s)
                
                # Same Day Actual
                actual = "--"
                if not today_df.empty:
                    try: actual = f"{int(float(today_df[s].values[0])):02d}"
                    except: actual = "--"

                results.append({
                    "Shift": s,
                    "📍 SAME DAY": actual,
                    "📊 ALL METHODS": methods_text,
                    "🌟 FINAL SELECTION": final_pick
                })

            st.table(pd.DataFrame(results))
            
            st.write("---")
            st.info("💡 **विश्लेषण का तरीका:** यह कोड पिछले 100 दिनों के AI, Frequency और Markov के रिजल्ट्स को आपस में मिलाता है। अगर दो या दो से ज्यादा तरीके एक ही नंबर बताते हैं, तो उसे **'Double Match'** मानकर 'Final Selection' में डाल दिया जाता है।")
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
