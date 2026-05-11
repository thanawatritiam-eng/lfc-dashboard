import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIG & STYLE (ดึงความสวยจาก HTML เดิม) ---
st.set_page_config(page_title="JamesPok LFC Dashboard", layout="wide")

# ใช้ CSS เพื่อทำ Navbar และปรับแต่งสี (ดึงโทนสีจากไฟล์เดิมของคุณ)
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .nav-bar {
        background-color: #1e293b;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        color: white;
    }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    <div class="nav-bar">
        <div style="font-weight:bold; font-size:20px;">🔴 JamesPok LFC Dashboard</div>
        <div>หน้าแรก | วิเคราะห์แมตช์ | ระบบโหวต | เกี่ยวกับเรา</div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. DATA (จำลองข้อมูล) ---
mock_data = {
    "2026-05-10": {
        "opponent": "Chelsea",
        "score": "1-1",
        "stats": {"Possession": [42, 58], "Shots": [11, 14], "On Target": [4, 5]},
        "news": "หงส์สะดุด! สล็อตประชดสื่อหลังโดนโห่"
    }
}

# --- 3. SIDEBAR ---
st.sidebar.header("⚽ เมนูควบคุม")
selected_date = st.sidebar.selectbox("เลือกแมตช์", list(mock_data.keys()))
match = mock_data[selected_date]

# --- 4. MAIN DASHBOARD ---
st.header(f"วิเคราะห์แมตช์ vs {match['opponent']}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("ผลการแข่งขัน", match['score'])
with col2:
    st.metric("Possession", f"{match['stats']['Possession'][0]}%")
with col3:
    st.metric("โอกาสยิง", match['stats']['Shots'][0])

# ส่วนของกราฟ (ดึงสไตล์จากไฟล์ HTML เดิม)
st.subheader("📊 เปรียบเทียบสถิติเชิงลึก")
fig = go.Figure()
fig.add_trace(go.Bar(name='LFC', x=list(match['stats'].keys()), y=[v[0] for v in match['stats'].values()], marker_color='#E31B23'))
fig.add_trace(go.Bar(name=match['opponent'], x=list(match['stats'].keys()), y=[v[1] for v in match['stats'].values()], marker_color='#034694'))
fig.update_layout(barmode='group', height=400, template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# --- 5. ANALYSIS SECTION (สไตล์โต๊ะรก) ---
with st.expander("🔍 อ่านบทวิเคราะห์ฉบับเต็ม"):
    st.write(f"**หัวข้อ:** {match['news']}")
    st.info("วิเคราะห์: เกมนี้ลิเวอร์พูลดูตื้อๆ ไปหน่อย โดยเฉพาะนาทีที่ 67 หลังจากถอดตัวรุกออกทำให้โมเมนตัมเปลี่ยนทันที...")

# --- 6. VOTING SYSTEM (ไอเดียใหม่ที่คุณอยากได้) ---
st.divider()
st.subheader("🗳️ แฟนบอลคิดอย่างไร?")
vote = st.radio("คุณเห็นด้วยกับการแก้เกมของโค้ชในนัดนี้ไหม?", ["เห็นด้วย", "ไม่เห็นด้วย", "เฉยๆ"])
if st.button("ส่งคะแนนโหวต"):
    st.success(f"ขอบคุณสำหรับคะแนนโหวต! (ระบบบันทึกว่าคุณเลือก: {vote})")
