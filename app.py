import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="JamesPok LFC Dashboard", layout="wide")

# ส่วนนี้ในอนาคตเราจะเปลี่ยนจาก Dict เป็นการดึงผ่าน API-Football
mock_data = {
    "2026-05-10": {
        "opponent": "Chelsea",
        "score": "1-1",
        "stats": {"Possession": [42, 58], "Shots": [11, 14], "On Target": [4, 5]},
        "news": "หงส์สะดุด! สล็อตประชดสื่อหลังโดนโห่"
    },
    "2026-05-03": {
        "opponent": "Man Utd",
        "score": "2-3",
        "stats": {"Possession": [55, 45], "Shots": [15, 10], "On Target": [6, 7]},
        "news": "แพ้คาบ้าน! เกมรับมีปัญหาอย่างหนัก"
    }
}

# --- SIDEBAR (การเลือกแมตช์) ---
st.sidebar.header("⚽ เลือกแมตช์ที่ต้องการวิเคราะห์")
selected_date = st.sidebar.selectbox("วันที่แข่งขัน", list(mock_data.keys()))
match = mock_data[selected_date]

# --- MAIN CONTENT ---
st.title(f"🔴 JamesPok LFC: Match Analysis vs {match['opponent']}")
st.subheader(match['news'])

# Layout แบ่งเป็น 2 คอลัมน์
col1, col2 = st.columns([1, 1])

with col1:
    st.metric(label="Score", value=match['score'])
    st.write("### สถิติภาพรวม")
    df_stats = pd.DataFrame({
        "Metric": list(match['stats'].keys()),
        "LFC": [v[0] for v in match['stats'].values()],
        "Opponent": [v[1] for v in match['stats'].values()]
    })
    st.table(df_stats)

with col2:
    # สร้างกราฟเปรียบเทียบ (ใช้ Plotly แทน Chart.js ใน Python)
    fig = go.Figure()
    fig.add_trace(go.Bar(name='LFC', x=list(match['stats'].keys()), y=[v[0] for v in match['stats'].values()], marker_color='#C8102E'))
    fig.add_trace(go.Bar(name=match['opponent'], x=list(match['stats'].keys()), y=[v[1] for v in match['stats'].values()], marker_color='#2563eb'))
    fig.update_layout(barmode='group', title="Comparison Chart")
    st.plotly_chart(fig, use_container_width=True)

# --- ANALYSIS SECTION ---
st.divider()
st.write("### 🗣️ วิเคราะห์สไตล์โต๊ะรก")
if match['opponent'] == "Chelsea":
    st.warning("ประเด็นร้อน: การถอด อึงูโมฮา ออกนาทีที่ 67 ทำให้โมเมนตัมพัง!")