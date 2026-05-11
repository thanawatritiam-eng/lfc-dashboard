import streamlit as st
import plotly.graph_objects as go

# --- 1. CONFIG & CUSTOM CSS (แกะดีไซน์จาก newslfc.html 100%) ---
st.set_page_config(page_title="เจมส์ป๊อก LFC - Dashboard", layout="wide")

# CSS เพื่อบังคับให้หน้าตาเป๊ะและแก้ปัญหาเรื่องสีฟอนต์ตามสั่ง
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap');
    
    /* ลบขอบขาวของ Streamlit */
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stHeader"] { display: none; }
    
    body, .stApp {
        font-family: 'Noto Sans Thai', sans-serif;
        background-color: #f8fafc;
    }

    /* Navbar ด้านบน (สไตล์พรีเมียม) */
    .nav-container {
        background-color: #0f172a;
        padding: 10px 0;
        text-align: center;
        position: sticky;
        top: 0;
        z-index: 999;
    }

    /* Header สีแดงลิเวอร์พูล */
    .header-banner {
        background-color: #C8102E;
        padding: 40px 20px;
        text-align: center;
        border-bottom: 6px solid #F6EB61;
    }
    .header-banner h1 { color: #ffffff !important; font-size: 3rem; font-weight: 800; margin: 0; }
    .header-banner p { color: #F6EB61 !important; font-size: 1.2rem; }

    /* การ์ดสถิติ (พื้นหลังขาว ตัวหนังสือดำ) [ตามสั่ง] */
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-bottom: 4px solid #C8102E;
        color: #1e293b;
    }
    
    /* คอนเทนเนอร์สีเข้ม (พื้นหลังดำ/น้ำเงิน ตัวหนังสือทอง) [ตามสั่ง] */
    .dark-panel {
        background-color: #1e293b;
        color: #F6EB61;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
    }
    .dark-panel h3 { color: #ffffff !important; }

    /* คอนเทนเนอร์สีอ่อน (พื้นหลังขาว ตัวหนังสือดำ) [ตามสั่ง] */
    .light-panel {
        background-color: #ffffff;
        color: #1e293b;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        border-left: 8px solid #C8102E;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNCTIONAL NAVBAR (ส่วนที่เปลี่ยนหน้าได้จริงๆ) ---
# เราจะใช้ st.radio แต่แต่ง CSS ให้เหมือน Navbar ด้านบน
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
selected_page = st.sidebar.radio(
    "🧭 เมนูหลัก",
    ["📊 Dashboard", "🧠 วิเคราะห์แทคติก", "💬 ข่าวลือ & บทสัมภาษณ์", "🗳️ ระบบโหวตสมาชิก"],
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

# --- 3. HEADER SECTION ---
st.markdown(f"""
    <div class="header-banner">
        <h1>🔴 เจมส์ป๊อก LFC</h1>
        <p>คุณกำลังอยู่ที่หน้า: {selected_page}</p>
    </div>
    """, unsafe_allow_html=True)

# --- 4. PAGE LOGIC (แยกเนื้อหาแต่ละหน้า) ---
st.markdown('<div style="max-width: 1200px; margin: auto; padding: 20px;">', unsafe_allow_html=True)

if selected_page == "📊 Dashboard":
    # --- หน้า Dashboard (เหมือนรูป image_a31a1a.png) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stat-card"><h4>ผลการแข่ง</h4><h2>1 - 1</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card"><h4>ครองบอล</h4><h2 style="color:#C8102E;">42%</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-card"><h4>โอกาสยิง</h4><h2>11 (4)</h2></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stat-card"><h4>ความล้ำ</h4><h2 style="color:#F6EB61; background:#1e293b; border-radius:8px;">TOP TIER</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="dark-panel">
            <h3>🔥 ประเด็นร้อน: ทำไมโมเมนตัมถึงตก?</h3>
            <p>วิเคราะห์นาทีที่ 67: การถอดตัวรุกออกทำให้เชลซีกล้าเปิดเกมแลก นี่คือจุดที่คุณต้องเอาไปทำคลิปขยี้ใน TikTok!</p>
        </div>
        """, unsafe_allow_html=True)

elif selected_page == "🧠 วิเคราะห์แทคติก":
    st.markdown("""
        <div class="light-panel">
            <h3 style="color:#C8102E;">🧠 เจาะลึกแผนการเล่น (Tactical Insight)</h3>
            <p>สล็อตใช้ระบบ 4-2-3-1 ในครึ่งแรก แต่ปัญหาคือการยืนตำแหน่งของฟูลแบ็กที่ลอยสูงเกินไป...</p>
        </div>
        """, unsafe_allow_html=True)
    # ใส่กราฟเรดาร์ที่นี่
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[8, 5, 8, 9, 7], theta=['รุก', 'รับ', 'กลาง', 'เพรส', 'สวน'], fill='toself', line_color='#C8102E'))
    st.plotly_chart(fig, use_container_width=True)

elif selected_page == "💬 ข่าวลือ & บทสัมภาษณ์":
    st.markdown("""
        <div class="dark-panel">
            <h3>💬 สรุปบทสัมภาษณ์หลังเกม</h3>
            <p>"เราไม่ได้ผลการแข่งขันที่ต้องการ แต่เราเห็นสัญญาณที่ดี" - อาร์เน สล็อต</p>
        </div>
        <div class="light-panel">
            <h3>📰 ข่าวลือตลาดซื้อขาย</h3>
            <p>ลิเวอร์พูลเตรียมยื่นข้อเสนอซื้อกองกลางคนใหม่จากบุนเดสลีกา...</p>
        </div>
        """, unsafe_allow_html=True)

elif selected_page == "🗳️ ระบบโหวตสมาชิก":
    st.markdown('<div class="light-panel">', unsafe_allow_html=True)
    st.subheader("🗳️ คุณคิดว่าใครคือ Man of the Match?")
    vote = st.radio("เลือกนักเตะ:", ["Salah", "Van Dijk", "Diaz", "Gravenberch"])
    if st.button("ส่งผลโหวต"):
        st.balloons()
        st.success("ขอบคุณสำหรับผลโหวต! ข้อมูลนี้จะนำไปโชว์สปอนเซอร์ต่อไป")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
