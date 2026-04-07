import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. एडवांस एनालिसिस इंजन (Error Fixed) ---
def get_advanced_analysis(df, s_name, target_date):
    try:
        # डेटा को साफ़ करना और तारीख को सही फॉर्मेट में लाना
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        
        # तारीख सुधार (Numeric/Float Error Fix)
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], errors='coerce')
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 50:
            return "Data Kam", "N/A", "N/A"

        # वार (Day) निकालना
        target_day_name = target_date.strftime('%A')
        hindi_days = {
            'Monday': 'सोमवार', 'Tuesday': 'मंगलवार', 'Wednesday': 'बुधवार',
            'Thursday': 'वीरवार', 'Friday': 'शुक्रवार', 'Saturday': 'शनिवार', 'Sunday': 'रविवार'
        }
        day_in_hindi = hindi_days.get(target_day_name, target_day_name)

        # A. साप्ताहिक विश्लेषण (Weekly Logic)
        day_data = df_clean[df_clean['DATE'].dt.day_name() == target_day_name]
        hot_day_num = Counter(day_data['NUM'].astype(int)).most_common(1)[0][0]
        
        # B. पकड़ नंबर (Pakad Number Logic)
        # वे नंबर जो पिछले 30 दिनों में हॉट रहे हैं पर पिछले 5 दिनों से नहीं आए
        recent_30 = df_clean[df_clean['DATE'].dt.date < target_date].tail(30)['NUM'].astype(int).tolist()
        last_5 = df_clean[df_clean['DATE'].dt.date < target_date].tail(5)['NUM'].astype(int).tolist()
        
        hot_list = [n for n, c in Counter(recent_30).most_common(10)]
        pakad_nums = [n for n in hot_list if n not in last_5][:2] # टॉप 2 पकड़ नंबर
        pakad_display = ", ".join([f"{n:02d}" for n in pakad_nums]) if pakad_nums else "--"

        analysis = f"📅 **{day_in_hindi}** का HOT: {hot_day_num:02d} | 🔥 पकड़ नंबर: {pakad_display}"
        
        # --- टॉप 5 मास्टर अंक ---
        p1 = hot_day_num
        p2 = pakad_nums[0] if pakad_nums else (hot_day_num + 55) % 100
        p3 = (hot_day_num + 50) % 100 # मिरर
        p4 = Counter(recent_30).most_common(1)[0][0] # करंट हॉट
        p5 = (int(last_5[-1]) + 11) % 100 if last_5 else 0 
        
        selection = f"{p1:02d} | {p2:02d} | {p3:02d} | {p4:02d} | {p5:02d}"
        return analysis, selection, pakad_display

    except Exception as e:
        return f"Error: {str(e)}", "N/A", "N/A"

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI: Weekly Pakad", layout="wide")
st.markdown("""
    <style>
    .reportview-container .main .block-container { max-width: 100%; padding: 1rem; }
    table { width: 100% !important; font-size: 18px !important; font-weight: bold; }
    th { background-color: #1a73e8; color: white; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 MAYA AI: Weekly Master & Pakad Logic")

uploaded_file = st.file_uploader("📂 अपनी 5 साल की एक्सेल फ़ाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    try:
        df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), engine='openpyxl')
        shift_cols = list(df.columns[2:9]) 

        target_date = st.date_input("📅 विश्लेषण की तारीख चुनें:", datetime.date.today())

        if st.button("🚀 विश्लेषण शुरू करें"):
            results = []
            
            # तारीख मिलान (Same Day)
            df_temp = df.copy()
            df_temp.iloc[:, 1] = pd.to_datetime(df_temp.iloc[:, 1], errors='coerce').dt.date
            today_data = df_temp[df_temp.iloc[:, 1] == target_date]

            for s in shift_cols:
                logic_info, top_picks, pakad = get_advanced_analysis(df, s, target_date)
                
                actual = "--"
                if not today_data.empty:
                    try:
                        val = today_data[s].values[0]
                        actual = f"{int(float(val)):02d}"
                    except: actual = "--"

                results.append({
                    "Shift": s,
                    "📍 SAME DAY": actual,
                    "🗓️ साप्ताहिक व पकड़ विश्लेषण": logic_info,
                    "🌟 टॉप 5 मास्टर अंक": top_picks
                })

            st.table(pd.DataFrame(results))
            st.info(f"💡 आज **{target_date.strftime('%A')}** है। कोड ने पिछले 5 सालों के सभी **{target_date.strftime('%A')}** और ताज़ा 'पकड़ नंबरों' का विश्लेषण किया है।")
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("5 साल की एक्सेल फ़ाइल अपलोड करें। 'पकड़ नंबर' देखने के लिए डेटा का पुराना होना ज़रूरी है।")
            
