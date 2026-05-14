import streamlit as st
import plotly.graph_objects as go
import json
import os

# --- 1. CONFIG & CSS ---
st.set_page_config(page_title="เจมส์ป๊อก LFC Dashboard", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap');
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stHeader"] { display: none; }
    body, .stApp { font-family: 'Noto Sans Thai', sans-serif; background-color: #f8fafc; }
    .header-banner { background-color: #C8102E; color: #ffffff; padding: 50px 20px; text-align: center; border-bottom: 6px solid #F6EB61; }
    .py-badge { background: #1d4ed8; color: white; font-size: 12px; padding: 2px 8px; border-radius: 10px; margin-left: 10px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; max-width: 1100px; margin: -30px auto 30px auto; padding: 0 20px; }
    .stat-card { background: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-bottom: 4px solid #C8102E; }
    .content-dark { background-color: #1e293b; color: #F6EB61; padding: 30px; border-radius: 15px; margin-bottom: 20px; border-right: 10px solid #C8102E; }
    .content-light { background-color: #ffffff; padding: 30px; border-radius: 15px; margin-bottom: 20px; border-left: 10px solid #C8102E; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 0; border: none; background-color: #0f172a; color: white; height: 50px; }
    .stButton>button:hover { background-color: #C8102E; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOAD DATA FROM JSON ---
# ฟังก์ชันอ่านไฟล์ JSON ที่เราเพิ่งสร้าง
@st.cache_data
def load_data():
    if os.path.exists("match_data.json"):
        with open("match_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

data = load_data()

# --- 3. NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = "หน้าแรก"

nav_cols = st.columns([1,1,1])
with nav_cols[0]:
    if st.button("🔴 ประเด็นร้อน"): st.session_state.page = "หน้าแรก"
with nav_cols[1]:
    if st.button("📊 สถิติเจาะลึก"): st.session_state.page = "สถิติ"
with nav_cols[2]:
    if st.button("🧠 วิเคราะห์แทคติก"): st.session_state.page = "แทคติก"

# --- 4. HEADER ---
st.markdown("""
    <div class="header-banner">
        <h1 style="font-weight:800; font-size:3rem; margin:0;">เจมส์ป๊อก LFC <span class="py-badge">STREAMLIT</span></h1>
        <p style="color:#F6EB61; font-weight:600;">ขยี้ทุกประเด็นหงส์แดง - วิเคราะห์สไตล์โต๊ะรก</p>
    </div>
    """, unsafe_allow_html=True)

# ตรวจสอบว่ามีข้อมูลไหม
if data is None:
    st.error("⚠️ ไม่พบไฟล์ match_data.json กรุณาสร้างไฟล์ข้อมูลก่อนครับ")
else:
    # --- PAGE: หน้าแรก ---
    if st.session_state.page == "หน้าแรก":
        # ดึงข้อมูลจาก JSON มาแสดง
        info = data["match_info"]
        st.markdown(f"""
            <div class="stats-grid">
                <div class="stat-card"><p style="color:gray; font-size:14px; margin:0;">ผลการแข่ง</p><h2 style="margin:0;">{info['title']}</h2></div>
                <div class="stat-card"><p style="color:gray; font-size:14px; margin:0;">ครองบอล</p><h2 style="color:#C8102E; margin:0;">{info['possession']}</h2></div>
                <div class="stat-card"><p style="color:gray; font-size:14px; margin:0;">โอกาสยิง</p><h2 style="margin:0;">{info['shots']}</h2></div>
                <div class="stat-card"><p style="color:gray; font-size:14px; margin:0;">ความล้ำ</p><h2 style="background:#1e293b; color:#F6EB61; border-radius:5px; margin:0;">{info['tier_score']}</h2></div>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            hot = data["hot_issue"]
            st.markdown(f"""
                <div class="content-dark">
                    <h2 style="color:white; border-bottom:2px solid #C8102E; display:inline-block;">{hot['topic']}</h2>
                    <p style="font-size:1.1rem; line-height:1.6;">{hot['detail']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.subheader("📊 กราฟโมเมนตัม (บวก=หงส์บุก / ลบ=สิงห์บุก)")
            m_data = data["momentum"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=m_data["x"], y=m_data["y"], mode='lines+markers+text',
                line=dict(color='#C8102E', width=4, shape='spline'),
                text=m_data["text"], textposition="top center"
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

    # --- PAGE: สถิติเจาะลึก ---
    elif st.session_state.page == "สถิติ":
        st.markdown('<div style="max-width:1100px; margin:auto;">', unsafe_allow_html=True)
        st.markdown("""
            <div class="content-light">
                <h2 style="color:#C8102E; text-align:center;">📊 เปรียบเทียบสถิติภาพรวม (Radar Chart)</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # กราฟ Radar ดึงข้อมูลจาก JSON
        radar = data["radar_stats"]
        fig_radar = go.Figure()
        
        # เพิ่มเส้นของ Liverpool
        fig_radar.add_trace(go.Scatterpolar(
            r=radar["liverpool"], theta=radar["labels"], fill='toself', name='Liverpool',
            line_color='#C8102E', fillcolor="rgba(200, 16, 46, 0.2)"
        ))
        # เพิ่มเส้นของ Chelsea
        fig_radar.add_trace(go.Scatterpolar(
            r=radar["chelsea"], theta=radar["labels"], fill='toself', name='Chelsea',
            line_color='#1d4ed8', fillcolor="rgba(29, 78, 216, 0.2)"
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True, height=500
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- PAGE: วิเคราะห์แทคติก ---
    elif st.session_state.page == "แทคติก":
        st.markdown('<div style="max-width:1100px; margin:auto;">', unsafe_allow_html=True)
        st.markdown("""
            <div class="content-dark">
                <h2 style="color:white; text-align:center;">🧠 วิเคราะห์สไตล์โต๊ะรก (Tactical Board)</h2>
                <p style="text-align:center; color:#F6EB61;">พื้นที่นี้เตรียมไว้สำหรับการลากวางแผนผังการเล่นในอนาคต</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# FOOTER
st.markdown("""
    <div style="text-align:center; padding:50px; color:#64748b; font-size:12px;">
        © 2026 เจมส์ป๊อก LFC Dashboard | Phase 2: Data-Driven Engine Active
    </div>
    """, unsafe_allow_html=True)
