import streamlit as st
import plotly.graph_objects as go
import json
import os
import streamlit.components.v1 as components

# ══════════════════════════════════════════════════
# 1. THE "HACKER" INJECTOR (สั่งปิด UI ของ Streamlit ให้หมด)
# ══════════════════════════════════════════════════
st.set_page_config(page_title="เจมส์ป๊อก LFC", layout="wide", initial_sidebar_state="collapsed")

components.html("""
<script>
const css = `
    /* ซ่อนองค์ประกอบของ Streamlit */
    header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
    .main .block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
    [data-testid="stAppViewContainer"] { background-color: #f8fafc !important; }
    
    /* บังคับ Font Noto Sans Thai */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap');
    * { font-family: 'Noto Sans Thai', sans-serif !important; }
`;
const style = window.parent.document.createElement('style');
style.innerHTML = css;
window.parent.document.head.appendChild(style);
</script>
""", height=0)

# ══════════════════════════════════════════════════
# 2. LOAD DATA FROM JSON
# ══════════════════════════════════════════════════
@st.cache_data
def load_data():
    if os.path.exists("match_data.json"):
        with open("match_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

data = load_data()

# ══════════════════════════════════════════════════
# 3. CSS — ดึงจากตัว "แบบเก่า" มาทั้งหมดเพื่อความเนียน
# ══════════════════════════════════════════════════
st.markdown("""
<style>
    .lfc-header { background: #C8102E; color: white; padding: 40px 20px; text-align: center; border-bottom: 6px solid #F6EB61; }
    .nav-bar { background: #1e293b; display: flex; justify-content: center; border-bottom: 3px solid #C8102E; }
    
    .stats-row { 
        display: flex; justify-content: center; gap: 20px; 
        margin-top: -30px; padding: 0 20px; flex-wrap: wrap; 
    }
    .stat-box { 
        background: white; padding: 15px 25px; border-radius: 12px; 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); 
        text-align: center; min-width: 180px; border-bottom: 4px solid #C8102E;
    }
    
    .main-grid { 
        display: grid; grid-template-columns: 2fr 1fr; gap: 25px; 
        max-width: 1200px; margin: 30px auto; padding: 0 20px; 
    }
    @media (max-width: 800px) { .main-grid { grid-template-columns: 1fr; } }

    .card-dark { background: #1e293b; color: #F6EB61; padding: 25px; border-radius: 15px; border-right: 10px solid #C8102E; }
    .card-light { background: white; padding: 25px; border-radius: 15px; border-left: 10px solid #C8102E; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 20px; }
    
    /* ปุ่ม Navbar แบบ Streamlit Hack */
    .stButton>button { border-radius: 0; border: none; background: #1e293b; color: white; height: 50px; font-weight: bold; }
    .stButton>button:hover { background: #C8102E; color: white; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# 4. CONTENT LOGIC
# ══════════════════════════════════════════════════
if 'page' not in st.session_state: st.session_state.page = "หน้าแรก"

# Navbar
nav_cols = st.columns([1,1,1])
with nav_cols[0]:
    if st.button("🔴 ประเด็นร้อน"): st.session_state.page = "หน้าแรก"
with nav_cols[1]:
    if st.button("📊 สถิติเจาะลึก"): st.session_state.page = "สถิติ"
with nav_cols[2]:
    if st.button("🧠 วิเคราะห์แทคติก"): st.session_state.page = "แทคติก"

# Header
st.markdown('<div class="lfc-header"><h1 style="font-size:3rem; font-weight:800; margin:0;">เจมส์ป๊อก LFC</h1><p style="color:#F6EB61; font-weight:600;">ขยี้ทุกประเด็นหงส์แดง - วิเคราะห์สไตล์โต๊ะรก</p></div>', unsafe_allow_html=True)

if not data:
    st.warning("⚠️ กำลังรอข้อมูลจาก match_data.json...")
else:
    if st.session_state.page == "หน้าแรก":
        # Stats Row
        st.markdown(f"""
        <div class="stats-row">
            <div class="stat-box"><small style="color:gray;">MATCH</small><h2 style="margin:0;">{data['match_info']['title']}</h2></div>
            <div class="stat-box"><small style="color:gray;">POSSESSION</small><h2 style="margin:0; color:#C8102E;">{data['match_info']['possession']}</h2></div>
            <div class="stat-box"><small style="color:gray;">SHOTS</small><h2 style="margin:0;">{data['match_info']['shots']}</h2></div>
            <div class="stat-box" style="background:#1e293b; color:#F6EB61;"><small>OFFSIDE RATING</small><h2 style="margin:0;">{data['match_info']['tier_score']}</h2></div>
        </div>
        """, unsafe_allow_html=True)

        # Main Layout (ใช้ Grid แทน Columns ของ Streamlit เพื่อความเป๊ะ)
        st.markdown('<div class="main-grid">', unsafe_allow_html=True)
        
        # คอลัมน์ซ้าย (เนื้อหาหลัก + กราฟ)
        with st.container():
            st.markdown(f"""
            <div class="card-dark">
                <h2 style="color:white; border-bottom:2px solid #C8102E; display:inline-block;">{data['hot_issue']['topic']}</h2>
                <p style="font-size:1.1rem; line-height:1.6; margin-top:15px;">{data['hot_issue']['detail']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("### 📊 Momentum Graph")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data['momentum']['x'], y=data['momentum']['y'], mode='lines+markers+text',
                                     line=dict(color='#C8102E', width=4, shape='spline'),
                                     text=data['momentum']['text'], textposition="top center"))
            fig.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='white')
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig, use_container_width=True)

        # คอลัมน์ขวา (Sidebar)
        with st.container():
            st.markdown("""
            <div class="card-light">
                <h3 style="color:#C8102E; margin:0;">💬 เจมส์ป๊อกขยี้</h3>
                <p style="font-size:0.95rem; margin-top:10px;">สถิติไม่เคยหลอกใคร ครึ่งหลังเราโดนกดจนโงหัวไม่ขึ้นจริงๆ ครับนัดนี้</p>
            </div>
            <div class="card-light" style="border-left-color: #f97316;">
                <h3 style="color:#f97316; margin:0;">🚨 ข่าวล่ามาแรง</h3>
                <p style="font-size:0.95rem; margin-top:10px;">มีรายงานว่าสโมสรกำลังคุยเรื่องสัญญาใหม่กับ กราเฟนแบร์ก!</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.page == "สถิติ":
        st.markdown('<div style="max-width:800px; margin: 40px auto; padding: 20px;">', unsafe_allow_html=True)
        st.markdown('<div class="card-light"><h2 style="text-align:center; color:#C8102E;">📊 สถิติเจาะลึก (Radar Chart)</h2></div>', unsafe_allow_html=True)
        radar = data["radar_stats"]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=radar["liverpool"], theta=radar["labels"], fill='toself', name='LFC', line_color='#C8102E'))
        fig_r.add_trace(go.Scatterpolar(r=radar["chelsea"], theta=radar["labels"], fill='toself', name='CFC', line_color='#1d4ed8'))
        fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=500)
        st.plotly_chart(fig_r, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div style="text-align:center; padding:40px; color:#94a3b8; font-size:12px;">© 2026 เจมส์ป๊อก LFC Dashboard | Back to Classic Look</div>', unsafe_allow_html=True)
