import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIG & INJECT CUSTOM CSS ---
st.set_page_config(page_title="JamesPok LFC Dashboard", layout="wide")

# แก้ปัญหาเรื่องสีฟอนต์และพื้นหลังที่กลืนกัน โดยใช้สีจาก lfcvscls.html
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Prompt', sans-serif;
        background-color: #f8fafc !important;
    }

    /* Navbar ที่ใช้งานได้จริงและสีเหมือนต้นฉบับ */
    .nav-bar {
        background-color: #0f172a;
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
        border-radius: 8px;
        margin-bottom: 2rem;
    }

    /* สไตล์ Card สถิติ */
    .stat-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-top: 4px solid #0f172a;
        text-align: center;
        color: #1e293b;
    }

    /* Timeline Card */
    .timeline-card {
        border-left: 4px solid #10b981;
        background-color: #f1f5f9;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0 8px 8px 0;
    }
    
    h1, h2, h3 { color: #1e293b !important; }
    .stMarkdown p { color: #475569 !important; }
    </style>

    <div class="nav-bar">
        <div style="font-size: 1.25rem; font-weight: bold;">⚽ JamesPok LFC News Dashboard</div>
        <div style="font-size: 0.8rem; background: #10b981; padding: 4px 12px; border-radius: 99px;">Road to 1M Followers</div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. HEADER SECTION ---
st.markdown("<h1 style='text-align: center; font-weight: 800;'>LIVERPOOL 1 - 1 CHELSEA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; max-width: 800px; margin: auto;'>ผ่าฟอร์ม วิเคราะห์แทคติก และสรุปประเด็นดราม่าเพื่อเป็น Content Pillars หลักสำหรับช่องของคุณ ดึงดูด Engagement รัวๆ!</p>", unsafe_allow_html=True)

# --- 3. EXECUTIVE SUMMARY ---
st.markdown("""
<div style="background: white; padding: 20px; border-radius: 15px; border-top: 4px solid #0f172a; margin-top: 30px;">
    <h3 style="margin-top:0;">🔥 Executive Summary (ภาพรวมรูปเกม)</h3>
    <p>เกมนี้เต็มไปด้วยการชิงไหวชิงพริบ ลิเวอร์พูลใช้การเพรสซิ่งแดนบน ขณะที่เชลซีมาในแผนรับลึกที่เหนียวแน่น ผลเสมอ 1-1 สะท้อนความเด็ดขาดที่หายไปของเจ้าบ้าน</p>
</div>
""", unsafe_allow_html=True)

# --- 4. MATCH STATS & MOMENTUM (กราฟเหมือน HTML) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 สถิติหลังเกม (Match Stats)")
    fig_stats = go.Figure()
    fig_stats.add_trace(go.Bar(name='LFC', x=['Possession', 'Shots', 'On Target'], y=[62, 18, 5], marker_color='#E31B23'))
    fig_stats.add_trace(go.Bar(name='Chelsea', x=['Possession', 'Shots', 'On Target'], y=[38, 8, 3], marker_color='#034694'))
    fig_stats.update_layout(barmode='group', height=350, margin=dict(t=20, b=20, l=0, r=0))
    st.plotly_chart(fig_stats, use_container_width=True)

with col2:
    st.markdown("### ⚔️ ประสิทธิภาพ (Radar Chart)")
    fig_radar = go.Figure()
    categories = ['เกมรุก', 'เกมรับ', 'แดนกลาง', 'สวนกลับ', 'เพรสซิ่ง']
    fig_radar.add_trace(go.Scatterpolar(r=[8, 5, 8, 6, 9], theta=categories, fill='toself', name='LFC', line_color='#E31B23'))
    fig_radar.add_trace(go.Scatterpolar(r=[5, 8, 4, 8, 5], theta=categories, fill='toself', name='Chelsea', line_color='#034694'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=350, margin=dict(t=20, b=20, l=0, r=0))
    st.plotly_chart(fig_radar, use_container_width=True)

# --- 5. TIMELINE & MOMENTUM ---
st.markdown("### 📅 Timeline ข่าวและประเด็นเด่น")
timeline_data = [
    {"date": "8 พ.ค. - Match Day", "content": "ประเด็นร้อน: ลิเวอร์พูลบุกหนักแต่โดนสวนกลับ มีจังหวะกังขา VAR ท้ายเกม", "tag": "HOT🔥"},
    {"date": "9 พ.ค. - บทสัมภาษณ์", "content": "กุนซือสล็อตผิดหวังผลตัดสิน ขณะที่เชลซีพอใจ 1 แต้มสำคัญ", "tag": "INTERVIEW💬"},
    {"date": "10 พ.ค. - บทวิเคราะห์", "content": "กูรูวิจารณ์แนวรุกหงส์ขาดความดุดัน ส่วนเชลซีกลางเก็บบอลไม่ได้", "tag": "ANALYSIS🧠"}
]

for item in timeline_data:
    st.markdown(f"""
    <div class="timeline-card">
        <div style="display: flex; justify-content: space-between;">
            <strong>{item['date']}</strong>
            <span style="font-size: 10px; background: #e2e8f0; padding: 2px 8px; border-radius: 4px;">{item['tag']}</span>
        </div>
        <p style="margin: 5px 0 0 0; font-size: 14px;">{item['content']}</p>
    </div>
    """, unsafe_allow_html=True)

# --- 6. VOTING SYSTEM (MANAGER'S ACTION) ---
st.markdown("""
<div style="background: linear-gradient(to bottom right, #1e293b, #0f172a); color: white; padding: 25px; border-radius: 15px; margin-top: 20px;">
    <h3>💡 Manager's Action Plan</h3>
    <p>1. ทำคลิปสั้นชูประเด็นการแก้เกมนาทีที่ 67<br>2. โพสต์รูปโควทคำพูดเด็ดจากสัมภาษณ์<br>3. ทำโพลโหวต Man of the Match</p>
</div>
""", unsafe_allow_html=True)

vote = st.selectbox("โหวต Man of the Match ของคุณ:", ["Salah", "Diaz", "Van Dijk", "Gravenberch"])
if st.button("ส่งคะแนนโหวต"):
    st.balloons()
    st.success(f"ขอบคุณครับ! ระบบบันทึกโหวต {vote} เรียบร้อย")
