import streamlit as st
import plotly.graph_objects as go
import json
import os
import streamlit.components.v1 as components

# ══════════════════════════════════════════════════
# 1. PAGE CONFIG & HACK CSS (เพื่อความเป๊ะ 100%)
# ══════════════════════════════════════════════════
st.set_page_config(page_title="เจมส์ป๊อก LFC", layout="wide", initial_sidebar_state="collapsed")

# เทคนิคพิเศษ: ฉีด CSS เข้าไปที่ตัวแม่ของ Streamlit เพื่อลบขอบขาวและ Header
components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap');
</style>
<script>
const css = `
  /* ลบ Header และระยะห่างของ Streamlit */
  header, footer, [data-testid="stHeader"] { visibility: hidden; display: none !important; }
  .main .block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
  [data-testid="stAppViewContainer"] { background-color: #f8fafc !important; }
  
  /* บังคับ Font */
  html, body, [class*="css"], .stMarkdown { font-family: 'Noto Sans Thai', sans-serif !important; }
`;
const style = window.parent.document.createElement('style');
style.innerHTML = css;
window.parent.document.head.appendChild(style);
</script>
""", height=0)

# ══════════════════════════════════════════════════
# 2. DATA LOADING (JSON)
# ══════════════════════════════════════════════════
@st.cache_data
def load_data():
    try:
        if os.path.exists("match_data.json"):
            with open("match_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return None

data = load_data()

# ══════════════════════════════════════════════════
# 3. CSS สำหรับ UI (เน้นสีแดงลิเวอร์พูล)
# ══════════════════════════════════════════════════
st.markdown("""
    <style>
    .header-banner { background-color: #C8102E; color: #ffffff; padding: 60px 20px; text-align: center; border-bottom: 8px solid #F6EB61; margin-bottom: 20px; }
    .nav-bar { background: #0f172a; display: flex; justify-content: center; border-bottom: 4px solid #C8102E; }
    .nav-btn { color: white; padding: 15px 30px; cursor: pointer; font-weight: bold; border: none; background: none; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; max-width: 1200px; margin: -40px auto 30px auto; padding: 0 20px; }
    .stat-card { background: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-bottom: 5px solid #C8102E; }
    .content-dark { background-color: #1e293b; color: #F6EB61; padding: 30px; border-radius: 20px; margin-bottom: 20px; border-right: 12px solid #C8102E; }
    .content-light { background-color: #ffffff; padding: 30px; border-radius: 20px; margin-bottom: 20px; border-left: 12px solid #C8102E; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    /* ปรับแต่งปุ่ม Streamlit ให้เข้ากับธีม */
    .stButton>button { background-color: #0f172a; color: white; border-radius: 0; border: none; width: 100%; height: 55px; font-weight: 800; font-size: 1.1rem; }
    .stButton>button:hover { background-color: #C8102E; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# 4. NAVIGATION & LOGIC
# ══════════════════════════════════════════════════
if 'page' not in st.session_state: st.session_state.page = "หน้าแรก"

# Navbar แถบบนสุด
cols = st.columns([1,1,1])
with cols[0]:
    if st.button("🔴 ประเด็นร้อน"): st.session_state.page = "หน้าแรก"
with cols[1]:
    if st.button("📊 สถิติเจาะลึก"): st.session_state.page = "สถิติ"
with cols[2]:
    if st.button("🧠 วิเคราะห์แทคติก"): st.session_state.page = "แทคติก"

# Header Banner
st.markdown("""
    <div class="header-banner">
        <h1 style="font-weight:800; font-size:3.5rem; margin:0; letter-spacing:-2px;">เจมส์ป๊อก LFC</h1>
        <p style="color:#F6EB61; font-weight:600; font-size:1.2rem; margin-top:10px;">ขยี้ทุกประเด็นหงส์แดง • วิเคราะห์สไตล์โต๊ะรก</p>
    </div>
    """, unsafe_allow_html=True)

if not data:
    st.error("❌ พัง! ไม่พบไฟล์ match_data.json หรือรูปแบบไฟล์ผิด กรุณาตรวจสอบไฟล์บน GitHub ครับ")
else:
    # --- หน้าแรก ---
    if st.session_state.page == "หน้าแรก":
        info = data["match_info"]
        st.markdown(f"""
            <div class="stats-grid">
                <div class="stat-card"><p style="color:gray; font-size:0.9rem; margin:0;">MATCH</p><h2 style="margin:0; font-weight:800;">{info['title']}</h2></div>
                <div class="stat-card"><p style="color:gray; font-size:0.9rem; margin:0;">POSSESSION</p><h2 style="color:#C8102E; margin:0; font-weight:800;">{info['possession']}</h2></div>
                <div class="stat-card"><p style="color:gray; font-size:0.9rem; margin:0;">SHOTS (ON TARGET)</p><h2 style="margin:0; font-weight:800;">{info['shots']}</h2></div>
                <div class="stat-card"><p style="color:gray; font-size:0.9rem; margin:0;">OFFSIDE RATING</p><h2 style="background:#1e293b; color:#F6EB61; border-radius:8px; margin:0; font-weight:800;">{info['tier_score']}</h2></div>
            </div>
            """, unsafe_allow_html=True)

        c1, c2 = st.columns([2, 1])
        with c1:
            hot = data["hot_issue"]
            st.markdown(f"""
                <div class="content-dark">
                    <h2 style="color:white; border-bottom:3px solid #C8102E; display:inline-block; margin-bottom:15px;">{hot['topic']}</h2>
                    <p style="font-size:1.2rem; line-height:1.7;">{hot['detail']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # กราฟโมเมนตัม
            m = data["momentum"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=m["x"], y=m["y"], mode='lines+markers+text', 
                                     line=dict(color='#C8102E', width=5, shape='spline'),
                                     text=m["text"], textposition="top center",
                                     marker=dict(size=10, color="#1e293b")))
            fig.update_layout(height=400, margin=dict(l=40, r=40, t=20, b=20), plot_bgcolor='white',
                              yaxis=dict(showticklabels=False, range=[-12, 12]),
                              xaxis=dict(gridcolor='#f1f5f9'))
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown("""
                <div class="content-light">
                    <h3 style="color:#C8102E; font-weight:800;">💬 เจมส์ป๊อกขยี้</h3>
                    <p><b>สล็อต:</b> "ผมไม่ได้สั่งถอย แต่เราคุมเกมไม่อยู่เอง!" เกมนี้ครึ่งหลังเราแพ้แทคติกของมาเรสก้าชัดเจนครับ</p>
                </div>
                <div class="content-light" style="background:#fff7ed; border-color:#f97316;">
                    <h3 style="color:#f97316; font-weight:800;">🚨 Breaking</h3>
                    <p>ซาลาห์ยังไม่ตกลงสัญญาใหม่! ข่าวนี้ทำแฟนบอลกังวลมากกว่าผลเสมอวันนี้เสียอีก</p>
                </div>
                """, unsafe_allow_html=True)

    # --- หน้าสถิติ ---
    elif st.session_state.page == "สถิติ":
        st.markdown('<div style="max-width:1000px; margin:0 auto; padding:20px;">', unsafe_allow_html=True)
        st.markdown('<div class="content-light"><h2 style="text-align:center; color:#C8102E; font-weight:800;">📊 ANALYTICS RADAR</h2></div>', unsafe_allow_html=True)
        
        radar = data["radar_stats"]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=radar["liverpool"], theta=radar["labels"], fill='toself', name='LFC', line_color='#C8102E'))
        fig_r.add_trace(go.Scatterpolar(r=radar["chelsea"], theta=radar["labels"], fill='toself', name='CFC', line_color='#1d4ed8'))
        fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=600)
        st.plotly_chart(fig_r, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════
st.markdown("""
    <div style="text-align:center; padding:60px 20px; color:#94a3b8; font-size:14px; background:#f1f5f9;">
        © 2026 JAMESPOK LFC DASHBOARD • POWERED BY DATA-DRIVEN ENGINE
    </div>
    """, unsafe_allow_html=True)
