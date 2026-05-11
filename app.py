import streamlit as st
import plotly.graph_objects as go

# --- 1. SETTINGS & FORCE CSS (บังคับให้เหมือน HTML ต้นฉบับ) ---
st.set_page_config(page_title="เจมส์ป๊อก LFC - Dashboard", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap');
    
    /* ลบส่วนเกินของ Streamlit ให้หน้าเว็บเต็มจอเป๊ะ */
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stHeader"] { display: none; }
    div[data-testid="stToolbar"] { display: none; }
    
    body, .stApp {
        font-family: 'Noto Sans Thai', sans-serif;
        background-color: #f8fafc;
    }

    /* NAVBAR ด้านบน ตามรูป image_a31a1a.png */
    .nav-custom {
        background-color: #0f172a;
        padding: 0;
        display: flex;
        justify-content: center;
        position: sticky;
        top: 0;
        z-index: 9999;
    }
    .nav-item {
        color: #ffffff;
        padding: 15px 25px;
        text-decoration: none;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        border-bottom: 4px solid transparent;
    }
    .nav-item:hover { background-color: #1e293b; color: #F6EB61; }
    .nav-active { border-bottom: 4px solid #C8102E; color: #F6EB61; }

    /* HEADER BANNER (สีแดงลิเวอร์พูล) */
    .header-banner {
        background-color: #C8102E;
        color: #ffffff;
        padding: 60px 20px;
        text-align: center;
        border-bottom: 8px solid #F6EB61;
    }
    .header-banner h1 { color: #ffffff !important; font-size: 3.5rem; font-weight: 800; margin: 0; }
    .header-banner p { color: #F6EB61 !important; font-size: 1.2rem; margin-top: 10px; font-weight: 600; }

    /* GRID สถิติ 4 ช่อง */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        max-width: 1200px;
        margin: -40px auto 30px auto;
        padding: 0 20px;
    }
    .stat-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border-bottom: 5px solid #C8102E;
    }
    .stat-card h4 { color: #64748b !important; font-size: 0.9rem; margin-bottom: 10px; }
    .stat-card h2 { color: #1e293b !important; font-size: 2.2rem; font-weight: 800; margin: 0; }
    .gold-text { color: #F6EB61 !important; background: #1e293b; padding: 5px 15px; border-radius: 8px; display: inline-block; }

    /* คอนเทนเนอร์สีเข้ม (พื้นหลังดำ ตัวหนังสือทอง) [ตามสั่งเป๊ะ] */
    .content-dark {
        background-color: #1e293b;
        color: #F6EB61;
        padding: 40px;
        border-radius: 20px;
        max-width: 1160px;
        margin: 20px auto;
        border-right: 12px solid #C8102E;
    }
    .content-dark h3 { color: #ffffff !important; font-size: 1.8rem; margin-bottom: 15px; border-bottom: 2px solid #C8102E; display: inline-block; }
    .content-dark p { color: #F6EB61 !important; font-size: 1.1rem; line-height: 1.8; }

    /* คอนเทนเนอร์สีอ่อน (พื้นหลังขาว ตัวหนังสือดำ) [ตามสั่งเป๊ะ] */
    .content-light {
        background-color: #ffffff;
        color: #1e293b;
        padding: 40px;
        border-radius: 20px;
        max-width: 1160px;
        margin: 20px auto;
        border-left: 12px solid #C8102E;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    .content-light h3 { color: #C8102E !important; font-size: 1.8rem; margin-bottom: 15px; }
    .content-light p { color: #1e293b !important; font-size: 1.1rem; line-height: 1.8; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAVIGATION LOGIC (เลียนแบบ Navbar ด้านบน) ---
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

# บังคับสร้าง Navbar ด้วยปุ่ม Streamlit แต่แต่งให้เหมือน Web Nav
st.markdown('<div class="nav-custom">', unsafe_allow_html=True)
nav_cols = st.columns([1,1,1,1,4]) # แบ่งพื้นที่ให้ปุ่มเรียงชิดซ้าย
with nav_cols[0]:
    if st.button("📊 Dashboard"): st.session_state.page = "Dashboard"
with nav_cols[1]:
    if st.button("🧠 แทคติก"): st.session_state.page = "แทคติก"
with nav_cols[2]:
    if st.button("💬 ข่าวสาร"): st.session_state.page = "ข่าวสาร"
with nav_cols[3]:
    if st.button("🗳️ โหวต"): st.session_state.page = "โหวต"
st.markdown('</div>', unsafe_allow_html=True)

# --- 3. HEADER & CONTENT BY PAGE ---
if st.session_state.page == "Dashboard":
    # HEADER
    st.markdown("""
        <div class="header-banner">
            <h1>🔴 เจมส์ป๊อก LFC</h1>
            <p>ขยี้ทุกประเด็นหงส์แดง - วิเคราะห์เจาะลึกแบบ "โต๊ะรก"</p>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><h4>ผลการแข่ง</h4><h2>1 - 1</h2></div>
            <div class="stat-card"><h4>การครองบอล</h4><h2 style="color:#C8102E !important;">42%</h2></div>
            <div class="stat-card"><h4>โอกาสยิง (เข้ากรอบ)</h4><h2>11 (4)</h2></div>
            <div class="stat-card"><h4>คะแนนความล้ำ</h4><h2 class="gold-text">9.5</h2></div>
        </div>
        """, unsafe_allow_html=True)

    # CONTENT 1: DARK BOX (ตามสั่ง: พื้นหลังดำ ตัวหนังสือทอง)
    st.markdown("""
        <div class="content-dark">
            <h3>🔥 ขยี้ประเด็นร้อน: นาทีที่ 67 คือคำตอบ?</h3>
            <p>จากข้อมูลในไฟล์ต้นฉบับ การเปลี่ยนตัวเอา "อึงูโมฮา" ออกในนาทีที่ 67 ส่งผลให้โมเมนตัมของทีมตกลงอย่างเห็นได้ชัด 
            นี่คือ Content Pillar สำคัญที่คุณต้องนำไปเล่าในช่องเพื่อดึงยอด Engagement!</p>
        </div>
        """, unsafe_allow_html=True)

    # กราฟโมเมนตัม (ดึงข้อมูลนาทีที่ 6, 35, 67 มาเป๊ะๆ)
    st.markdown('<div style="max-width:1160px; margin:auto;">', unsafe_allow_html=True)
    st.subheader("📊 กราฟโมเมนตัมนาทีต่อนาที")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0, 6, 15, 35, 45, 60, 67, 90], 
        y=[0, 10, 5, -8, 2, 6, -10, 2],
        mode='lines+markers+text',
        line=dict(color='#C8102E', width=4),
        text=["", "⚽ กราเฟนแบร์ก", "", "⚽ เอ็นโซ่", "พักครึ่ง", "", "⚠️ ถอดอึงูโมฮา", "จบเกม"],
        textposition="top center"
    ))
    fig.update_layout(height=400, plot_bgcolor='white', yaxis=dict(range=[-15, 15]))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # CONTENT 2: LIGHT BOX (ตามสั่ง: พื้นหลังขาว ตัวหนังสือดำ)
    st.markdown("""
        <div class="content-light">
            <h3>🧠 Tactical Insight: การแก้เกมของสล็อต</h3>
            <p>ลิเวอร์พูลในนัดนี้เล่นระบบเน้นการบีบพื้นที่ แต่ปัญหาเกิดขึ้นเมื่อพละกำลังในช่วงท้ายเกมลดลง 
            ทำให้เชลซีมีโอกาสสวนกลับจนได้ประตูตีเสมอ สถิติโอกาสยิง 11 ครั้งเข้ากรอบเพียง 4 ครั้งคือสิ่งที่ต้องปรับปรุง</p>
        </div>
        """, unsafe_allow_html=True)

else:
    # หน้าอื่นๆ ให้แสดงแค่หัวข้อเพื่อให้เห็นว่าเปลี่ยนหน้าได้จริง
    st.markdown(f"""<div class="header-banner"><h1>🔴 {st.session_state.page}</h1></div>""", unsafe_allow_html=True)
    st.markdown(f'<div class="content-light"><h3>กำลังเตรียมข้อมูลหน้า {st.session_state.page}...</h3></div>', unsafe_allow_html=True)

# FOOTER
st.markdown('<div style="text-align:center; padding:40px; color:#64748b;">© 2026 JamesPok LFC Dashboard</div>', unsafe_allow_html=True)
