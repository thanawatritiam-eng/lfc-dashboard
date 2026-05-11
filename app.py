"""
เจมส์ป๊อก LFC Dashboard - Python Version
ใช้ Flask + Plotly แทน HTML/Chart.js
รัน: python app.py  แล้วเปิด http://localhost:5000
"""

import random
import json
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# ============================================================
# DATA LAYER — ข้อมูลทั้งหมดของ Dashboard
# ============================================================

MATCH_DATA = {
    "home": {"name": "LIV", "score": 1, "color": "#b91c1c"},
    "away": {"name": "CHE", "score": 1, "color": "#1d4ed8"},
}

TIMELINE_EVENTS = [
    {
        "minute": "6'",
        "type": "goal_liv",
        "title": "GOAL! (LIV)",
        "detail": "ริโอ อึงูโมฮา ไหลบอลให้ <strong>ไรอัน กราเฟนแบร์ก</strong> ปั่นโค้งสุดสวย หงส์ขึ้นนำ!",
        "border_color": "#C8102E",
        "title_color": "#b91c1c",
    },
    {
        "minute": "35'",
        "type": "goal_che",
        "title": "GOAL! (CHE)",
        "detail": "<strong>เอ็นโซ เฟร์นานเดซ</strong> ปั่นฟรีคิกแฉลบเข้าประตู สิงห์บลูส์ตีเสมอ",
        "border_color": "#1d4ed8",
        "title_color": "#1d4ed8",
    },
    {
        "minute": "67'",
        "type": "drama",
        "title": "จุดเปลี่ยน & ดราม่า",
        "detail": "สล็อตถอด <strong>อึงูโมฮา</strong> ที่กำลังเล่นดีออก แฟนบอลในแอนฟิลด์เริ่มส่งเสียงโห่",
        "border_color": "#d1d5db",
        "title_color": "#1e293b",
    },
    {
        "minute": "FT",
        "type": "fulltime",
        "title": "จบเกม เสมอ 1-1",
        "detail": "โซบอสซ์ไลยิงชนเสา ฟาน ไดจ์คโหม่งชนคาน เจาะไม่เข้า",
        "border_color": "#d1d5db",
        "title_color": "#1e293b",
    },
]

DRAMA_CARDS = [
    {
        "id": "slot",
        "label": "อาร์เน่อ สล็อต",
        "label_color": "#C8102E",
        "quote": '"พวกคุณคิดจริงๆ เหรอว่าผมสั่งให้ทีมถอยไปรับ? นี่คุณเห็นผมตะโกนสั่งข้างสนามว่า \'ถอยไปเดี๋ยวนี้! กลับไปเฝ้าเขตโทษตัวเอง\' หรือไง?"',
        "note": "<strong>เจมส์ป๊อกขยี้:</strong> กุนซือหงส์แดงตอบคำถามแบบติดประชดหลังโดนวิจารณ์เรื่องแทคติกครึ่งหลังที่ดูถอยไปตั้งรับมากเกินไป",
        "bg": "#ffffff",
        "border": "#e5e7eb",
        "hot": False,
    },
    {
        "id": "salah",
        "label": "ระเบิดจากซาลาห์!",
        "label_color": "#C8102E",
        "quote": '"ทีมชุดนี้ ขาดผู้นำ"',
        "note": "<strong>รายงานจาก Paul Gorst (Tier 1):</strong> โม ซาลาห์ ให้สัมภาษณ์แทงใจดำ ทำเอาสล็อตหัวเสียสุดๆ บ่งบอกถึงรอยร้าวในแคมป์",
        "bg": "#fef2f2",
        "border": "#C8102E",
        "hot": True,
    },
]

STATS_RADAR = {
    "labels": ["การครองบอล (%)", "โอกาสยิง", "ยิงเข้ากรอบ", "จ่ายบอลสำเร็จ (%)", "เตะมุม", "ฟาวล์"],
    "liverpool": [42, 11, 4, 81, 6, 12],
    "chelsea":   [58, 14, 5, 87, 5, 10],
}

MOMENTUM_DATA = {
    "labels": ["0", "15", "30", "HT", "60", "75", "90"],
    "values": [0, 5, -2, -5, 2, -8, -4],
    "tooltips": {
        0: "นาที 6: กราเฟนแบร์กยิงนำ",
        2: "นาที 35: เอ็นโซ่ตีเสมอ",
        5: "นาที 67: ถอดอึงูโมฮา โมเมนตัมตก",
    },
}

PLAYER_SPOTLIGHT = {
    "name": "ริโอ อึงูโมฮา",
    "age": 17,
    "dribbles": "4/5 ครั้ง",
    "dribble_pct": 80,
    "assists": 1,
    "note": "*สล็อตอ้างว่าเปลี่ยนออกเพราะนักเตะมีอาการตะคริว",
}

INITIAL_COMMENTS = [
    {"user": "Kopite_1989", "text": "ซาลาห์พูดถูก ทีมขาดผู้นำจริงๆ กัปตันหายไปไหนตอนทีมเป๋?",
     "user_color": "#1d4ed8", "border": False},
    {"user": "JamesPok LFC", "text": "ตบขมับเลยครับแมตช์นี้!",
     "user_color": "#1e293b", "border": True},
]

# In-memory comment store
comment_store = list(INITIAL_COMMENTS)


# ============================================================
# PLOTLY CHART BUILDERS
# ============================================================

def build_radar_chart():
    """
    สร้าง Radar Chart ด้วย Plotly (ถ้ามี) หรือคืน config สำหรับ Chart.js (fallback)
    """
    try:
        import plotly.graph_objects as go

        labels = STATS_RADAR["labels"] + [STATS_RADAR["labels"][0]]
        liv = STATS_RADAR["liverpool"] + [STATS_RADAR["liverpool"][0]]
        che = STATS_RADAR["chelsea"]   + [STATS_RADAR["chelsea"][0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=liv, theta=labels, fill="toself", name="ลิเวอร์พูล",
            line=dict(color="#C8102E", width=2),
            fillcolor="rgba(200,16,46,0.15)",
            marker=dict(color="#C8102E"),
        ))
        fig.add_trace(go.Scatterpolar(
            r=che, theta=labels, fill="toself", name="เชลซี",
            line=dict(color="#1d4ed8", width=2),
            fillcolor="rgba(29,78,216,0.15)",
            marker=dict(color="#1d4ed8"),
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100],
                                tickfont=dict(size=10, color="#475569")),
                angularaxis=dict(tickfont=dict(size=11, color="#1e293b")),
                bgcolor="#f8fafc",
            ),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2,
                        xanchor="center", x=0.5,
                        font=dict(size=13, color="#1e293b")),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            margin=dict(l=60, r=60, t=30, b=60),
            height=380,
        )
        return {"engine": "plotly", "json": fig.to_json()}

    except ImportError:
        # Fallback → Chart.js config (rendered by JS in template)
        return {
            "engine": "chartjs",
            "type": "radar",
            "data": {
                "labels": STATS_RADAR["labels"],
                "datasets": [
                    {
                        "label": "ลิเวอร์พูล",
                        "data": STATS_RADAR["liverpool"],
                        "backgroundColor": "rgba(200,16,46,0.2)",
                        "borderColor": "#C8102E",
                        "pointBackgroundColor": "#C8102E",
                        "borderWidth": 2,
                    },
                    {
                        "label": "เชลซี",
                        "data": STATS_RADAR["chelsea"],
                        "backgroundColor": "rgba(37,99,235,0.2)",
                        "borderColor": "#2563eb",
                        "pointBackgroundColor": "#2563eb",
                        "borderWidth": 2,
                    },
                ],
            },
            "options": {
                "maintainAspectRatio": False,
                "responsive": True,
                "scales": {"r": {"angleLines": {"display": True}, "suggestedMin": 0}},
                "plugins": {"legend": {"position": "bottom"}},
            },
        }


def build_momentum_chart():
    """
    สร้าง Line Chart ด้วย Plotly (ถ้ามี) หรือคืน config สำหรับ Chart.js (fallback)
    """
    try:
        import plotly.graph_objects as go

        labels = MOMENTUM_DATA["labels"]
        values = MOMENTUM_DATA["values"]
        tips   = MOMENTUM_DATA["tooltips"]

        point_colors = ["#C8102E" if i in tips else "#1e293b" for i in range(len(values))]
        hover_texts  = [tips.get(i, f"โมเมนตัม: {v}") for i, v in enumerate(values)]

        fig = go.Figure()
        fig.add_hrect(y0=0,   y1=10,  fillcolor="rgba(200,16,46,0.05)", line_width=0)
        fig.add_hrect(y0=-10, y1=0,   fillcolor="rgba(29,78,216,0.05)", line_width=0)
        fig.add_trace(go.Scatter(
            x=labels, y=values,
            mode="lines+markers",
            line=dict(color="#1e293b", width=3, shape="spline", smoothing=0.4),
            fill="tozeroy",
            fillcolor="rgba(30,41,59,0.08)",
            marker=dict(size=10, color=point_colors,
                        line=dict(color="#ffffff", width=2)),
            hovertext=hover_texts,
            hoverinfo="text",
            name="โมเมนตัม",
        ))
        fig.add_hline(y=0, line_color="#0f172a", line_width=1.5)
        fig.add_annotation(x="15", y=5,  text="LFC ✦", showarrow=False,
                           font=dict(color="#C8102E", size=11), yshift=14)
        fig.add_annotation(x="75", y=-8, text="CHE ✦", showarrow=False,
                           font=dict(color="#1d4ed8", size=11), yshift=-16)
        fig.update_layout(
            xaxis=dict(title="นาที", tickfont=dict(size=12, color="#1e293b"),
                       gridcolor="#e5e7eb", showgrid=True),
            yaxis=dict(range=[-10, 10], showticklabels=False, gridcolor="#e5e7eb"),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=40),
            height=300,
        )
        return {"engine": "plotly", "json": fig.to_json()}

    except ImportError:
        return {
            "engine": "chartjs",
            "type": "line",
            "data": {
                "labels": MOMENTUM_DATA["labels"],
                "datasets": [
                    {
                        "label": "ดัชนีโมเมนตัม (บวก=LIV, ลบ=CHE)",
                        "data": MOMENTUM_DATA["values"],
                        "borderColor": "#1e293b",
                        "backgroundColor": "rgba(30,41,59,0.1)",
                        "borderWidth": 3,
                        "tension": 0.4,
                        "fill": True,
                        "pointRadius": 5,
                    }
                ],
            },
            "options": {
                "maintainAspectRatio": False,
                "responsive": True,
                "scales": {
                    "y": {
                        "min": -10,
                        "max": 10,
                        "ticks": {"display": False},
                    }
                },
                "plugins": {"legend": {"display": False}},
            },
        }


# ============================================================
# HTML TEMPLATE (Jinja2) — ครบ 100% โครงสร้างเดิม
# ============================================================

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>เจมส์ป๊อก LFC - ขยี้ทุกประเด็นหงส์แดง (Python Edition)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap" rel="stylesheet"/>
  <style>
    body { font-family:'Noto Sans Thai',sans-serif; background:#f8fafc; color:#1e293b; }

    /* Liverpool Brand */
    .bg-lfc-red   { background-color:#C8102E; }
    .text-lfc-red { color:#C8102E; }
    .border-lfc-red { border-color:#C8102E; }
    .text-lfc-gold  { color:#F6EB61; }

    /* Tab animation */
    .section-hidden { display:none; }
    .section-active  { display:block; animation:fadeIn .5s ease-in-out; }
    @keyframes fadeIn { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }

    /* Stat card hover */
    .stat-card { transition:transform .2s,box-shadow .2s; }
    .stat-card:hover { transform:translateY(-5px);
      box-shadow:0 10px 15px -3px rgba(0,0,0,.1),0 4px 6px -2px rgba(0,0,0,.05); }

    /* Progress bar */
    .progress-bar { height:8px; border-radius:9999px; background:#e5e7eb; }
    .progress-fill { height:100%; border-radius:9999px; background:#C8102E; }

    /* Comment section scroll */
    #comments-list { max-height:160px; overflow-y:auto; }

    /* Python badge */
    .py-badge {
      background:linear-gradient(135deg,#3b82f6,#1d4ed8);
      color:#fff; font-size:10px; font-weight:700;
      padding:2px 8px; border-radius:9999px;
      letter-spacing:.05em; vertical-align:middle;
    }
  </style>
</head>

<body class="antialiased min-h-screen flex flex-col">

<!-- ═══════════════════════════════════════
     HEADER
═══════════════════════════════════════ -->
<header class="bg-lfc-red shadow-md sticky top-0 z-50">
  <div class="container mx-auto px-4 py-4 flex justify-between items-center">

    <!-- Logo -->
    <div class="flex items-center space-x-3">
      <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center
                  font-bold text-xl border-2 border-yellow-300 text-lfc-red">JP</div>
      <div>
        <h1 class="text-2xl font-extrabold uppercase tracking-wider text-white">
          เจมส์ป๊อก LFC
          <span class="py-badge ml-2">Python</span>
        </h1>
        <p class="text-xs text-lfc-gold font-semibold uppercase tracking-widest">
          ขยี้ทุกประเด็นหงส์แดง
        </p>
      </div>
    </div>

    <!-- Desktop Nav -->
    <nav class="hidden md:flex space-x-6">
      <button onclick="switchTab('hot-topics')" id="nav-hot-topics"
        class="nav-btn font-semibold text-white hover:text-yellow-300 transition-colors
               border-b-2 border-white pb-1">
        ประเด็นร้อน (Chelsea 1-1)
      </button>
      <button onclick="switchTab('match-stats')" id="nav-match-stats"
        class="nav-btn font-semibold text-white hover:text-yellow-300 transition-colors
               border-b-2 border-transparent pb-1">
        เจาะสถิติ
      </button>
      <button onclick="switchTab('analysis')" id="nav-analysis"
        class="nav-btn font-semibold text-white hover:text-yellow-300 transition-colors
               border-b-2 border-transparent pb-1">
        วิเคราะห์สไตล์โต๊ะรก
      </button>
    </nav>

    <!-- Mobile hamburger -->
    <button class="md:hidden text-white text-2xl"
      onclick="document.getElementById('mobile-menu').classList.toggle('hidden')">☰</button>
  </div>

  <!-- Mobile Menu -->
  <div id="mobile-menu" class="hidden md:hidden pb-4" style="background:#991b1b;">
    <button onclick="switchTab('hot-topics');document.getElementById('mobile-menu').classList.add('hidden')"
      class="block w-full text-left px-4 py-2 text-white hover:bg-red-700">ประเด็นร้อน</button>
    <button onclick="switchTab('match-stats');document.getElementById('mobile-menu').classList.add('hidden')"
      class="block w-full text-left px-4 py-2 text-white hover:bg-red-700">เจาะสถิติ</button>
    <button onclick="switchTab('analysis');document.getElementById('mobile-menu').classList.add('hidden')"
      class="block w-full text-left px-4 py-2 text-white hover:bg-red-700">วิเคราะห์สไตล์โต๊ะรก</button>
  </div>
</header>

<!-- ═══════════════════════════════════════
     MAIN
═══════════════════════════════════════ -->
<main class="flex-grow container mx-auto px-4 py-8">

  <!-- ─────────────────────────────────────
       SECTION 1 : ประเด็นร้อน
  ───────────────────────────────────── -->
  <section id="hot-topics" class="section-active">
    <div class="mb-8 text-center">
      <h2 class="text-4xl font-bold text-gray-900 mb-4 uppercase tracking-tight">
        หงส์สะดุดอีก! เสียงโห่ลั่นแอนฟิลด์
      </h2>
      <p class="text-xl text-gray-600 max-w-3xl mx-auto">
        ควันหลงและดราม่าหลังเกมที่เครื่องจักรสีแดงทำได้แค่เปิดบ้านเสมอ เชลซี 1-1
        สรุปเหตุการณ์สำคัญและระเบิดลูกใหญ่จากนักเตะ
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

      <!-- Match Result & Timeline -->
      <div class="lg:col-span-1 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 class="text-xl font-bold text-gray-900 border-b-2 border-lfc-red pb-2 mb-4 inline-block">
          ผลการแข่งขัน &amp; ไทม์ไลน์
        </h3>

        <!-- Scoreboard -->
        <div class="flex justify-between items-center bg-gray-50 p-4 rounded-lg mb-6">
          <div class="text-center">
            <span class="block font-bold text-lg" style="color:#b91c1c;">LIV</span>
            <span class="text-3xl font-black text-gray-900">1</span>
          </div>
          <div class="font-bold text-xl text-gray-400">VS</div>
          <div class="text-center">
            <span class="block font-bold text-lg" style="color:#1d4ed8;">CHE</span>
            <span class="text-3xl font-black text-gray-900">1</span>
          </div>
        </div>

        <!-- Timeline -->
        <div class="space-y-4">
          {% for evt in timeline %}
          <div class="flex">
            <div class="w-12 text-sm font-bold text-gray-500 pt-1">{{ evt.minute }}</div>
            <div class="flex-1 border-l-2 pl-4 pb-4"
                 style="border-color:{{ evt.border_color }};">
              <span class="text-xl font-black leading-none block mb-1"
                    style="color:{{ evt.title_color }};">{{ evt.title }}</span>
              <p class="text-sm text-gray-700">{{ evt.detail | safe }}</p>
            </div>
          </div>
          {% endfor %}
        </div>
      </div>

      <!-- Drama Cards -->
      <div class="lg:col-span-2 space-y-6">
        <h3 class="text-2xl font-bold text-gray-900 border-l-4 border-lfc-red pl-3">
          ประเด็นเดือดหลังเกม
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          {% for card in drama %}
          <div class="p-6 rounded-xl shadow-sm border relative overflow-hidden"
               style="background:{{ card.bg }}; border-color:{{ card.border }};">
            <div class="absolute top-0 right-0 w-16 h-16 rounded-bl-full -mr-8 -mt-8"
                 style="background:{{ 'rgba(200,16,46,0.12)' if card.hot else '#f3f4f6' }};"></div>
            <span class="text-xs font-bold uppercase tracking-wider mb-2 block {% if card.hot %}animate-pulse{% endif %}"
                  style="color:{{ card.label_color }};">{{ card.label }}</span>
            <blockquote class="text-lg mb-4"
                        style="font-style:italic; color:#0f172a; {% if card.hot %}font-weight:700;font-style:normal;{% endif %}">
              {{ card.quote }}
            </blockquote>
            <p class="text-sm text-gray-600">{{ card.note | safe }}</p>
          </div>
          {% endfor %}

          <!-- Gravenberch -->
          <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 md:col-span-2">
            <div class="flex flex-col sm:flex-row items-center gap-4">
              <div class="text-4xl">🗣️</div>
              <div>
                <span class="text-xs font-bold text-gray-500 uppercase tracking-wider block">
                  ไรอัน กราเฟนแบร์ก ตัดพ้อแฟนบอล
                </span>
                <p class="text-gray-800 font-semibold mt-1">
                  "พวกเราไม่สมควรได้รับมัน (เสียงโห่)"
                </p>
                <p class="text-sm text-gray-500 mt-1">
                  ผู้ทำประตูขึ้นนำออกมาปกป้องทีม หลังจากแฟนบอลในแอนฟิลด์ส่งเสียงโห่
                  หลังจบเกมและจังหวะเปลี่ยนตัว
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Romano Box -->
        <div class="p-6 rounded-xl shadow-md mt-6 flex items-start gap-4"
             style="background:#1e293b;">
          <div class="text-3xl">📰</div>
          <div>
            <h4 class="font-bold mb-1" style="color:#F6EB61;">Fabrizio Romano Update</h4>
            <p class="text-sm" style="color:#cbd5e1;">
              บอร์ดบริหารลิเวอร์พูลยังคง
              <strong style="color:#ffffff;">"หนุนหลัง"</strong>
              อาร์เน่อ สล็อต อย่างเต็มที่ ข่าวลือเรื่องการติดต่อ ชาบี อลอนโซ่
              ไม่เป็นความจริง สล็อตยังได้ไปต่อ!
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ─────────────────────────────────────
       SECTION 2 : เจาะสถิติ
  ───────────────────────────────────── -->
  <section id="match-stats" class="section-hidden">
    <div class="mb-8 text-center">
      <h2 class="text-4xl font-bold text-gray-900 mb-4 uppercase tracking-tight">
        เจาะสถิติ ฟ้องด้วยตัวเลข
      </h2>
      <p class="text-xl text-gray-600 max-w-3xl mx-auto">
        สถิติจากเกมนี้บอกอะไรเรา? ลิเวอร์พูลถอยไปรับจริง
        หรือแค่เจาะเชลซีไม่เข้า มาดูตัวเลขเปรียบเทียบกัน
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">

      <!-- Radar Chart -->
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 class="text-xl font-bold mb-4 text-center text-gray-900">สถิติภาพรวมเกมรุกและรับ</h3>
        <div id="radarChart" style="width:100%;height:380px;"></div>
      </div>

      <!-- Quick Stats + Spotlight -->
      <div class="space-y-6">
        <div class="grid grid-cols-2 gap-4">
          <div class="stat-card bg-red-50 p-4 rounded-xl border border-red-100 text-center">
            <span class="block text-3xl font-black mb-1" style="color:#b91c1c;">11</span>
            <span class="text-xs font-bold text-gray-600 uppercase tracking-wider">โอกาสยิง (ลิเวอร์พูล)</span>
          </div>
          <div class="stat-card bg-blue-50 p-4 rounded-xl border border-blue-100 text-center">
            <span class="block text-3xl font-black mb-1" style="color:#1d4ed8;">14</span>
            <span class="text-xs font-bold text-gray-600 uppercase tracking-wider">โอกาสยิง (เชลซี)</span>
          </div>
          <div class="stat-card bg-gray-50 p-4 rounded-xl border border-gray-200 text-center col-span-2">
            <span class="block text-2xl font-black text-gray-800 mb-1">2 ครั้ง</span>
            <span class="text-xs font-bold text-gray-600 uppercase tracking-wider">
              ยิงชนเสา/คาน (โซบอสซ์ไล, ฟาน ไดจ์ค)
            </span>
          </div>
        </div>

        <!-- Player Spotlight -->
        <div class="bg-white p-6 rounded-xl shadow-sm border-2" style="border-color:#F6EB61;">
          <h3 class="text-lg font-bold mb-4 flex items-center gap-2 text-gray-900">
            🌟 Spotlight: {{ spotlight.name }} ({{ spotlight.age }} ปี)
          </h3>
          <p class="text-gray-700 text-sm mb-4">
            ดาวรุ่งที่โชว์ฟอร์มได้โดดเด่นที่สุดในแนวรุก ก่อนถูกเปลี่ยนตัวออกจนเกิดเสียงโห่
          </p>
          <div class="space-y-3">
            <div class="flex justify-between items-end">
              <span class="text-sm font-semibold text-gray-600">เลี้ยงผ่านคู่แข่ง (สูงสุดในทีม)</span>
              <span class="font-bold text-lg text-gray-900">{{ spotlight.dribbles }}</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width:{{ spotlight.dribble_pct }}%;"></div>
            </div>
            <div class="flex justify-between items-end mt-4">
              <span class="text-sm font-semibold text-gray-600">แอสซิสต์</span>
              <span class="font-bold text-lg text-gray-900">{{ spotlight.assists }}</span>
            </div>
          </div>
          <p class="text-xs text-gray-500 mt-4 italic">{{ spotlight.note }}</p>
        </div>
      </div>
    </div>

    <!-- Momentum Chart (Plotly) -->
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 class="text-xl font-bold mb-2 text-center text-gray-900">โมเมนตัมการบุก (จำลอง)</h3>
      <p class="text-sm text-center text-gray-500 mb-4">
        กราฟแสดงความกดดันในแต่ละช่วงเวลา (บวก = หงส์บุก, ลบ = สิงห์บุก)
      </p>
      <div id="momentumChart" style="width:100%;height:300px;"></div>
    </div>
  </section>

  <!-- ─────────────────────────────────────
       SECTION 3 : วิเคราะห์สไตล์โต๊ะรก
  ───────────────────────────────────── -->
  <section id="analysis" class="section-hidden">
    <div class="mb-8 text-center">
      <h2 class="text-4xl font-bold text-gray-900 mb-4 uppercase tracking-tight">โต๊ะรก วิจารณ์</h2>
      <p class="text-xl text-gray-600 max-w-3xl mx-auto">
        ถึงเวลาตบขมับ! วิเคราะห์เจาะลึกแบบไม่เกรงใจใคร สไตล์ เจมส์ป๊อก LFC
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">

      <!-- Editor's Take -->
      <div class="bg-white p-8 rounded-xl shadow-sm border-t-4 border-lfc-red">
        <h3 class="text-2xl font-black mb-4 text-gray-900">ถอด อึงูโมฮา... แทคติก หรือ พลาด?</h3>
        <p class="text-gray-700 leading-relaxed mb-4">
          เกมนี้ของกำลังมาแท้ๆ ไอ้หนู ริโอ เลื้อยจนแนวรับเชลซีหัวหมุน
          แต่สล็อตดันเลือกถอดออกนาที 67 แล้วส่ง อิซัค ลงมาแทน!
          เข้าใจว่าอ้างเรื่องตะคริว แต่พอเปลี่ยนปุ๊บ เกมรุกฝั่งซ้ายบอดสนิททันที
          กลายเป็นว่าเราเสียโมเมนตัมไปดื้อๆ
        </p>
        <p class="text-gray-700 leading-relaxed font-semibold">
          "การสัมภาษณ์หลังเกมที่สล็อตตอบแบบประชดนักข่าว ยิ่งทำให้เห็นว่าเขากำลังกดดัน
          และไม่พร้อมรับเสียงวิจารณ์ นี่แหละที่ทำให้เก้าอี้เริ่มร้อน!"
        </p>
      </div>

      <!-- Right Column -->
      <div class="flex flex-col justify-between gap-6">

        <!-- Rival Comparison -->
        <div class="p-8 rounded-xl shadow-lg"
             style="background:linear-gradient(135deg,#7f1d1d,#000);">
          <h3 class="text-xl font-bold mb-4" style="color:#F6EB61;">เปรียบเทียบคู่แค้น</h3>
          <p class="mb-4" style="color:#e2e8f0;">
            แมนฯ ยูไนเต็ด เพิ่งเอาชนะเราไป 3-2 เมื่อเร็วๆ นี้... ลองมองภาพรวมตอนนี้
          </p>
          <div class="flex justify-between items-center text-center">
            <div>
              <span class="block text-2xl font-black text-white">LIV</span>
              <span class="text-sm" style="color:#fca5a5;">ทรงบอลอึดอัด โค้ชมีปัญหากับแฟน</span>
            </div>
            <div class="text-xl font-bold text-gray-300">VS</div>
            <div>
              <span class="block text-2xl font-black" style="color:#ef4444;">MUN</span>
              <span class="text-sm text-gray-400">ชนะบิ๊กแมตช์ โมเมนตัมกำลังมา?</span>
            </div>
          </div>
        </div>

        <!-- Interactive Comment Section (Fetch API → Flask) -->
        <div class="bg-gray-50 p-6 rounded-xl border border-gray-200">
          <h4 class="font-bold text-gray-900 mb-4">เพื่อนๆ คิดยังไง? (จำลองคอมเมนต์)</h4>

          <div class="flex gap-2 mb-4">
            <button onclick="postComment('agree')"
              class="bg-lfc-red hover:bg-red-800 text-white px-4 py-2 rounded text-sm
                     font-bold transition-colors">
              ไล่สล็อตออก!
            </button>
            <button onclick="postComment('disagree')"
              class="text-white px-4 py-2 rounded text-sm font-bold transition-colors
                     hover:bg-black"
              style="background:#1f2937;">
              ให้โอกาสไปก่อน
            </button>
          </div>

          <div id="comments-list" class="space-y-3">
            {% for c in comments %}
            <div class="bg-white p-3 rounded shadow-sm text-sm
                        {% if c.border %}border-l-2 border-lfc-red{% endif %}">
              <span class="font-bold" style="color:{{ c.user_color }};">{{ c.user }}:</span>
              <span class="text-gray-700"> {{ c.text }}</span>
            </div>
            {% endfor %}
          </div>
        </div>

      </div>
    </div>
  </section>

</main>

<!-- FOOTER -->
<footer class="py-6 text-center" style="background:#111827;">
  <p class="font-bold mb-2 text-white">เจมส์ป๊อก LFC</p>
  <p class="text-sm" style="color:#9ca3af;">
    ข้อมูลอ้างอิง: Paul Gorst (Tier 1), NBC Sports, Chelsea FC Official
  </p>
  <p class="text-xs mt-2" style="color:#6b7280;">
    &copy; 2026 เจมส์ป๊อก LFC Dashboard &mdash; Powered by Python 🐍 Flask + Plotly
  </p>
</footer>

<!-- ═══════════════════════════════════════
     JAVASCRIPT
═══════════════════════════════════════ -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
/* ── Tab switching ── */
function switchTab(tabId) {
  ['hot-topics','match-stats','analysis'].forEach(id => {
    const el = document.getElementById(id);
    el.classList.remove('section-active');
    el.classList.add('section-hidden');
  });
  document.getElementById(tabId).classList.replace('section-hidden','section-active');

  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.remove('border-white');
    btn.classList.add('border-transparent');
  });
  document.getElementById('nav-'+tabId).classList.replace('border-transparent','border-white');

  if (tabId === 'match-stats' && !window._chartsRendered) {
    renderCharts();
    window._chartsRendered = true;
  }
}

/* ── Chart render (Plotly or Chart.js) ── */
const RADAR_CFG    = {{ radar_cfg | safe }};
const MOMENTUM_CFG = {{ momentum_cfg | safe }};

function renderCharts() {
  renderChart('radarChart',    RADAR_CFG);
  renderChart('momentumChart', MOMENTUM_CFG);
}

function renderChart(containerId, cfg) {
  if (cfg.engine === 'plotly') {
    const parsed = JSON.parse(cfg.json);
    Plotly.newPlot(containerId, parsed.data, parsed.layout,
                   {responsive: true, displayModeBar: false});
  } else {
    // Chart.js fallback
    const canvas = document.createElement('canvas');
    document.getElementById(containerId).appendChild(canvas);

    // Momentum: colour points dynamically
    if (containerId === 'momentumChart') {
      cfg.data.datasets[0].pointBackgroundColor = cfg.data.datasets[0].data.map(
        (_, i) => [0,2,5].includes(i) ? '#C8102E' : '#1e293b'
      );
    }
    new Chart(canvas.getContext('2d'), {
      type: cfg.type,
      data: cfg.data,
      options: cfg.options,
    });
  }
}

/* ── Comment via Fetch → Flask API ── */
async function postComment(type) {
  const res  = await fetch('/api/comment', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({type})
  });
  const data = await res.json();
  const list = document.getElementById('comments-list');
  const div  = document.createElement('div');
  div.className = 'bg-white p-3 rounded shadow-sm text-sm animate-pulse';
  div.innerHTML = `<span class="font-bold" style="color:#1e293b;">${data.user}:</span>
                   <span class="text-gray-700"> ${data.text}</span>`;
  list.insertBefore(div, list.firstChild);
  setTimeout(() => div.classList.remove('animate-pulse'), 1000);
}
</script>
</body>
</html>
"""


# ============================================================
# FLASK ROUTES
# ============================================================

@app.route("/")
def index():
    radar_fig    = build_radar_chart()
    momentum_fig = build_momentum_chart()
    return render_template_string(
        HTML_TEMPLATE,
        timeline      = TIMELINE_EVENTS,
        drama         = DRAMA_CARDS,
        spotlight     = PLAYER_SPOTLIGHT,
        comments      = INITIAL_COMMENTS,
        radar_cfg     = json.dumps(radar_fig),
        momentum_cfg  = json.dumps(momentum_fig),
    )


@app.route("/api/comment", methods=["POST"])
def add_comment():
    """API endpoint รับ POST แล้วคืน comment object"""
    data = request.get_json()
    ctype = data.get("type", "agree")
    name  = f"Fan_{random.randint(1, 999)}"
    if ctype == "agree":
        text = "เห็นด้วยกับพี่เจมส์ป๊อก สล็อตดื้อเกินไป ไม่ยอมรับผิด!"
    else:
        text = "ผมว่าใจเย็นๆ ขุมกำลังเราเจ็บเยอะ สล็อตทำได้เท่านี้ก็โอเคแล้ว"
    comment = {"user": name, "text": text}
    comment_store.insert(0, comment)
    return jsonify(comment)


@app.route("/api/stats")
def get_stats():
    """API endpoint คืน match stats เป็น JSON"""
    return jsonify({
        "match": MATCH_DATA,
        "radar": STATS_RADAR,
        "momentum": MOMENTUM_DATA,
        "spotlight": PLAYER_SPOTLIGHT,
    })


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print("  🔴 เจมส์ป๊อก LFC Dashboard — Python Edition")
    print("  🐍 Flask + Plotly")
    print("  🌐 เปิดเบราว์เซอร์ที่ → http://localhost:5000")
    print("=" * 55)
    app.run(debug=True, host="0.0.0.0", port=5000)
