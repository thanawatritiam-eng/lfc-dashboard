import streamlit as st
import plotly.graph_objects as go

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="เจมส์ป๊อก LFC - Dashboard", layout="wide")

# --- 2. CUSTOM CSS (แกะสไตล์จาก newslfc.html เป๊ะๆ) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap');
    
    /* ลบส่วนเกินของ Streamlit ออกให้หมดเพื่อให้เหมือนหน้าเว็บจริง */
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stHeader"] { display: none; }
    
    body, .stApp {
        font-family: 'Noto Sans Thai', sans-serif;
        background-color: #f1f5f9; /* พื้นหลังเทาอ่อนเพื่อให้ Content สีขาวลอยเด่น */
    }

    /* Navbar ด้านบน (สีน้ำเงินเข้ม ตัวหนังสือสีขาว) */
    .nav-bar-wrapper {
        background-color: #0f172a;
        padding: 15px 0;
        display: flex;
        justify-content: center;
        gap: 20px;
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Header แบนเนอร์ (สีแดงลิเวอร์พูล ตัวหนังสือทอง/ขาว) */
    .header-banner {
        background-color: #C8102E;
        color: #ffffff;
        padding: 50px 20px;
        text-align: center;
        border-bottom: 8px solid #F6EB61; /* เส้นสีทอง */
    }
    .header-banner h1 { color: #ffffff !important; font-size: 3.5rem; font-weight: 800; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .header-banner p { color: #F6EB61 !important; font-size: 1.3rem; margin-top: 10px; font-weight: 600; }

    /* การ์ดสถิติ (พื้นหลังขาว ตัวหนังสือดำเข้ม) [แก้ปัญหาเรื่องการอ่าน] */
    .stat-card {
        background: white;
        padding: 30px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-top: 6px solid #C8102E;
        transition: transform 0.2s;
    }
    .stat-card:hover { transform: translateY(-5px); }
    .stat-card h4 { color: #475569 !important; font-size: 1rem; margin-bottom: 10px; }
    .stat-card h2 { color: #1e293b !important; font-size: 2.5rem; font-weight: 800; margin: 0; }

    /* คอนเทนเนอร์สีเข้ม (พื้นหลังดำ ตัวหนังสือทอง) [ตามสั่ง] */
    .dark-box {
        background-color: #1e293b;
        color: #F6EB61;
        padding: 35px;
        border-radius: 20px;
        margin: 25px 0;
        border-right: 10px solid #C8102E;
    }
    .dark-box h3 { color: #ffffff !important; font-size: 1.8rem; margin-bottom: 15px; border-bottom: 2px solid #C8102E; padding-bottom: 10px; }
    .dark-box p { color: #F6EB61 !important; font-size: 1.1rem; line-height: 1.8; }

    /* คอนเทนเนอร์สีอ่อน (พื้นหลังขาว ตัวหนังสือดำ) [ตามสั่ง] */
    .light-box {
        background-color: #ffffff;
        color: #1e293b;
        padding: 35px;
        border-radius: 20px;
        margin: 25px 0;
        border-left: 10px solid #C8102E;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .light-box h3 { color: #C8102E !important; font-size: 1.8rem; margin-bottom: 15px; }
    .light-box p { color: #334155 !important; font-size: 1.1rem; line-height: 1.8; }

    /* ปุ่มกด Navbar ของ Streamlit ให้ดูเหมือนปุ่มจริง */
    div.stButton > button {
        background-color: #1e293b;
        color: white;
        border: 2px solid #F6EB61;
        border-radius: 8px;
        padding: 10px 20px;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #C8102E;
        border-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC: MULTI-PAGE NAVIGATION (Navbar ด้านบน) ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📊 Dashboard"

# จำลอง Navbar ด้วยคอลัมน์ด้านบน
st.markdown('<div class="nav-bar-wrapper">', unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
with nav_col1:
    if st.button("📊 Dashboard"): st.session_state.current_page = "📊 Dashboard"
with nav_col2:
    if st.button("🧠 แทคติก"): st.session_state.current_page = "🧠 แทคติก"
with nav_col3:
    if st.button("💬 ข่าวสาร"): st.session_state.current_page = "💬 ข่าวสาร"
with nav_col4:
    if st.button("🗳️ โหวต"): st.session_state.current_page = "🗳️ โหวต"
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. HEADER ---
st.markdown(f"""
    <div class="header-banner">
        <h1>🔴 เจมส์ป๊อก LFC</h1>
        <p>Dashboard วิเคราะห์เจาะลึก: {st.session_state.current_page}</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. PAGE CONTENT ---
st.markdown('<div style="max-width: 1200px; margin: auto; padding: 40px 20px;">', unsafe_allow_html=True)

if st.session_state.current_page == "📊 Dashboard":
    # --- สถิติ (Grid 4 ช่อง) ---
    st.markdown("### 🏟️ สถิติแมตช์ล่าสุด: Liverpool vs Chelsea")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    with stat_col1:
        st.markdown('<div class="stat-card"><h4>ผลการแข่งขัน</h4><h2>1 - 1</h2></div>', unsafe_allow_html=True)
    with stat_col2:
        st.markdown('<div class="stat-card"><h4>ครองบอล</h4><h2 style="color:#C8102E;">42%</h2></div>', unsafe_allow_html=True)
    with stat_col3:
        st.markdown('<div class="stat-card"><h4>ยิงเข้ากรอบ</h4><h2>4 / 11</h2></div>', unsafe_allow_html=True)
    with stat_col4:
        st.markdown('<div class="stat-card"><h4>ระดับความล้ำ</h4><h2 style="color:#f59e0b;">TOP TIER</h2></div>', unsafe_allow_html=True)

    # --- กราฟโมเมนตัม (จาก newslfc.html) ---
    st.markdown("### 📊 โมเมนตัมการแข่งขัน (Minute by Minute)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0, 6, 35, 45, 60, 67, 90], 
        y=[0, 10, -5, 2, 6, -10, 2],
        mode='lines+markers+text',
        line=dict(color='#C8102E', width=4),
        text=["เริ่ม", "⚽ กราเฟนแบร์ก", "⚽ เอ็นโซ่", "พักครึ่ง", "", "⚠️ เปลี่ยนตัว", "จบ"],
        textposition="top center"
    ))
    fig.update_layout(height=400, plot_bgcolor='white', yaxis=dict(title="Momentum", range=[-15, 15]))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
        <div class="dark-box">
            <h3>🔥 ขยี้ประเด็นร้อน: นาทีที่ 67 คือคำตอบ?</h3>
            <p>จากการวิเคราะห์พบว่าหลังจากถอดตัวรุกที่กดดันแดนหน้าออก โมเมนตัมของลิเวอร์พูลตกลงทันที (ดูได้จากกราฟด้านบน) 
            นี่คือข้อมูลสำคัญที่คุณเจมส์ป๊อกสามารถนำไปตัดคลิปขยี้ใน TikTok ได้ว่า "สล็อตพลาดหรือตั้งใจ?"</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == "🧠 แทคติก":
    st.markdown("""
        <div class="light-box">
            <h3>🧠 Tactical Analysis: ระบบ 4-2-3-1 ของสล็อต</h3>
            <p>ในนัดนี้ลิเวอร์พูลพยายามใช้การเพรสซิ่งแดนบน (High Press) แต่ทว่าการยืนตำแหน่งของคู่กลางยังทับซ้อนกันในบางจังหวะ 
            ทำให้เชลซีมีพื้นที่ในการสวนกลับเร็ว (Counter Attack) ได้ง่ายในช่วงครึ่งหลัง</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == "💬 ข่าวสาร":
    st.markdown("""
        <div class="dark-box">
            <h3>📰 สรุปข่าวจาก Tier 1</h3>
            <p>โรมาโน่รายงาน: ลิเวอร์พูลกำลังเจรจาขยายสัญญากับแกนหลัก 3 คนในช่วงซัมเมอร์นี้ คาดว่าจะมีความชัดเจนหลังจบฤดูกาล</p>
        </div>
        <div class="light-box">
            <h3>💬 บทสัมภาษณ์หลังเกม</h3>
            <p>"เราพอใจกับ 1 แต้มในวันนี้ แต่เราควรจะเด็ดขาดกว่านี้ในจังหวะสุดท้าย" - อาร์เน สล็อต</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == "🗳️ โหวต":
    st.markdown('<div class="light-box">', unsafe_allow_html=True)
    st.subheader("🗳️ Man of the Match (Fan Vote)")
    m_choice = st.radio("เลือกนักเตะที่คุณประทับใจที่สุด:", ["Salah", "Gravenberch", "Van Dijk", "Konate"])
    if st.button("ยืนยันการโหวต"):
        st.balloons()
        st.success(f"ขอบคุณครับ! คุณเลือก {m_choice} เป็น MOM นัดนี้")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
