import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. SETTINGS & CSS (จัดแต่งให้เหมือน HTML ต้นฉบับ) ---
st.set_page_config(page_title="JamesPok LFC Dashboard", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Prompt', sans-serif;
        background-color: #f8fafc;
    }
    
    /* Navbar สไตล์ไฟล์ HTML เดิม */
    .nav-container {
        background-color: #1e293b;
        padding: 15px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
        border-radius: 0 0 15px 15px;
        margin-bottom: 25px;
    }
    
    /* Card สไตล์ไฟล์ HTML เดิม */
    .stat-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border-top: 5px solid #E31B23;
        margin-bottom: 20px;
    }
    
    .vibrant-red { color: #E31B23; font-weight: bold; }
    .vibrant-blue { color: #034694; font-weight: bold; }
    </style>
    
    <div class="nav-container">
        <div style="font-size: 22px; font-weight: 700;">🔴 JamesPok <span style="font-weight: 300;">LFC News</span></div>
        <div style="font-size: 14px;">หน้าแรก | วิเคราะห์แมตช์ | สถิติเชิงลึก | ระบบโหวต</div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. DATA (จำลองข้อมูลจากแมตช์ Chelsea) ---
match_info = {
    "title": "Liverpool vs Chelsea 1-1",
    "headline": "หงส์สะดุด! สล็อตประชดสื่อหลังโดนโห่ - วิเคราะห์ความผิดพลาดนาที 67",
    "stats": {
        "ครองบอล (%)": [42, 58],
        "โอกาสยิง": [11, 14],
        "ยิงเข้ากรอบ": [4, 5],
        "เตะมุม": [6, 8],
        "ฟาวล์": [10, 12]
    }
}

# --- 3. MAIN DASHBOARD ---
st.markdown(f"### 🏟️ {match_info['title']}")
st.markdown(f"<p style='font-size: 18px; color: #64748b;'>{match_info['headline']}</p>", unsafe_allow_html=True)

# ส่วนของสถิติแบบ Card (เหมือนในไฟล์ HTML)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="stat-card"><p>ผลการแข่ง</p><h3>1 - 1</h3></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-card"><p>LFC ครองบอล</p><h3 class="vibrant-red">{match_info["stats"]["ครองบอล (%)"][0]}%</h3></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-card"><p>โอกาสยิง</p><h3>{match_info["stats"]["โอกาสยิง"][0]} ครั้ง</h3></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="stat-card"><p>Tier ข่าว</p><h3 style="color:#10b981;">Tier 1</h3></div>', unsafe_allow_html=True)

# --- 4. CHARTS (ใช้สี Red/Blue ตามต้นฉบับ) ---
st.divider()
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📊 เปรียบเทียบสถิติทีม")
    categories = list(match_info["stats"].keys())
    lfc_vals = [v[0] for v in match_info["stats"].values()]
    opp_vals = [v[1] for v in match_info["stats"].values()]

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Liverpool', x=categories, y=lfc_vals, marker_color='#E31B23'))
    fig.add_trace(go.Bar(name='Chelsea', x=categories, y=opp_vals, marker_color='#034694'))

    fig.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        margin=dict(l=20, r=20, t=20, b=20),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🕵️ เจาะประเด็นร้อน")
    st.warning("**นาทีที่ 67:** การเปลี่ยนตัวของสล็อตทำให้โมเมนตัมเปลี่ยน ทีมเสียสมดุลการครองบอลทันที")
    st.info("**สถิติหลังเกม:** แม้ครองบอลน้อยกว่า แต่โอกาสทำประตูจะแจ้ง (Big Chance) มีเท่ากันที่ 2 ครั้ง")

# --- 5. VOTING SYSTEM (ระบบที่คุณอยากได้เพิ่ม) ---
st.divider()
st.markdown("### 🗳️ แฟนบอลลิเวอร์พูลโหวต!")
vote_col1, vote_col2 = st.columns([1, 1])

with vote_col1:
    choice = st.radio("คุณพอใจกับการจัดตัวนัดนี้ไหม?", ["พอใจมาก", "พอใจ", "ไม่ค่อยพอใจ", "ควรเปลี่ยนโค้ช"])
    if st.button("ยืนยันการโหวต"):
        st.balloons()
        st.success(f"บันทึกคะแนนโหวต '{choice}' ของคุณเรียบร้อยแล้ว!")

with vote_col2:
    # โชว์กราฟผลโหวตจำลอง
    st.write("ผลโหวตรวมขณะนี้")
    st.progress(70, text="70% เห็นว่าควรเก็บนักเตะชุดนี้ไว้")
    st.progress(30, text="30% เห็นว่าควรขายออก")
