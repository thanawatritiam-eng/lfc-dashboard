"""
เจมส์ป๊อก LFC Dashboard — Streamlit Edition (Fixed v2)
แก้ปัญหา CSS โชว์เป็น text และสีขาวอ่านไม่ออก
"""
import random
import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ══════════════════════════════════════════════════
# PAGE CONFIG — ต้องเป็น st call แรกสุดเสมอ
# ══════════════════════════════════════════════════
st.set_page_config(
    page_title="เจมส์ป๊อก LFC",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════
# CSS — inject ผ่าน components.html (height=0)
# วิธีนี้ทำงานได้ทุก Streamlit Cloud version
# ══════════════════════════════════════════════════
components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap');
</style>
<script>
// inject styles into parent Streamlit document
const css = `
  html, body, [class*="css"], .stMarkdown, .stMarkdown p, .stMarkdown div,
  .element-container { font-family: 'Noto Sans Thai', sans-serif !important; }
  section[data-testid="stSidebar"] { display:none; }
  #MainMenu, footer, header { visibility:hidden; }
  .stApp { background:#f8fafc !important; }
  .block-container { padding-top:1rem !important; padding-bottom:2rem !important; }

  .lfc-header { background:#C8102E; padding:16px 28px; border-radius:12px;
    display:flex; align-items:center; gap:14px;
    box-shadow:0 4px 12px rgba(200,16,46,.35); margin-bottom:20px; }
  .lfc-logo { width:46px; height:46px; background:#fff; border-radius:50%;
    border:2px solid #F6EB61; display:flex; align-items:center;
    justify-content:center; font-weight:900; font-size:16px; color:#C8102E; flex-shrink:0; }
  .lfc-title { color:#fff; font-size:20px; font-weight:800;
    text-transform:uppercase; letter-spacing:.06em; line-height:1.2; }
  .lfc-sub { color:#F6EB61; font-size:11px; font-weight:600;
    text-transform:uppercase; letter-spacing:.12em; }
  .st-badge { background:linear-gradient(135deg,#3b82f6,#1d4ed8);
    color:#fff !important; font-size:10px; font-weight:700;
    padding:3px 9px; border-radius:9999px; display:inline-block;
    margin-left:8px; vertical-align:middle; }

  .card { background:#fff; border-radius:14px; padding:22px;
    border:1px solid #e5e7eb; box-shadow:0 1px 5px rgba(0,0,0,.07);
    margin-bottom:14px; color:#1e293b; }
  .card-red-border { border:1.5px solid #C8102E !important; background:#fef2f2 !important; }
  .card-gold-border { border:2px solid #F6EB61 !important; }

  .scoreboard { background:#f1f5f9; border-radius:12px; padding:18px;
    display:flex; justify-content:space-around; align-items:center;
    text-align:center; margin-bottom:20px; }
  .score-team-liv { color:#b91c1c; font-weight:800; font-size:18px; }
  .score-team-che { color:#1d4ed8; font-weight:800; font-size:18px; }
  .score-num { color:#0f172a; font-weight:900; font-size:42px; line-height:1; }
  .score-vs  { color:#64748b; font-weight:700; font-size:22px; }

  .tl-row  { display:flex; margin-bottom:14px; }
  .tl-min  { width:42px; flex-shrink:0; color:#475569; font-weight:700;
    font-size:13px; padding-top:3px; }
  .tl-body { flex:1; padding-left:14px; border-left:3px solid #d1d5db; padding-bottom:14px; }
  .tl-body.red  { border-color:#C8102E; }
  .tl-body.blue { border-color:#1d4ed8; }
  .tl-title-red  { color:#b91c1c; font-weight:900; font-size:17px; }
  .tl-title-blue { color:#1d4ed8; font-weight:900; font-size:17px; }
  .tl-title-gray { color:#1e293b; font-weight:700; font-size:15px; }
  .tl-desc { color:#374151; font-size:13px; margin-top:3px; line-height:1.5; }

  .quote-label { font-size:11px; font-weight:700; text-transform:uppercase;
    letter-spacing:.08em; margin-bottom:8px; display:block; }
  .quote-text { font-size:15px; font-style:italic; color:#1e293b;
    margin-bottom:10px; line-height:1.6; }
  .quote-bold { font-size:18px; font-weight:800; color:#0f172a; margin-bottom:10px; }
  .quote-note { font-size:13px; color:#4b5563; line-height:1.5; }

  .romano-box { background:#1e293b; border-radius:14px; padding:22px;
    display:flex; align-items:flex-start; gap:14px; margin-top:14px; }
  .romano-title { color:#F6EB61; font-weight:700; margin-bottom:5px; font-size:15px; }
  .romano-text  { color:#cbd5e1; font-size:13px; line-height:1.6; }
  .romano-text strong { color:#fff; }

  .grav-card { background:#fff; border-radius:14px; padding:18px;
    border:1px solid #e5e7eb; display:flex; gap:14px;
    align-items:flex-start; margin-top:10px; }
  .grav-icon  { font-size:32px; flex-shrink:0; }
  .grav-label { color:#475569; font-size:11px; font-weight:700;
    text-transform:uppercase; letter-spacing:.08em; }
  .grav-quote { color:#1e293b; font-weight:600; font-size:15px; margin:4px 0; }
  .grav-desc  { color:#475569; font-size:13px; line-height:1.5; }

  .drama-heading { color:#0f172a; font-size:20px; font-weight:800;
    border-left:4px solid #C8102E; padding-left:12px; margin-bottom:14px; }
  .sec-heading { color:#0f172a; font-size:28px; font-weight:800;
    text-transform:uppercase; text-align:center; margin-bottom:6px; }
  .sec-sub { color:#475569; font-size:16px; text-align:center;
    max-width:680px; margin:0 auto 28px; line-height:1.6; }

  .stat-card-red  { background:#fef2f2; border:1px solid #fecaca;
    border-radius:12px; padding:16px; text-align:center; }
  .stat-card-blue { background:#eff6ff; border:1px solid #bfdbfe;
    border-radius:12px; padding:16px; text-align:center; }
  .stat-card-gray { background:#f8fafc; border:1px solid #e2e8f0;
    border-radius:12px; padding:16px; text-align:center; margin-top:10px; }
  .stat-num-red  { color:#b91c1c; font-size:38px; font-weight:900; }
  .stat-num-blue { color:#1d4ed8; font-size:38px; font-weight:900; }
  .stat-num-gray { color:#0f172a; font-size:28px; font-weight:900; }
  .stat-label    { color:#374151; font-size:11px; font-weight:700;
    text-transform:uppercase; letter-spacing:.05em; margin-top:4px; }

  .progress-wrap { background:#e5e7eb; border-radius:9999px; height:8px; margin:6px 0 12px; }
  .progress-fill { background:#C8102E; border-radius:9999px; height:8px; }

  .compare-box { background:linear-gradient(135deg,#7f1d1d,#000);
    border-radius:14px; padding:26px; margin-bottom:14px; }
  .compare-title   { color:#F6EB61; font-weight:700; font-size:17px; margin-bottom:8px; }
  .compare-body    { color:#e2e8f0; font-size:13px; margin-bottom:14px; line-height:1.5; }
  .compare-row     { display:flex; justify-content:space-around; text-align:center; }
  .compare-liv     { color:#fff; font-size:22px; font-weight:900; }
  .compare-liv-sub { color:#fca5a5; font-size:12px; }
  .compare-vs      { color:#e2e8f0; font-size:18px; font-weight:700; align-self:center; }
  .compare-mun     { color:#ef4444; font-size:22px; font-weight:900; }
  .compare-mun-sub { color:#94a3b8; font-size:12px; }

  .comment-box   { background:#f1f5f9; border:1px solid #e2e8f0;
    border-radius:14px; padding:18px; }
  .comment-title { color:#0f172a; font-weight:700; margin-bottom:10px; font-size:15px; }
  .comment-item  { background:#fff; border-radius:8px; padding:10px 14px;
    margin-bottom:8px; box-shadow:0 1px 3px rgba(0,0,0,.06);
    font-size:13px; color:#374151; line-height:1.5; }
  .comment-item-red  { border-left:3px solid #C8102E; }
  .comment-user-blue { color:#1d4ed8; font-weight:700; }
  .comment-user-dark { color:#1e293b; font-weight:700; }

  .editor-card  { background:#fff; border-radius:14px; padding:28px;
    border-top:4px solid #C8102E; box-shadow:0 1px 5px rgba(0,0,0,.07); }
  .editor-title { color:#0f172a; font-size:20px; font-weight:900; margin-bottom:12px; }
  .editor-body  { color:#374151; line-height:1.8; margin-bottom:12px; font-size:14px; }
  .editor-quote { color:#1e293b; font-weight:600; line-height:1.8; font-size:14px; }

  .lfc-footer { background:#111827; padding:22px; text-align:center;
    border-radius:14px; margin-top:36px; }
  .footer-title { color:#fff; font-weight:700; font-size:16px; margin-bottom:5px; }
  .footer-ref   { color:#9ca3af; font-size:13px; margin-bottom:3px; }
  .footer-copy  { color:#6b7280; font-size:11px; }
`;
const style = window.parent.document.createElement('style');
style.textContent = css;
window.parent.document.head.appendChild(style);
</script>
""", height=0, scrolling=False)

# ══════════════════════════════════════════════════
# DATA LAYER
# ══════════════════════════════════════════════════
TIMELINE_EVENTS = [
    {"minute":"6'",  "title":"GOAL! (LIV)", "tcls":"tl-title-red",  "bcls":"red",
     "detail":"ริโอ อึงูโมฮา ไหลบอลให้ <b>ไรอัน กราเฟนแบร์ก</b> ปั่นโค้งสุดสวย หงส์ขึ้นนำ!"},
    {"minute":"35'", "title":"GOAL! (CHE)", "tcls":"tl-title-blue", "bcls":"blue",
     "detail":"<b>เอ็นโซ เฟร์นานเดซ</b> ปั่นฟรีคิกแฉลบเข้าประตู สิงห์บลูส์ตีเสมอ"},
    {"minute":"67'", "title":"จุดเปลี่ยน & ดราม่า","tcls":"tl-title-gray","bcls":"",
     "detail":"สล็อตถอด <b>อึงูโมฮา</b> ที่กำลังเล่นดีออก แฟนบอลในแอนฟิลด์เริ่มส่งเสียงโห่"},
    {"minute":"FT",  "title":"จบเกม เสมอ 1-1","tcls":"tl-title-gray","bcls":"",
     "detail":"โซบอสซ์ไลยิงชนเสา ฟาน ไดจ์คโหม่งชนคาน เจาะไม่เข้า"},
]
STATS_LABELS = ["การครองบอล (%)", "โอกาสยิง", "ยิงเข้ากรอบ",
                "จ่ายบอลสำเร็จ (%)", "เตะมุม", "ฟาวล์"]
STATS_LIV    = [42, 11, 4, 81, 6, 12]
STATS_CHE    = [58, 14, 5, 87, 5, 10]
MOMENTUM_X   = ["0","15","30","HT","60","75","90"]
MOMENTUM_Y   = [0, 5, -2, -5, 2, -8, -4]
MOMENTUM_TIPS= {0:"นาที 6: กราเฟนแบร์กยิงนำ",
                2:"นาที 35: เอ็นโซ่ตีเสมอ",
                5:"นาที 67: ถอดอึงูโมฮา โมเมนตัมตก"}
AGREE_TEXT    = "เห็นด้วยกับพี่เจมส์ป๊อก สล็อตดื้อเกินไป ไม่ยอมรับผิด!"
DISAGREE_TEXT = "ผมว่าใจเย็นๆ ขุมกำลังเราเจ็บเยอะ สล็อตทำได้เท่านี้ก็โอเคแล้ว"

# ══════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════
if "tab" not in st.session_state:
    st.session_state.tab = "hot"
if "comments" not in st.session_state:
    st.session_state.comments = [
        {"user":"JamesPok LFC","text":"ตบขมับเลยครับแมตช์นี้!",
         "ucls":"comment-user-dark","border":True},
        {"user":"Kopite_1989","text":"ซาลาห์พูดถูก ทีมขาดผู้นำจริงๆ กัปตันหายไปไหนตอนทีมเป๋?",
         "ucls":"comment-user-blue","border":False},
    ]

# ══════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════
st.markdown("""
<div class="lfc-header">
  <div class="lfc-logo">JP</div>
  <div>
    <div class="lfc-title">เจมส์ป๊อก LFC <span class="st-badge">Streamlit</span></div>
    <div class="lfc-sub">ขยี้ทุกประเด็นหงส์แดง</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB NAVIGATION
# ══════════════════════════════════════════════════
t1, t2, t3, _ = st.columns([2.3, 1.4, 2.3, 2.5])
with t1:
    if st.button("🔥 ประเด็นร้อน (Chelsea 1-1)", use_container_width=True, key="btn_hot",
                 type="primary" if st.session_state.tab == "hot" else "secondary"):
        st.session_state.tab = "hot"; st.rerun()
with t2:
    if st.button("📊 เจาะสถิติ", use_container_width=True, key="btn_stats",
                 type="primary" if st.session_state.tab == "stats" else "secondary"):
        st.session_state.tab = "stats"; st.rerun()
with t3:
    if st.button("🗒️ วิเคราะห์สไตล์โต๊ะรก", use_container_width=True, key="btn_analysis",
                 type="primary" if st.session_state.tab == "analysis" else "secondary"):
        st.session_state.tab = "analysis"; st.rerun()

st.markdown("<hr style='border:none;border-top:1px solid #e5e7eb;margin:12px 0 24px;'>",
            unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 1 — ประเด็นร้อน
# ══════════════════════════════════════════════════════════════
if st.session_state.tab == "hot":

    st.markdown('<p class="sec-heading">หงส์สะดุดอีก! เสียงโห่ลั่นแอนฟิลด์</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">ควันหลงและดราม่าหลังเกมที่เครื่องจักรสีแดงทำได้แค่เปิดบ้านเสมอ เชลซี 1-1 สรุปเหตุการณ์สำคัญและระเบิดลูกใหญ่จากนักเตะ</p>',
                unsafe_allow_html=True)

    left, right = st.columns([1, 2], gap="large")

    with left:
        tl_rows = "".join([
            f'<div class="tl-row">'
            f'<div class="tl-min">{e["minute"]}</div>'
            f'<div class="tl-body {e["bcls"]}">'
            f'<div class="{e["tcls"]}">{e["title"]}</div>'
            f'<div class="tl-desc">{e["detail"]}</div>'
            f'</div></div>'
            for e in TIMELINE_EVENTS
        ])
        st.markdown(f"""
        <div class="card">
          <div style="font-size:17px;font-weight:800;color:#0f172a;
            border-bottom:2px solid #C8102E;padding-bottom:8px;
            margin-bottom:16px;display:inline-block;">
            ผลการแข่งขัน &amp; ไทม์ไลน์
          </div>
          <div class="scoreboard">
            <div><div class="score-team-liv">LIV</div><div class="score-num">1</div></div>
            <div class="score-vs">VS</div>
            <div><div class="score-team-che">CHE</div><div class="score-num">1</div></div>
          </div>
          {tl_rows}
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="drama-heading">ประเด็นเดือดหลังเกม</div>',
                    unsafe_allow_html=True)
        d1, d2 = st.columns(2, gap="medium")
        with d1:
            st.markdown("""
            <div class="card">
              <span class="quote-label" style="color:#C8102E;">อาร์เน่อ สล็อต</span>
              <div class="quote-text">"พวกคุณคิดจริงๆ เหรอว่าผมสั่งให้ทีมถอยไปรับ? นี่คุณเห็นผมตะโกนสั่งข้างสนามว่า 'ถอยไปเดี๋ยวนี้! กลับไปเฝ้าเขตโทษตัวเอง' หรือไง?"</div>
              <div class="quote-note"><strong>เจมส์ป๊อกขยี้:</strong> กุนซือหงส์แดงตอบคำถามแบบติดประชดหลังโดนวิจารณ์เรื่องแทคติกครึ่งหลังที่ดูถอยไปตั้งรับมากเกินไป</div>
            </div>""", unsafe_allow_html=True)
        with d2:
            st.markdown("""
            <div class="card card-red-border">
              <span class="quote-label" style="color:#C8102E;">🚨 ระเบิดจากซาลาห์!</span>
              <div class="quote-bold">"ทีมชุดนี้ ขาดผู้นำ"</div>
              <div class="quote-note"><strong>รายงานจาก Paul Gorst (Tier 1):</strong> โม ซาลาห์ ให้สัมภาษณ์แทงใจดำ ทำเอาสล็อตหัวเสียสุดๆ บ่งบอกถึงรอยร้าวในแคมป์</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="grav-card">
          <div class="grav-icon">🗣️</div>
          <div>
            <div class="grav-label">ไรอัน กราเฟนแบร์ก ตัดพ้อแฟนบอล</div>
            <div class="grav-quote">"พวกเราไม่สมควรได้รับมัน (เสียงโห่)"</div>
            <div class="grav-desc">ผู้ทำประตูขึ้นนำออกมาปกป้องทีม หลังจากแฟนบอลในแอนฟิลด์ส่งเสียงโห่หลังจบเกมและจังหวะเปลี่ยนตัว</div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="romano-box">
          <div style="font-size:26px;flex-shrink:0;">📰</div>
          <div>
            <div class="romano-title">Fabrizio Romano Update</div>
            <div class="romano-text">บอร์ดบริหารลิเวอร์พูลยังคง <strong>"หนุนหลัง"</strong> อาร์เน่อ สล็อต อย่างเต็มที่ ข่าวลือเรื่องการติดต่อ ชาบี อลอนโซ่ ไม่เป็นความจริง สล็อตยังได้ไปต่อ!</div>
          </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION 2 — เจาะสถิติ
# ══════════════════════════════════════════════════════════════
elif st.session_state.tab == "stats":

    st.markdown('<p class="sec-heading">เจาะสถิติ ฟ้องด้วยตัวเลข</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">สถิติจากเกมนี้บอกอะไรเรา? ลิเวอร์พูลถอยไปรับจริง หรือแค่เจาะเชลซีไม่เข้า มาดูตัวเลขเปรียบเทียบกัน</p>', unsafe_allow_html=True)

    chart_col, right_col = st.columns(2, gap="large")

    with chart_col:
        st.markdown('<div class="card"><p style="font-size:17px;font-weight:800;color:#0f172a;text-align:center;margin-bottom:8px;">สถิติภาพรวมเกมรุกและรับ</p>', unsafe_allow_html=True)
        lc  = STATS_LABELS + [STATS_LABELS[0]]
        lv  = STATS_LIV    + [STATS_LIV[0]]
        lch = STATS_CHE    + [STATS_CHE[0]]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=lv, theta=lc, fill="toself", name="ลิเวอร์พูล",
            line=dict(color="#C8102E",width=2), fillcolor="rgba(200,16,46,0.15)",
            marker=dict(color="#C8102E")))
        fig_r.add_trace(go.Scatterpolar(r=lch, theta=lc, fill="toself", name="เชลซี",
            line=dict(color="#1d4ed8",width=2), fillcolor="rgba(29,78,216,0.15)",
            marker=dict(color="#1d4ed8")))
        fig_r.update_layout(
            polar=dict(
                radialaxis=dict(visible=True,range=[0,100],
                                tickfont=dict(size=10,color="#475569")),
                angularaxis=dict(tickfont=dict(size=11,color="#1e293b")),bgcolor="#f8fafc"),
            legend=dict(orientation="h",y=-0.18,x=0.5,xanchor="center",
                        font=dict(size=13,color="#1e293b")),
            paper_bgcolor="#ffffff",margin=dict(l=40,r=40,t=20,b=60),height=380)
        st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        s1, s2 = st.columns(2)
        with s1:
            st.markdown('<div class="stat-card-red"><div class="stat-num-red">11</div><div class="stat-label">โอกาสยิง (ลิเวอร์พูล)</div></div>', unsafe_allow_html=True)
        with s2:
            st.markdown('<div class="stat-card-blue"><div class="stat-num-blue">14</div><div class="stat-label">โอกาสยิง (เชลซี)</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-card-gray"><div class="stat-num-gray">2 ครั้ง</div><div class="stat-label">ยิงชนเสา/คาน (โซบอสซ์ไล, ฟาน ไดจ์ค)</div></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="card card-gold-border" style="margin-top:12px;">
          <div style="font-size:15px;font-weight:800;color:#1e293b;margin-bottom:8px;">🌟 Spotlight: ริโอ อึงูโมฮา (17 ปี)</div>
          <div style="color:#374151;font-size:13px;margin-bottom:12px;">ดาวรุ่งที่โชว์ฟอร์มได้โดดเด่นที่สุดในแนวรุก ก่อนถูกเปลี่ยนตัวออกจนเกิดเสียงโห่</div>
          <div style="display:flex;justify-content:space-between;">
            <span style="font-size:13px;font-weight:600;color:#374151;">เลี้ยงผ่านคู่แข่ง</span>
            <span style="font-weight:800;color:#1e293b;">4/5 ครั้ง</span>
          </div>
          <div class="progress-wrap"><div class="progress-fill" style="width:80%;"></div></div>
          <div style="display:flex;justify-content:space-between;margin-top:4px;">
            <span style="font-size:13px;font-weight:600;color:#374151;">แอสซิสต์</span>
            <span style="font-weight:800;color:#1e293b;">1</span>
          </div>
          <div style="font-size:11px;color:#64748b;margin-top:10px;font-style:italic;">*สล็อตอ้างว่าเปลี่ยนออกเพราะนักเตะมีอาการตะคริว</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="card" style="margin-top:8px;">
      <p style="font-size:17px;font-weight:800;color:#0f172a;text-align:center;margin-bottom:4px;">โมเมนตัมการบุก (จำลอง)</p>
      <p style="color:#64748b;font-size:13px;text-align:center;margin-bottom:10px;">กราฟแสดงความกดดันในแต่ละช่วงเวลา (บวก = หงส์บุก, ลบ = สิงห์บุก)</p>
    """, unsafe_allow_html=True)
    pt_colors = ["#C8102E" if i in MOMENTUM_TIPS else "#1e293b" for i in range(len(MOMENTUM_Y))]
    hov = [MOMENTUM_TIPS.get(i, f"โมเมนตัม: {v}") for i, v in enumerate(MOMENTUM_Y)]
    fig_m = go.Figure()
    fig_m.add_hrect(y0=0,  y1=10, fillcolor="rgba(200,16,46,0.05)", line_width=0)
    fig_m.add_hrect(y0=-10,y1=0,  fillcolor="rgba(29,78,216,0.05)", line_width=0)
    fig_m.add_trace(go.Scatter(x=MOMENTUM_X,y=MOMENTUM_Y,mode="lines+markers",
        line=dict(color="#1e293b",width=3,shape="spline"),fill="tozeroy",
        fillcolor="rgba(30,41,59,0.08)",
        marker=dict(size=10,color=pt_colors,line=dict(color="#fff",width=2)),
        hovertext=hov,hoverinfo="text",name="โมเมนตัม"))
    fig_m.add_hline(y=0,line_color="#0f172a",line_width=1.5)
    fig_m.add_annotation(x="15",y=5,text="🔴 LFC บุก",showarrow=False,
                         font=dict(color="#C8102E",size=11),yshift=16)
    fig_m.add_annotation(x="75",y=-8,text="🔵 CHE บุก",showarrow=False,
                         font=dict(color="#1d4ed8",size=11),yshift=-18)
    fig_m.update_layout(
        xaxis=dict(title="นาที",tickfont=dict(size=12,color="#1e293b"),gridcolor="#e5e7eb"),
        yaxis=dict(range=[-10,10],showticklabels=False,gridcolor="#e5e7eb"),
        paper_bgcolor="#ffffff",plot_bgcolor="#ffffff",
        showlegend=False,margin=dict(l=20,r=20,t=10,b=40),height=300)
    st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION 3 — วิเคราะห์สไตล์โต๊ะรก
# ══════════════════════════════════════════════════════════════
elif st.session_state.tab == "analysis":

    st.markdown('<p class="sec-heading">โต๊ะรก วิจารณ์</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">ถึงเวลาตบขมับ! วิเคราะห์เจาะลึกแบบไม่เกรงใจใคร สไตล์ เจมส์ป๊อก LFC</p>', unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("""
        <div class="editor-card">
          <div class="editor-title">ถอด อึงูโมฮา... แทคติก หรือ พลาด?</div>
          <div class="editor-body">เกมนี้ของกำลังมาแท้ๆ ไอ้หนู ริโอ เลื้อยจนแนวรับเชลซีหัวหมุน แต่สล็อตดันเลือกถอดออกนาที 67 แล้วส่ง อิซัค ลงมาแทน! เข้าใจว่าอ้างเรื่องตะคริว แต่พอเปลี่ยนปุ๊บ เกมรุกฝั่งซ้ายบอดสนิททันที กลายเป็นว่าเราเสียโมเมนตัมไปดื้อๆ</div>
          <div class="editor-quote">"การสัมภาษณ์หลังเกมที่สล็อตตอบแบบประชดนักข่าว ยิ่งทำให้เห็นว่าเขากำลังกดดัน และไม่พร้อมรับเสียงวิจารณ์ นี่แหละที่ทำให้เก้าอี้เริ่มร้อน!"</div>
        </div>""", unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="compare-box">
          <div class="compare-title">เปรียบเทียบคู่แค้น</div>
          <div class="compare-body">แมนฯ ยูไนเต็ด เพิ่งเอาชนะเราไป 3-2 เมื่อเร็วๆ นี้... ลองมองภาพรวมตอนนี้</div>
          <div class="compare-row">
            <div><div class="compare-liv">LIV</div><div class="compare-liv-sub">ทรงบอลอึดอัด โค้ชมีปัญหากับแฟน</div></div>
            <div class="compare-vs">VS</div>
            <div><div class="compare-mun">MUN</div><div class="compare-mun-sub">ชนะบิ๊กแมตช์ โมเมนตัมกำลังมา?</div></div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="comment-box"><div class="comment-title">เพื่อนๆ คิดยังไง? (จำลองคอมเมนต์)</div>', unsafe_allow_html=True)
        ba, bb, _ = st.columns([1.4, 1.8, 1.3])
        with ba:
            if st.button("🔴 ไล่สล็อตออก!", key="agree_btn", use_container_width=True):
                st.session_state.comments.insert(0,{
                    "user":f"Fan_{random.randint(1,999)}","text":AGREE_TEXT,
                    "ucls":"comment-user-dark","border":False})
                st.rerun()
        with bb:
            if st.button("⚪ ให้โอกาสไปก่อน", key="disagree_btn", use_container_width=True):
                st.session_state.comments.insert(0,{
                    "user":f"Fan_{random.randint(1,999)}","text":DISAGREE_TEXT,
                    "ucls":"comment-user-dark","border":False})
                st.rerun()

        chtml = "".join([
            f'<div class="comment-item {"comment-item-red" if c.get("border") else ""}">'
            # ใช้ .get() เพื่อป้องกัน Error ถ้าหา Key ไม่เจอ
f'<span class="{c.get("ucls", "comment-user-dark")}">{c.get("user", "Unknown")}:</span> {c.get("text", "")}</div>'
            for c in st.session_state.comments[:6]])
        st.markdown(chtml, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════
st.markdown("""
<div class="lfc-footer">
  <div class="footer-title">เจมส์ป๊อก LFC</div>
  <div class="footer-ref">ข้อมูลอ้างอิง: Paul Gorst (Tier 1), NBC Sports, Chelsea FC Official</div>
  <div class="footer-copy">&copy; 2026 เจมส์ป๊อก LFC Dashboard — 🐍 Streamlit + Plotly</div>
</div>
""", unsafe_allow_html=True)
