import streamlit as st
import plotly.graph_objects as go
import json

# --- 1. CONFIG & CSS (ลบขอบขาว บังคับสีให้เหมือนต้นฉบับ) ---
st.set_page_config(page_title="เจมส์ป๊อก LFC Dashboard", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap');
    
    /* ปรับจอกว้างเต็มพิกัด */
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stHeader"] { display: none; }
    
    body, .stApp {
        font-family: 'Noto Sans Thai', sans-serif;
        background-color: #f8fafc;
    }

    /* สไตล์ Banner สีแดงลิเวอร์พูล */
    .header-banner {
        background-color: #C8102E;
        color: #ffffff;
        padding: 50px 20px;
        text-align: center;
        border-bottom: 6px solid #F6EB61;
    }
    .py-badge {
        background: #1d4ed8; color: white; font-size: 12px; 
        padding: 2px 8px; border-radius: 10px; margin-left: 10px;
    }

    /* กล่องสถิติ 4 ช่อง */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        max-width: 1100px;
        margin: -30px auto 30px auto;
        padding: 0 20px;
    }
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-bottom: 4px solid #C8102E;
    }

    /* กล่องเนื้อหาแบบ ดำ-ทอง */
    .content-dark {
        background-color: #1e293b;
        color: #F6EB61;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 20px;
        border-right: 10px solid #C8102E;
    }
    
    /* กล่องเนื้อหาแบบ ขาว-แดง */
    .content-light {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 20px;
        border-left: 10px solid #C8102E;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* ปุ่ม Navbar แบบ Streamlit Hack */
    .stButton>button {
        width: 100%;
        border-radius: 0;
        border: none;
        background-color: #0f172a;
        color: white;
        height: 50px;
    }
    .stButton>button:hover { background-color: #C8102E; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LAYER (ดึงจากไฟล์ newslfc.html มาครบถ้วน) ---
if 'page' not in st.session_state:
    st.session_state.page = "หน้าแรก"

# --- 3. NAVIGATION (แถบบนสุด) ---
nav_cols = st.columns([1,1,1])
with nav_cols[0]:
    if st.button("🔴 ประเด็นร้อน"): st.session_state.page = "หน้าแรก"
with nav_cols[1]:
    if st.button("📊 สถิติเจาะลึก"): st.session_state.page = "สถิติ"
with nav_cols[2]:
    if st.button("🧠 วิเคราะห์แทคติก"): st.session_state.page = "แทคติก"

# --- 4. MAIN CONTENT ---

# ส่วนหัวเหมือนกันทุกหน้า
st.markdown("""
    <div class="header-banner">
        <h1 style="font-weight:800; font-size:3rem; margin:0;">เจมส์ป๊อก LFC <span class="py-badge">STREAMLIT</span></h1>
        <p style="color:#F6EB61; font-weight:600;">ขยี้ทุกประเด็นหงส์แดง - วิเคราะห์สไตล์โต๊ะรก</p>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.page == "หน้าแรก":
    # กล่องสถิติสรุป (Verified Data)
    st.markdown("""
        <div class="stats-grid">
            <div class="stat-card"><p style="color:gray; font-size:14px; margin:0;">ผลการแข่ง</p><h2 style="margin:0;">LIV 1-1 CHE</h2></div>
            <div class="stat-card"><p style="color:gray; font-size:14px; margin:0;">ครองบอล</p><h2 style="color:#C8102E; margin:0;">42%</h2></div>
            <div class="stat-card"><p style="color:gray; font-size:14px; margin:0;">โอกาสยิง</p><h2 style="margin:0;">11 (4)</h2></div>
            <div class="stat-card"><p style="color:gray; font-size:14px; margin:0;">ความล้ำ</p><h2 style="background:#1e293b; color:#F6EB61; border-radius:5px; margin:0;">9.5</h2></div>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
            <div class="content-dark">
                <h2 style="color:white; border-bottom:2px solid #C8102E; display:inline-block;">🔥 ประเด็นนาทีที่ 67</h2>
                <p style="font-size:1.1rem; line-height:1.6;">สล็อตถอด <b>"อึงูโมฮา"</b> ออกในนาทีที่ 67 คือจุดเปลี่ยนสำคัญ! 
                จากสถิติจะเห็นว่าหลังจากนั้นโมเมนตัมเกมรุกตกลงอย่างเห็นได้ชัด แฟนบอลแอนฟิลด์ถึงกับส่งเสียงโห่ใส่แทคติกนี้</p>
            </div>
            """, unsafe_allow_html=True)
        
        # กราฟโมเมนตัม (Plotly) - ข้อมูลเป๊ะตาม HTML
        st.subheader("📊 กราฟโมเมนตัม (บวก=หงส์บุก / ลบ=สิงห์บุก)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[0, 6, 15, 35, 45, 60, 67, 90], 
            y=[0, 10, 5, -8, 2, 6, -10, 2],
            mode='lines+markers+text',
            line=dict(color='#C8102E', width=4, shape='spline'),
            text=["", "⚽ กราเฟนแบร์ก", "", "⚽ เอ็นโซ่", "พักครึ่ง", "", "⚠️ เปลี่ยนตัว", "จบเกม"],
            textposition="top center"
        ))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='white')
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""
            <div class="content-light">
                <h3 style="color:#C8102E;">💬 เจมส์ป๊อกขยี้</h3>
                <p style="font-size:0.95rem;"><b>สล็อต:</b> "พวกคุณคิดว่าผมสั่งทีมถอยไปรับเหรอ?" <br><br>
                กุนซือตอบแบบประชดหลังโดนถามเรื่องความป๊อดในช่วงท้ายเกม! เกมนี้ฟาน ไดจ์ค และโซบอสซ์ไล ยิงชนเสาชนคานไปคนละที ไม่งั้นชนะไปแล้ว</p>
            </div>
            
            <div class="content-light" style="background:#fef2f2; border-color:#ef4444;">
                <h3 style="color:#ef4444;">🚨 ระเบิดจากซาลาห์</h3>
                <p style="font-size:0.95rem;">รายงานจาก Tier 1 ระบุว่าซาลาห์ไม่พอใจภาวะผู้นำในทีมชุดนี้ นี่คือรอยร้าวที่ต้องรีบแก้!</p>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == "สถิติ":
    st.markdown('<div class="content-light"><h2>📊 เจาะลึกสถิติรายบุคคล</h2></div>', unsafe_allow_html=True)
    # ใส่ Radar Chart หรือตารางสถิติเพิ่มที่นี่
    st.info("หน้านี้คุณสามารถใส่กราฟเรดาร์ที่ดึงมาจากไฟล์ HTML ได้เลยครับ")

# FOOTER
st.markdown("""
    <div style="text-align:center; padding:50px; color:#64748b; font-size:12px;">
        © 2026 เจมส์ป๊อก LFC Dashboard | Powered by Streamlit (No More Flask Error!)
    </div>
    """, unsafe_allow_html=True)
