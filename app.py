import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. SETTINGS & FULL CSS INJECTION (แกะจาก newslfc.html) ---
st.set_page_config(page_title="เจมส์ป๊อก LFC - ขยี้ทุกประเด็นหงส์แดง", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap');
    
    /* พื้นหลังหลักของเว็บ */
    .stApp { background-color: #f8fafc; font-family: 'Noto Sans Thai', sans-serif; }
    
    /* Header สีแดงลิเวอร์พูล ตัวหนังสือทอง/ขาว [ตามสั่ง: พื้นหลังเข้มตัวหนังสืออ่อน] */
    .header-banner {
        background-color: #C8102E;
        padding: 40px 20px;
        text-align: center;
        color: #F6EB61; /* สีทอง */
        border-radius: 0 0 20px 20px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-banner h1 { color: #ffffff !important; font-weight: 800; margin-bottom: 5px; }
    .header-banner p { color: #F6EB61 !important; font-size: 1.1rem; }

    /* การ์ดสถิติ พื้นหลังขาว ตัวหนังสือดำ [ตามสั่ง: พื้นหลังอ่อนตัวหนังสือเข้ม] */
    .stat-box {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border-bottom: 4px solid #C8102E;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stat-box h4 { color: #64748b !important; margin-bottom: 10px; font-size: 14px; }
    .stat-box h2 { color: #1e293b !important; font-weight: 800; font-size: 28px; }

    /* คอนเทนเนอร์บทวิเคราะห์ */
    .analysis-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        color: #1e293b;
        border-left: 6px solid #F6EB61;
        margin-bottom: 20px;
    }
    .analysis-card h3 { color: #C8102E !important; font-weight: 700; }

    /* ล้างค่า Padding ของ Streamlit ให้เหมือนเว็บทั่วไป */
    .block-container { padding-top: 0rem; padding-bottom: 2rem; }
    </style>

    <div class="header-banner">
        <h1>🔴 เจมส์ป๊อก LFC</h1>
        <p>Dashboard ขยี้ทุกประเด็นหงส์แดง - วิเคราะห์เจาะลึกแบบ "โต๊ะรก"</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. MATCH SELECTOR (SIDEBAR) ---
st.sidebar.markdown("<h2 style='color:#C8102E;'>⚽ เมนูควบคุม</h2>", unsafe_allow_html=True)
match_day = st.sidebar.selectbox("เลือกแมตช์วิเคราะห์", ["LFC 1-1 Chelsea (10/05/2026)", "LFC 2-3 Man Utd (03/05/2026)"])

# --- 3. DASHBOARD GRID (สไตล์การ์ดจากไฟล์ HTML) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="stat-box"><h4>ผลการแข่ง</h4><h2>1 - 1</h2></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="stat-box"><h4>การครองบอล</h4><h2 style="color:#C8102E !important;">42%</h2></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="stat-box"><h4>โอกาสยิง</h4><h2>11 (4)</h2></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="stat-box"><h4>ความล้ำ</h4><h2 style="color:#F6EB61 !important;">TOP TIER</h2></div>', unsafe_allow_html=True)

# --- 4. MOMENTUM CHART (เลียนแบบ Chart.js ใน newslfc.html) ---
st.write("")
st.subheader("📊 กราฟโมเมนตัมนาทีต่อนาที")

# สร้างข้อมูลกราฟจำลองให้เหมือนในไฟล์ HTML
minutes = [0, 6, 15, 35, 45, 60, 67, 90]
momentum = [0, 8, 4, -5, 2, 5, -8, 1] # 67 นาที โมเมนตัมตกตามบทวิเคราะห์คุณ
colors = ['#1e293b' if m >= 0 else '#C8102E' for m in momentum]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=minutes, y=momentum,
    mode='lines+markers+text',
    line=dict(color='#C8102E', width=3),
    marker=dict(size=10, color=colors),
    text=["เริ่ม", "⚽ ยิงนำ", "", "⚽ เสียประตู", "", "", "⚠️ เปลี่ยนตัว", "จบเกม"],
    textposition="top center"
))

fig.update_layout(
    height=400,
    plot_bgcolor='white',
    paper_bgcolor='#f8fafc',
    yaxis=dict(showgrid=True, gridcolor='#e5e7eb', range=[-15, 15], title="Momentum Score"),
    xaxis=dict(showgrid=False, title="นาทีการแข่งขัน")
)
st.plotly_chart(fig, use_container_width=True)

# --- 5. ANALYSIS SECTION (สไตล์ "โต๊ะรก" ของแท้) ---
st.divider()
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown(f"""
    <div class="analysis-card">
        <h3>🔍 บทวิเคราะห์: หงส์สะดุดเพราะการแก้เกม?</h3>
        <p>ประเด็นที่น่าสนใจที่สุดในนัดนี้คือ <b>"นาทีที่ 67"</b> หลังจากสล็อตตัดสินใจถอดอึงูโมฮาออก 
        เราเห็นได้ชัดว่าโครงสร้างเกมรุกเปลี่ยนไปทันที เชลซีเริ่มกล้าบุกสวนกลับมากขึ้น 
        จนนำมาสู่ความผิดพลาดในแดนกลาง</p>
        <p style="margin-top:10px; font-weight:600; color:#C8102E;">💡 Key Takeaway: สล็อตต้องตอบคำถามเรื่องการจัดการพละกำลังนักเตะในช่วงท้ายเกม</p>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("### 🗳️ โหวตประเด็นร้อน")
    vote = st.radio("คุณเห็นด้วยกับการเปลี่ยนตัวนาที 67 ไหม?", ["เห็นด้วย (ต้องพักตัว)", "ไม่เห็นด้วย (เกมพัง)", "เฉยๆ"])
    if st.button("ส่งคะแนนโหวต"):
        st.success("บันทึกข้อมูลเรียบร้อย!")
        st.balloons()

# --- 6. FOOTER ---
st.markdown("""
    <div style="text-align:center; padding:30px; color:#64748b; font-size:12px;">
        © 2026 JamesPok LFC Dashboard | ข้อมูลสดจาก API-FOOTBALL
    </div>
    """, unsafe_allow_html=True)
