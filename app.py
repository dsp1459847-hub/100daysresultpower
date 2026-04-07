import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. एडवांस वीकली और डे इंजन ---
def get_advanced_analysis(df, s_name, target_date):
    try:
        # डेटा साफ़ करना
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], errors='coerce')
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna()

        if len(df_clean) < 100:
            return "Data Kam", "N/A"

        # आज का दिन (Monday, Tuesday etc.)
        target_day_name = target_date.strftime('%A')
        hindi_days = {
            'Monday': 'सोमवार', 'Tuesday': 'मंगलवार', 'Wednesday': 'बुधवार',
            'Thursday': 'वीरवार', 'Friday': 'शुक्रवार', 'Saturday': 'शनिवार', 'Sunday': 'रविवार'
        }
        day_in_hindi = hindi_days.get(target_day_name, target_day_name)

        # A. डे-वाइज एनालिसिस (Day-wise 5-Year Trend)
        # पिछले 5 सालों में जितने भी 'सोमवार' (या जो भी आज है) आए, उनका डेटा
        df_clean['DAY_NAME'] = df_clean['DATE'].dt.day_name()
        day_data = df_clean[df_clean['DAY_NAME'] == target_day_name]
        hot_day_num = Counter(day_data['NUM'].values).most_common(1)[0][0]

        # B. वीकली पैटर्न (Current Week Pulse)
        # पिछले 4 हफ्तों में इस दिन क्या-क्या आया था
        last_4_weeks = day_data[day_data['DATE'].dt.date < target_date].tail(4)
        week_history = [f"{int(n):02d}" for n in last_4_weeks['NUM'].values]

        # C. मंथली और इयरली (Legacy)
        t_day, t_month = target_date.day, target_date.month
        past_years = df_clean[(df_clean['DATE'].dt.day == t_day) & (df_clean['DATE'].dt.month == t_month)]
        yearly_res = [f"{int(n):02d}" for n in past_years['NUM'].values[-3:]]

        analysis = f"📅 **{day_in_hindi}** का HOT: {hot_day_num:02d} | 🕒 पिछले 4 हफ्तों का {day_in_hindi}: {', '.join(week_history) if week_history else '--'}"
        
        # --- टॉप 5 मास्टर प्रेडिक्शन (Day + Week + Year Logic) ---
        p1 = hot_day_num # उस दिन का सबसे बड़ा नंबर
        p2 = int(yearly_res[0]) if yearly_res else (hot_day_num + 11) % 100
        p3 = (hot_day_num + 50) % 100 # मिरर चाल
        p4 = Counter(df_clean['NUM'].values[-30:]).most_common(1)[0][0] # करंट हॉट
        p5 = (int(week_history[-1]) + 10) % 100 if week_history else 0 # वीकली रोटेशन
        
        selection = f"{p1:02d} | {p2:02d} | {p3:02d} | {p4:02d} | {p5:02d}"
        return analysis, selection

    except Exception as e:
        return f"Error: {e}", "N/A"

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI: Weekly Master", layout="wide")
st.markdown("""
    <style>
    .reportview-container .main .block-container { max-width: 100%; padding: 1rem; }
    table { width: 100% !important; font-size: 20px !important; font-weight: bold; border: 2px solid #1a73e8; }
    th { background-color: #1a73e8; color: white; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 MAYA AI: 5-Year Weekly & Day Master Scanner")

uploaded_file = st.file_uploader("📂 अपनी 5 साल की एक्सेल फ़ाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    try:
        df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), engine='openpyxl')
        shift_cols = list(df.columns[2:9]) 

        target_date = st.date_input("📅 विश्लेषण की तारीख चुनें:", datetime.date.today())

        if st.button("🚀 वीकली और डे-वाइज विश्लेषण शुरू करें"):
            # दिन का नाम हिंदी में दिखाने के लिए
            day_name = target_date.strftime('%A')
            results = []
            
            df_temp = df.copy()
            df_temp.iloc[:, 1] = pd.to_datetime(df_temp.iloc[:, 1], errors='coerce').dt.date
            today_data = df_temp[df_temp.iloc[:, 1] == target_date]

            for s in shift_cols:
                logic_info, top_picks = get_advanced_analysis(df, s, target_date)
                
                actual = "--"
                if not today_data.empty:
                    try:
                        val = today_data[s].values[0]
                        actual = f"{int(float(val)):02d}"
                    except: actual = "--"

                results.append({
                    "Shift": s,
                    "📍 SAME DAY": actual,
                    "🗓️ साप्ताहिक विश्लेषण (Weekly/Day Logic)": logic_info,
                    "🌟 टॉप 5 मास्टर अंक": top_picks
                })

            st.table(pd.DataFrame(results))
            st.info(f"💡 **नोट:** आज **{target_date.strftime('%A')}** है। यह कोड पिछले 5 सालों के सभी **{target_date.strftime('%A')}** का डेटा खंगालकर रिजल्ट दे रहा है।")
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("5 साल की एक्सेल फ़ाइल अपलोड करें। 'वार' (Day) के हिसाब से प्रेडिक्शन देखने के लिए यह सबसे बेस्ट है।")
    
