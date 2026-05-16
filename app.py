"""
เจมส์ป๊อก LFC Dashboard — Phase 2
✅ Data decoupled → match_data.json
✅ KeyError comment fix
✅ Doughnut possession chart (ใหม่)
✅ Mobile-friendly layout
"""
import json, random, pathlib
import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ══════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════
st.set_page_config(
    page_title="เจมส์ป๊อก LFC",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════
# LOAD DATA FROM JSON  ← Phase 2: แก้ข้อมูลที่นี่เลย
# ══════════════════════════════════════════════════
@st.cache_data
def load_match():
    p = pathlib.Path(__file__).parent / "match_data.json"
    with open(p, encoding="utf-8") as f:
        return json.load(f)

D = load_match()          # ตัวแปรหลัก
META   = D["meta"]
TL     = D["timeline"]
QUOTES = D["quotes"]
GRAV   = D["gravenberch"]
ROM    = D["romano"]
STATS  = D["stats"]
SPOT   = D["spotlight"]
ANA    = D["analysis"]
RIV    = D["rival_compare"]
DEF_CM = D["default_comments"]

AGREE_TEXT    = "เห็นด้วยกับพี่เจมส์ป๊อก สล็อตดื้อเกินไป ไม่ยอมรับผิด!"
DISAGREE_TEXT = "ผมว่าใจเย็นๆ ขุมกำลังเราเจ็บเยอะ สล็อตทำได้เท่านี้ก็โอเคแล้ว"

# ══════════════════════════════════════════════════
# CSS via components.html
# ══════════════════════════════════════════════════
components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap');
</style>
<script>
const css = `
  html,body,[class*="css"],.stMarkdown,.stMarkdown p,.stMarkdown div,.element-container
    { font-family:'Noto Sans Thai',sans-serif !important; }
  section[data-testid="stSidebar"] { display:none; }
  #MainMenu,footer,header { visibility:hidden; }
  .stApp { background:#f8fafc !important; }
  .block-container { padding-top:1rem !important; padding-bottom:2rem !important; }

  /* Header */
  .lfc-header { background:#C8102E; padding:14px 24px; border-radius:12px;
    display:flex; align-items:center; gap:12px;
    box-shadow:0 4px 12px rgba(200,16,46,.35); margin-bottom:20px; }
  .lfc-logo { width:44px;height:44px;background:#fff;border-radius:50%;
    border:2px solid #F6EB61;display:flex;align-items:center;
    justify-content:center;font-weight:900;font-size:16px;color:#C8102E;flex-shrink:0; }
  .lfc-title { color:#fff;font-size:19px;font-weight:800;
    text-transform:uppercase;letter-spacing:.06em;line-height:1.2; }
  .lfc-sub   { color:#F6EB61;font-size:10px;font-weight:600;
    text-transform:uppercase;letter-spacing:.12em; }
  .st-badge  { background:linear-gradient(135deg,#3b82f6,#1d4ed8);
    color:#fff !important;font-size:10px;font-weight:700;
    padding:2px 8px;border-radius:9999px;margin-left:8px;vertical-align:middle; }

  /* Card */
  .card { background:#fff;border-radius:14px;padding:20px;
    border:1px solid #e5e7eb;box-shadow:0 1px 5px rgba(0,0,0,.07);
    margin-bottom:14px;color:#1e293b; }
  .card-red-border  { border:1.5px solid #C8102E !important;background:#fef2f2 !important; }
  .card-gold-border { border:2px solid #F6EB61 !important; }

  /* Scoreboard */
  .scoreboard { background:#f1f5f9;border-radius:12px;padding:16px;
    display:flex;justify-content:space-around;align-items:center;
    text-align:center;margin-bottom:18px; }
  .score-team-liv { color:#b91c1c;font-weight:800;font-size:17px; }
  .score-team-che { color:#1d4ed8;font-weight:800;font-size:17px; }
  .score-num      { color:#0f172a;font-weight:900;font-size:42px;line-height:1; }
  .score-vs       { color:#64748b;font-weight:700;font-size:22px; }

  /* Timeline */
  .tl-row  { display:flex;margin-bottom:12px; }
  .tl-min  { width:40px;flex-shrink:0;color:#475569;font-weight:700;
    font-size:12px;padding-top:3px; }
  .tl-body { flex:1;padding-left:12px;border-left:3px solid #d1d5db;padding-bottom:12px; }
  .tl-body.red  { border-color:#C8102E; }
  .tl-body.blue { border-color:#1d4ed8; }
  .tl-title-red  { color:#b91c1c;font-weight:900;font-size:16px; }
  .tl-title-blue { color:#1d4ed8;font-weight:900;font-size:16px; }
  .tl-title-gray { color:#1e293b;font-weight:700;font-size:14px; }
  .tl-desc { color:#374151;font-size:13px;margin-top:3px;line-height:1.5; }

  /* Quotes */
  .quote-label { font-size:11px;font-weight:700;text-transform:uppercase;
    letter-spacing:.08em;margin-bottom:8px;display:block; }
  .quote-text  { font-size:15px;font-style:italic;color:#1e293b;
    margin-bottom:10px;line-height:1.6; }
  .quote-bold  { font-size:18px;font-weight:800;color:#0f172a;margin-bottom:10px; }
  .quote-note  { font-size:13px;color:#4b5563;line-height:1.5; }

  /* Romano */
  .romano-box   { background:#1e293b;border-radius:14px;padding:20px;
    display:flex;align-items:flex-start;gap:12px;margin-top:12px; }
  .romano-title { color:#F6EB61;font-weight:700;margin-bottom:4px;font-size:14px; }
  .romano-text  { color:#cbd5e1;font-size:13px;line-height:1.6; }
  .romano-text strong { color:#fff; }

  /* Gravenberch */
  .grav-card  { background:#fff;border-radius:14px;padding:16px;
    border:1px solid #e5e7eb;display:flex;gap:12px;
    align-items:flex-start;margin-top:10px; }
  .grav-icon  { font-size:30px;flex-shrink:0; }
  .grav-label { color:#475569;font-size:11px;font-weight:700;
    text-transform:uppercase;letter-spacing:.08em; }
  .grav-quote { color:#1e293b;font-weight:600;font-size:14px;margin:4px 0; }
  .grav-desc  { color:#475569;font-size:13px;line-height:1.5; }

  /* Headings */
  .drama-heading { color:#0f172a;font-size:19px;font-weight:800;
    border-left:4px solid #C8102E;padding-left:12px;margin-bottom:14px; }
  .sec-heading   { color:#0f172a;font-size:26px;font-weight:800;
    text-transform:uppercase;text-align:center;margin-bottom:6px; }
  .sec-sub       { color:#475569;font-size:15px;text-align:center;
    max-width:660px;margin:0 auto 24px;line-height:1.6; }

  /* Stat cards */
  .stat-card-red  { background:#fef2f2;border:1px solid #fecaca;
    border-radius:12px;padding:14px;text-align:center; }
  .stat-card-blue { background:#eff6ff;border:1px solid #bfdbfe;
    border-radius:12px;padding:14px;text-align:center; }
  .stat-card-gray { background:#f8fafc;border:1px solid #e2e8f0;
    border-radius:12px;padding:14px;text-align:center;margin-top:10px; }
  .stat-num-red   { color:#b91c1c;font-size:36px;font-weight:900; }
  .stat-num-blue  { color:#1d4ed8;font-size:36px;font-weight:900; }
  .stat-num-gray  { color:#0f172a;font-size:26px;font-weight:900; }
  .stat-label     { color:#374151;font-size:11px;font-weight:700;
    text-transform:uppercase;letter-spacing:.05em;margin-top:3px; }

  /* Progress */
  .progress-wrap { background:#e5e7eb;border-radius:9999px;height:7px;margin:5px 0 10px; }
  .progress-fill { background:#C8102E;border-radius:9999px;height:7px; }

  /* Compare */
  .compare-box   { background:linear-gradient(135deg,#7f1d1d,#000);
    border-radius:14px;padding:24px;margin-bottom:14px; }
  .compare-title   { color:#F6EB61;font-weight:700;font-size:16px;margin-bottom:8px; }
  .compare-body    { color:#e2e8f0;font-size:13px;margin-bottom:14px;line-height:1.5; }
  .compare-row     { display:flex;justify-content:space-around;text-align:center;align-items:center; }
  .compare-liv     { color:#fff;font-size:20px;font-weight:900; }
  .compare-liv-sub { color:#fca5a5;font-size:11px; }
  .compare-vs      { color:#e2e8f0;font-size:18px;font-weight:700; }
  .compare-riv     { font-size:20px;font-weight:900; }
  .compare-riv-sub { font-size:11px;color:#94a3b8; }

  /* Comment */
  .comment-box   { background:#f1f5f9;border:1px solid #e2e8f0;
    border-radius:14px;padding:16px; }
  .comment-title { color:#0f172a;font-weight:700;margin-bottom:10px;font-size:14px; }
  .comment-item  { background:#fff;border-radius:8px;padding:9px 13px;
    margin-bottom:7px;box-shadow:0 1px 3px rgba(0,0,0,.06);
    font-size:13px;color:#374151;line-height:1.5; }
  .comment-item-red { border-left:3px solid #C8102E; }

  /* Editor */
  .editor-card  { background:#fff;border-radius:14px;padding:26px;
    border-top:4px solid #C8102E;box-shadow:0 1px 5px rgba(0,0,0,.07); }
  .editor-title { color:#0f172a;font-size:19px;font-weight:900;margin-bottom:10px; }
  .editor-body  { color:#374151;line-height:1.8;margin-bottom:10px;font-size:14px; }
  .editor-quote { color:#1e293b;font-weight:600;line-height:1.8;font-size:14px; }

  /* Footer */
  .lfc-footer   { background:#111827;padding:20px;text-align:center;
    border-radius:14px;margin-top:32px; }
  .footer-title { color:#fff;font-weight:700;font-size:15px;margin-bottom:4px; }
  .footer-ref   { color:#9ca3af;font-size:12px;margin-bottom:3px; }
  .footer-copy  { color:#6b7280;font-size:11px; }

  /* Mobile responsive */
  @media (max-width:768px) {
    .lfc-title { font-size:15px; }
    .sec-heading { font-size:20px; }
    .scoreboard { padding:12px; }
    .score-num  { font-size:32px; }
    .card { padding:14px; }
  }
`;
const s = window.parent.document.createElement('style');
s.textContent = css;
window.parent.document.head.appendChild(s);
</script>
""", height=0, scrolling=False)

# ══════════════════════════════════════════════════
# SESSION STATE  — แก้ KeyError: ใช้ .get() ทุกที่
# ══════════════════════════════════════════════════
if "tab" not in st.session_state:
    st.session_state.tab = "hot"

if "comments" not in st.session_state:
    st.session_state.comments = [
        {
            "user":       c.get("user", "Unknown"),
            "text":       c.get("text", ""),
            "user_color": c.get("user_color", "#1e293b"),
            "border":     c.get("border", False),
        }
        for c in DEF_CM
    ]

# ── helper: render comment HTML (ปลอดภัย ไม่มี KeyError) ──
def render_comment(c: dict) -> str:
    color  = c.get("user_color", "#1e293b")
    user   = c.get("user", "Fan")
    text   = c.get("text", "")
    border = "comment-item-red" if c.get("border") else ""
    return (
        f'<div class="comment-item {border}">'
        f'<span style="color:{color};font-weight:700;">{user}:</span> {text}'
        f'</div>'
    )

# ── helper: timeline CSS class ──
def tl_cls(t: str):
    return {"goal_liv": ("tl-title-red",  "red"),
            "goal_che": ("tl-title-blue", "blue")}.get(t, ("tl-title-gray", ""))

# ══════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════
st.markdown(f"""
<div class="lfc-header">
  <div class="lfc-logo">JP</div>
  <div>
    <div class="lfc-title">เจมส์ป๊อก LFC <span class="st-badge">Phase 2</span></div>
    <div class="lfc-sub">ขยี้ทุกประเด็นหงส์แดง • {META['competition']} MW{META['matchweek']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB NAV
# ══════════════════════════════════════════════════
t1, t2, t3, _ = st.columns([2.4, 1.4, 2.3, 2.4])
with t1:
    if st.button(f"🔥 ประเด็นร้อน ({META['home_short']} {META['home_score']}-{META['away_score']} {META['away_short']})",
                 use_container_width=True, key="btn_hot",
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

st.markdown("<hr style='border:none;border-top:1px solid #e5e7eb;margin:10px 0 22px;'>",
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

    # ── LEFT: Scoreboard + Timeline ──
    with left:
        tl_rows = ""
        for e in TL:
            tc, bc = tl_cls(e["type"])
            tl_rows += (
                f'<div class="tl-row">'
                f'<div class="tl-min">{e["minute"]}</div>'
                f'<div class="tl-body {bc}">'
                f'<div class="{tc}">{e["title"]}</div>'
                f'<div class="tl-desc">{e["detail"]}</div>'
                f'</div></div>'
            )
        st.markdown(f"""
        <div class="card">
          <div style="font-size:16px;font-weight:800;color:#0f172a;
            border-bottom:2px solid #C8102E;padding-bottom:7px;
            margin-bottom:14px;display:inline-block;">
            ผลการแข่งขัน &amp; ไทม์ไลน์
          </div>
          <div class="scoreboard">
            <div>
              <div class="score-team-liv">{META['home_short']}</div>
              <div class="score-num">{META['home_score']}</div>
            </div>
            <div class="score-vs">VS</div>
            <div>
              <div class="score-team-che">{META['away_short']}</div>
              <div class="score-num">{META['away_score']}</div>
            </div>
          </div>
          {tl_rows}
        </div>
        """, unsafe_allow_html=True)

    # ── RIGHT: Quote cards + Gravenberch + Romano ──
    with right:
        st.markdown('<div class="drama-heading">ประเด็นเดือดหลังเกม</div>',
                    unsafe_allow_html=True)
        d1, d2 = st.columns(2, gap="medium")
        cols = [d1, d2]
        for i, q in enumerate(QUOTES):
            is_hot = q["style"] == "hot"
            cls    = "card card-red-border" if is_hot else "card"
            qtag   = "quote-bold" if is_hot else "quote-text"
            with cols[i % 2]:
                st.markdown(f"""
                <div class="{cls}">
                  <span class="quote-label" style="color:#C8102E;">{q['speaker']}</span>
                  <div class="{qtag}">{q['quote']}</div>
                  <div class="quote-note">{q['note']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="grav-card">
          <div class="grav-icon">🗣️</div>
          <div>
            <div class="grav-label">ไรอัน กราเฟนแบร์ก ตัดพ้อแฟนบอล</div>
            <div class="grav-quote">{GRAV['quote']}</div>
            <div class="grav-desc">{GRAV['detail']}</div>
          </div>
        </div>
        <div class="romano-box">
          <div style="font-size:26px;flex-shrink:0;">📰</div>
          <div>
            <div class="romano-title">Fabrizio Romano Update</div>
            <div class="romano-text">{ROM['update']}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION 2 — เจาะสถิติ  (Phase 2: เพิ่ม Doughnut possession)
# ══════════════════════════════════════════════════════════════
elif st.session_state.tab == "stats":

    st.markdown('<p class="sec-heading">เจาะสถิติ ฟ้องด้วยตัวเลข</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">สถิติจากเกมนี้บอกอะไรเรา? ลิเวอร์พูลถอยไปรับจริง หรือแค่เจาะเชลซีไม่เข้า มาดูตัวเลขเปรียบเทียบกัน</p>', unsafe_allow_html=True)

    # ── Row 1: Radar + Quick stats ──
    chart_col, right_col = st.columns(2, gap="large")

    with chart_col:
        st.markdown('<div class="card"><p style="font-size:16px;font-weight:800;color:#0f172a;text-align:center;margin-bottom:6px;">สถิติภาพรวมเกมรุกและรับ</p>', unsafe_allow_html=True)
        rl  = STATS["radar_labels"] + [STATS["radar_labels"][0]]
        hv  = STATS["home_values"]  + [STATS["home_values"][0]]
        av  = STATS["away_values"]  + [STATS["away_values"][0]]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=hv, theta=rl, fill="toself",
            name=META["home_short"],
            line=dict(color="#C8102E",width=2), fillcolor="rgba(200,16,46,0.15)",
            marker=dict(color="#C8102E")))
        fig_r.add_trace(go.Scatterpolar(r=av, theta=rl, fill="toself",
            name=META["away_short"],
            line=dict(color="#1d4ed8",width=2), fillcolor="rgba(29,78,216,0.15)",
            marker=dict(color="#1d4ed8")))
        fig_r.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0,100],
                                tickfont=dict(size=10, color="#475569")),
                angularaxis=dict(tickfont=dict(size=11, color="#1e293b")),
                bgcolor="#f8fafc"),
            legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center",
                        font=dict(size=13, color="#1e293b")),
            paper_bgcolor="#ffffff", margin=dict(l=40,r=40,t=20,b=60), height=360)
        st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        # Quick stat cards from JSON
        s1, s2 = st.columns(2)
        qs = STATS["quick"]
        style_map = {
            "red":  ('<div class="stat-card-red">',  "stat-num-red"),
            "blue": ('<div class="stat-card-blue">', "stat-num-blue"),
            "gray": ('<div class="stat-card-gray">', "stat-num-gray"),
        }
        with s1:
            tag, num_cls = style_map[qs[0]["style"]]
            st.markdown(f'{tag}<div class="{num_cls}">{qs[0]["value"]}</div><div class="stat-label">{qs[0]["label"]}</div></div>', unsafe_allow_html=True)
        with s2:
            tag, num_cls = style_map[qs[1]["style"]]
            st.markdown(f'{tag}<div class="{num_cls}">{qs[1]["value"]}</div><div class="stat-label">{qs[1]["label"]}</div></div>', unsafe_allow_html=True)
        tag, num_cls = style_map[qs[2]["style"]]
        st.markdown(f'{tag}<div class="{num_cls}">{qs[2]["value"]}</div><div class="stat-label">{qs[2]["label"]}</div></div>', unsafe_allow_html=True)

        # ── Spotlight (from JSON) ──
        spot_stats_html = ""
        for s in SPOT["stats"]:
            spot_stats_html += f"""
            <div style="display:flex;justify-content:space-between;margin-top:6px;">
              <span style="font-size:13px;font-weight:600;color:#374151;">{s['label']}</span>
              <span style="font-weight:800;color:#1e293b;">{s['value']}</span>
            </div>"""
            if s["pct"] is not None:
                spot_stats_html += f'<div class="progress-wrap"><div class="progress-fill" style="width:{s["pct"]}%;"></div></div>'

        st.markdown(f"""
        <div class="card card-gold-border" style="margin-top:12px;">
          <div style="font-size:14px;font-weight:800;color:#1e293b;margin-bottom:7px;">
            🌟 Spotlight: {SPOT['name']} ({SPOT['age']} ปี)
          </div>
          <div style="color:#374151;font-size:13px;margin-bottom:10px;">
            ดาวรุ่งที่โชว์ฟอร์มได้โดดเด่นที่สุดในแนวรุก ก่อนถูกเปลี่ยนตัวออกจนเกิดเสียงโห่
          </div>
          {spot_stats_html}
          <div style="font-size:11px;color:#64748b;margin-top:8px;font-style:italic;">
            {SPOT['note']}
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Row 2: Doughnut Possession (ใหม่ Phase 2) + Momentum ──
    dough_col, mom_col = st.columns([1, 2], gap="large")

    with dough_col:
        st.markdown('<div class="card"><p style="font-size:16px;font-weight:800;color:#0f172a;text-align:center;margin-bottom:6px;">การครองบอล</p>', unsafe_allow_html=True)
        poss = STATS["possession"]
        fig_d = go.Figure(go.Pie(
            labels=[META["home_short"], META["away_short"]],
            values=[poss["home"], poss["away"]],
            hole=0.6,
            marker=dict(colors=["#C8102E","#1d4ed8"],
                        line=dict(color="#fff", width=3)),
            textinfo="label+percent",
            textfont=dict(size=14, color="#fff"),
            insidetextorientation="auto",
        ))
        fig_d.add_annotation(
            text=f"<b>{poss['home']}%</b><br><span style='font-size:11px'>LIV</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#C8102E"))
        fig_d.update_layout(
            showlegend=False,
            paper_bgcolor="#ffffff",
            margin=dict(l=10,r=10,t=10,b=10),
            height=220)
        st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    with mom_col:
        st.markdown('<div class="card"><p style="font-size:16px;font-weight:800;color:#0f172a;text-align:center;margin-bottom:4px;">โมเมนตัมการบุก (จำลอง)</p><p style="color:#64748b;font-size:12px;text-align:center;margin-bottom:8px;">บวก = หงส์บุก · ลบ = สิงห์บุก</p>', unsafe_allow_html=True)

        mx   = STATS["momentum_x"]
        my   = STATS["momentum_y"]
        tips = {int(k): v for k, v in STATS["momentum_tips"].items()}
        pt_colors = ["#C8102E" if i in tips else "#1e293b" for i in range(len(my))]
        hov = [tips.get(i, f"โมเมนตัม: {v}") for i, v in enumerate(my)]

        fig_m = go.Figure()
        fig_m.add_hrect(y0=0,  y1=10, fillcolor="rgba(200,16,46,0.05)", line_width=0)
        fig_m.add_hrect(y0=-10,y1=0,  fillcolor="rgba(29,78,216,0.05)", line_width=0)
        fig_m.add_trace(go.Scatter(
            x=mx, y=my, mode="lines+markers",
            line=dict(color="#1e293b",width=3,shape="spline"),
            fill="tozeroy", fillcolor="rgba(30,41,59,0.08)",
            marker=dict(size=9,color=pt_colors,line=dict(color="#fff",width=2)),
            hovertext=hov, hoverinfo="text", name="โมเมนตัม"))
        fig_m.add_hline(y=0, line_color="#0f172a", line_width=1.5)
        fig_m.add_annotation(x="15",y=5, text="🔴 LFC", showarrow=False,
                             font=dict(color="#C8102E",size=11), yshift=16)
        fig_m.add_annotation(x="75",y=-8,text="🔵 CHE", showarrow=False,
                             font=dict(color="#1d4ed8",size=11), yshift=-18)
        fig_m.update_layout(
            xaxis=dict(title="นาที",tickfont=dict(size=11,color="#1e293b"),gridcolor="#e5e7eb"),
            yaxis=dict(range=[-10,10],showticklabels=False,gridcolor="#e5e7eb"),
            paper_bgcolor="#ffffff",plot_bgcolor="#ffffff",
            showlegend=False, margin=dict(l=16,r=16,t=8,b=36), height=220)
        st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SECTION 3 — วิเคราะห์
# ══════════════════════════════════════════════════════════════
elif st.session_state.tab == "analysis":

    st.markdown('<p class="sec-heading">โต๊ะรก วิจารณ์</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">ถึงเวลาตบขมับ! วิเคราะห์เจาะลึกแบบไม่เกรงใจใคร สไตล์ เจมส์ป๊อก LFC</p>', unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown(f"""
        <div class="editor-card">
          <div class="editor-title">{ANA['title']}</div>
          <div class="editor-body">{ANA['body']}</div>
          <div class="editor-quote">{ANA['quote']}</div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        riv_color = RIV.get("rival_color","#ef4444")
        st.markdown(f"""
        <div class="compare-box">
          <div class="compare-title">เปรียบเทียบคู่แค้น</div>
          <div class="compare-body">{RIV['context']}</div>
          <div class="compare-row">
            <div>
              <div class="compare-liv">{META['home_short']}</div>
              <div class="compare-liv-sub">{RIV['home_desc']}</div>
            </div>
            <div class="compare-vs">VS</div>
            <div>
              <div class="compare-riv" style="color:{riv_color};">{RIV['rival_short']}</div>
              <div class="compare-riv-sub">{RIV['rival_desc']}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Comment section (KeyError-proof) ──
        st.markdown('<div class="comment-box"><div class="comment-title">เพื่อนๆ คิดยังไง?</div>', unsafe_allow_html=True)
        ba, bb, _ = st.columns([1.4, 1.8, 1.3])
        with ba:
            if st.button("🔴 ไล่สล็อตออก!", key="agree_btn", use_container_width=True):
                st.session_state.comments.insert(0, {
                    "user":       f"Fan_{random.randint(1,999)}",
                    "text":       AGREE_TEXT,
                    "user_color": "#1e293b",
                    "border":     False,
                })
                st.rerun()
        with bb:
            if st.button("⚪ ให้โอกาสไปก่อน", key="disagree_btn", use_container_width=True):
                st.session_state.comments.insert(0, {
                    "user":       f"Fan_{random.randint(1,999)}",
                    "text":       DISAGREE_TEXT,
                    "user_color": "#1e293b",
                    "border":     False,
                })
                st.rerun()

        # render ทุก comment ผ่าน helper — ไม่มี KeyError อีกแล้ว
        chtml = "".join(render_comment(c) for c in st.session_state.comments[:6])
        st.markdown(chtml, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════
st.markdown(f"""
<div class="lfc-footer">
  <div class="footer-title">เจมส์ป๊อก LFC</div>
  <div class="footer-ref">{META['competition']} • {META['venue']} • {META['date']}</div>
  <div class="footer-copy">&copy; 2026 JamesPok LFC — Phase 2 · Data-Driven Edition 🐍</div>
</div>
""", unsafe_allow_html=True)
