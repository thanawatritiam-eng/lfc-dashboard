"""
เจมส์ป๊อก LFC Dashboard — Phase 4
✅ Phase 1: UI/UX Streamlit Cloud
✅ Phase 2: JSON Data, Charts, Mobile
✅ Phase 3: Google Sheets Comments
✅ Phase 4: API-Football Real-time (ผล + ตาราง + สถิตินักเตะ)
"""
import json, random, pathlib, datetime, requests, time
import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components
from google.oauth2 import service_account
from googleapiclient.discovery import build

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
# CONSTANTS
# ══════════════════════════════════════════════════
LIVERPOOL_ID  = 40
SEASON        = 2024          # ปรับได้ใน match_data.json
CACHE_TTL_SEC = 3600          # 1 ชั่วโมง (ประหยัด quota)
LIVE_TTL_SEC  = 300           # 5 นาที (วันแข่ง)

# competition IDs ที่ Liverpool เล่น
COMPETITIONS = {
    39:  "Premier League",
    2:   "Champions League",
    45:  "FA Cup",
    48:  "League Cup",
}

# ══════════════════════════════════════════════════
# API-FOOTBALL LAYER  ← Phase 4 (RapidAPI Edition)
# ══════════════════════════════════════════════════
def _api_headers() -> dict:
    return {
        "x-rapidapi-key":  st.secrets["api_football"]["key"],
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
    }

def _get(endpoint: str, params: dict) -> dict | None:
    """raw GET — จัดการ error ให้ครบ"""
    try:
        r = requests.get(
            f"https://api-football-v1.p.rapidapi.com/v3/{endpoint}",
            headers=_api_headers(),
            params=params,
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            if data.get("errors"):
                st.warning(f"⚠️ API error: {data['errors']}")
                return None
            return data
        else:
            st.warning(f"⚠️ HTTP {r.status_code} จาก API")
            return None
    except requests.exceptions.Timeout:
        st.warning("⚠️ API timeout — ลองใหม่อีกครั้ง")
        return None
    except Exception as e:
        st.warning(f"⚠️ API error: {e}")
        return None

# ── Smart Cache (ใช้ st.session_state เก็บ timestamp) ──
def _cache_key(name: str) -> str:
    return f"_cache_{name}"

def _cached(name: str, ttl: int, fetch_fn):
    """ดึงจาก session_state cache ถ้ายังไม่หมดอายุ"""
    key     = _cache_key(name)
    key_ts  = f"{key}_ts"
    now     = time.time()
    if key in st.session_state and (now - st.session_state.get(key_ts, 0)) < ttl:
        return st.session_state[key]
    data = fetch_fn()
    if data is not None:
        st.session_state[key]    = data
        st.session_state[key_ts] = now
    return st.session_state.get(key)

# ── ฟังก์ชันตัวช่วยแปลงข้อมูล (Helper Functions) สำหรับจัดหน้าผลบอล ──
def fmt_date(iso_str: str) -> str:
    """แปลงเวลาสากล ISO เป็นวันเวลาไทยอ่านง่าย"""
    try:
        dt = datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        # ปรับเพิ่มเวลาเข้าสู่โซนเวลาไทย (+7 ชั่วโมง)
        dt_th = dt.astimezone(datetime.timezone(datetime.timedelta(hours=7)))
        return dt_th.strftime("%d/%m/%Y %H:%M น.")
    except:
        return iso_str[:16]

def result_badge(home_goals: int, away_goals: int, home_id: int) -> tuple[str, str]:
    """คำนวณว่า ลิเวอร์พูล ชนะ(W) เสมอ(D) หรือ แพ้(L) เพื่อส่งกลับตัวอักษรและสีป้ายแสดงผล"""
    if home_goals == away_goals:
        return "D", "#ca8a04" # เสมอ - สีส้มทอง
        
    is_lfc_home = (home_id == LIVERPOOL_ID)
    if home_goals > away_goals:
        return ("W", "#16a34a") if is_lfc_home else ("L", "#C8102E")
    else:
        return ("L", "#C8102E") if is_lfc_home else ("W", "#16a34a")

# ── Optimized Fetch Functions (ลดการยิง API ป้องกัน HTTP 429) ──

def fetch_all_fixtures_data() -> list:
    """ดึงข้อมูลแมตช์ทั้งหมดของฤดูกาลในครั้งเดียว เพื่อลดจำนวน Request"""
    def _fetch():
        data = _get("fixtures", {
            "team": LIVERPOOL_ID,
            "season": SEASON
        })
        if data and data.get("response"):
            return data["response"]
        return []
    return _cached("all_fixtures_all", CACHE_TTL_SEC, _fetch) or []

def fetch_last_fixtures(n: int = 5) -> list:
    """กรองผลการแข่งขันล่าสุด n แมตช์จากข้อมูลรวมด้วย Python (ไม่ต้องยิง API เพิ่ม)"""
    all_fix = fetch_all_fixtures_data()
    if not all_fix:
        return []
    # กรองเฉพาะแมตช์ที่แข่งจบไปแล้ว
    past_fixtures = [f for f in all_fix if f["fixture"]["status"]["short"] in ["FT", "AET", "PEN"]]
    # เรียงจากวันที่ล่าสุดไปอดีต
    past_fixtures.sort(key=lambda f: f["fixture"]["date"], reverse=True)
    return past_fixtures[:n]

def fetch_next_fixture() -> dict | None:
    """กรองหาแมตช์ถัดไปจากข้อมูลรวมด้วย Python (ไม่ต้องยิง API เพิ่ม)"""
    all_fix = fetch_all_fixtures_data()
    if not all_fix:
        return None
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # กรองเฉพาะแมตช์ในอนาคตที่ยังมาไม่ถึง
    upcoming = [f for f in all_fix if f["fixture"]["date"] > now_str]
    if upcoming:
        upcoming.sort(key=lambda f: f["fixture"]["date"])
        return upcoming[0]
    return None

def fetch_live_fixture() -> dict | None:
    """แมตช์ที่กำลังแข่งสด (ยิงแยก 1 ครั้งเฉพาะวันที่มีแข่งจริง)"""
    def _fetch():
        data = _get("fixtures", {
            "team": LIVERPOOL_ID,
            "live": "all"
        })
        if data and data.get("response"):
            return data["response"][0]
        return None
    return _cached("live", LIVE_TTL_SEC, _fetch)

def fetch_standings() -> dict:
    """ดึงตารางคะแนน (ปรับดึงเฉพาะพรีเมียร์ลีกหลัก เพื่อประหยัดโควตาไม่ให้ติด 429)"""
    def _fetch():
        out = {}
        # ดึงเฉพาะ Premier League (ID: 39) เพื่อตัดลูปยิง API ซ้ำซ้อนสำหรับลีกอื่นที่รูปแบบไม่ตรงกัน
        data = _get("standings", {"league": 39, "season": SEASON})
        if data and data.get("response"):
            out["Premier League"] = data["response"][0]["league"]["standings"][0]
        return out
    return _cached("standings", CACHE_TTL_SEC, _fetch) or {}

def fetch_player_stats(league_id: int = 39) -> list:
    """สถิตินักเตะ Liverpool ในลีกล่าสุด (ยิง 1 ครั้ง)"""
    def _fetch():
        data = _get("players", {
            "team":   LIVERPOOL_ID,
            "league": league_id,
            "season": SEASON,
            "page":   1,
        })
        if data:
            players = data.get("response", [])
            players.sort(
                key=lambda p: (
                    p["statistics"][0]["goals"]["total"] or 0,
                    p["statistics"][0]["goals"]["assists"] or 0,
                ),
                reverse=True,
            )
            return players[:8]
        return []
    return _cached("players", CACHE_TTL_SEC, _fetch) or []
# ══════════════════════════════════════════════════
# GOOGLE SHEETS — Phase 3
# ══════════════════════════════════════════════════
SHEET_TAB = "Sheet1"
SCOPES    = ["https://www.googleapis.com/auth/spreadsheets"]

@st.cache_resource
def get_sheets_service():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES)
    return build("sheets", "v4", credentials=creds).spreadsheets()

def get_sheet_id() -> str:
    return st.secrets["gsheets"]["spreadsheet_id"]

def fetch_comments() -> list:
    try:
        res  = get_sheets_service().values().get(
            spreadsheetId=get_sheet_id(),
            range=f"{SHEET_TAB}!A2:D",
        ).execute()
        rows = res.get("values", [])
        out  = []
        for r in reversed(rows):
            if len(r) >= 3:
                out.append({
                    "timestamp":  r[0] if len(r) > 0 else "",
                    "user":       r[1] if len(r) > 1 else "Fan",
                    "text":       r[2] if len(r) > 2 else "",
                    "user_color": "#1e293b",
                    "border":     (r[3].lower() == "true") if len(r) > 3 else False,
                })
        return out
    except Exception as e:
        st.warning(f"⚠️ โหลดคอมเมนต์ไม่ได้: {e}")
        return []

def push_comment(user: str, text: str, border: bool = False) -> bool:
    try:
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        get_sheets_service().values().append(
            spreadsheetId=get_sheet_id(),
            range=f"{SHEET_TAB}!A:D",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [[ts, user, text, str(border)]]},
        ).execute()
        return True
    except Exception as e:
        st.error(f"❌ บันทึกไม่สำเร็จ: {e}")
        return False

# ══════════════════════════════════════════════════
# LOAD MATCH DATA JSON — Phase 2
# ══════════════════════════════════════════════════
@st.cache_data
def load_match():
    p = pathlib.Path(__file__).parent / "match_data.json"
    with open(p, encoding="utf-8") as f:
        return json.load(f)

D      = load_match()
META   = D["meta"]
TL     = D["timeline"]
QUOTES = D["quotes"]
GRAV   = D["gravenberch"]
ROM    = D["romano"]
STATS  = D["stats"]
SPOT   = D["spotlight"]
ANA    = D["analysis"]
RIV    = D["rival_compare"]

AGREE_TEXT    = "เห็นด้วยกับพี่เจมส์ป๊อก สล็อตดื้อเกินไป ไม่ยอมรับผิด!"
DISAGREE_TEXT = "ผมว่าใจเย็นๆ ขุมกำลังเราเจ็บเยอะ สล็อตทำได้เท่านี้ก็โอเคแล้ว"

# ══════════════════════════════════════════════════
# CSS
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
  .lfc-header { background:#C8102E;padding:14px 24px;border-radius:12px;
    display:flex;align-items:center;gap:12px;
    box-shadow:0 4px 12px rgba(200,16,46,.35);margin-bottom:20px; }
  .lfc-logo { width:44px;height:44px;background:#fff;border-radius:50%;
    border:2px solid #F6EB61;display:flex;align-items:center;justify-content:center;
    font-weight:900;font-size:16px;color:#C8102E;flex-shrink:0; }
  .lfc-title { color:#fff;font-size:19px;font-weight:800;
    text-transform:uppercase;letter-spacing:.06em;line-height:1.2; }
  .lfc-sub { color:#F6EB61;font-size:10px;font-weight:600;
    text-transform:uppercase;letter-spacing:.12em; }
  .badge { font-size:10px;font-weight:700;padding:2px 8px;border-radius:9999px;
    margin-left:6px;vertical-align:middle; }
  .badge-green { background:linear-gradient(135deg,#16a34a,#15803d);color:#fff !important; }
  .badge-orange { background:linear-gradient(135deg,#ea580c,#c2410c);color:#fff !important; }
  .badge-live { background:#C8102E;color:#fff !important;animation:pulse 1.5s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.6} }

  /* Cards */
  .card { background:#fff;border-radius:14px;padding:20px;
    border:1px solid #e5e7eb;box-shadow:0 1px 5px rgba(0,0,0,.07);
    margin-bottom:14px;color:#1e293b; }
  .card-red-border  { border:1.5px solid #C8102E !important;background:#fef2f2 !important; }
  .card-gold-border { border:2px solid #F6EB61 !important; }
  .card-dark { background:#1e293b !important;border-color:#334155 !important; }

  /* Live score banner */
  .live-banner { background:linear-gradient(135deg,#C8102E,#991b1b);
    border-radius:14px;padding:18px 24px;color:#fff;margin-bottom:16px;
    display:flex;align-items:center;justify-content:space-between;
    box-shadow:0 4px 12px rgba(200,16,46,.3); }
  .live-dot { width:10px;height:10px;background:#4ade80;border-radius:50%;
    display:inline-block;margin-right:6px;animation:pulse 1.5s infinite; }
  .live-score { font-size:36px;font-weight:900;letter-spacing:.05em; }
  .live-teams { font-size:13px;opacity:.85; }
  .live-min   { font-size:28px;font-weight:800;color:#F6EB61; }

  /* Fixture card */
  .fix-card { background:#fff;border-radius:10px;padding:12px 16px;
    border:1px solid #e5e7eb;margin-bottom:8px;
    display:flex;align-items:center;justify-content:space-between; }
  .fix-teams { font-weight:600;font-size:14px;color:#1e293b; }
  .fix-score { font-weight:900;font-size:18px;color:#0f172a;text-align:center;min-width:50px; }
  .fix-comp  { font-size:11px;color:#64748b; }
  .fix-date  { font-size:11px;color:#94a3b8;text-align:right; }
  .wdl-badge { font-size:11px;font-weight:800;padding:2px 7px;border-radius:6px;color:#fff; }

  /* Standing table */
  .stand-table { width:100%;border-collapse:collapse;font-size:13px; }
  .stand-table th { color:#475569;font-weight:600;font-size:11px;
    text-transform:uppercase;letter-spacing:.05em;
    padding:6px 8px;border-bottom:1px solid #e5e7eb;text-align:center; }
  .stand-table td { padding:7px 8px;border-bottom:1px solid #f1f5f9;
    color:#374151;text-align:center; }
  .stand-table td:first-child { text-align:left;font-weight:600;color:#1e293b; }
  .stand-table tr.highlight-lfc td { background:#fef2f2;font-weight:800;color:#b91c1c; }
  .stand-table tr:hover td { background:#f8fafc; }

  /* Player stats */
  .player-row { display:flex;align-items:center;padding:10px 0;
    border-bottom:1px solid #f1f5f9;gap:10px; }
  .player-num  { width:22px;font-size:12px;font-weight:700;color:#94a3b8;text-align:center; }
  .player-name { flex:1;font-weight:600;font-size:14px;color:#1e293b; }
  .player-pos  { font-size:11px;color:#64748b;margin-left:4px; }
  .player-stat { text-align:center;min-width:36px; }
  .player-stat-val  { font-size:16px;font-weight:900;color:#C8102E; }
  .player-stat-lbl  { font-size:10px;color:#94a3b8; }

  /* Next match */
  .next-match { background:linear-gradient(135deg,#1e293b,#0f172a);
    border-radius:14px;padding:20px;color:#fff;margin-bottom:14px; }
  .next-label  { color:#F6EB61;font-size:11px;font-weight:700;
    text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px; }
  .next-teams  { font-size:22px;font-weight:800;margin-bottom:6px; }
  .next-detail { color:#94a3b8;font-size:13px; }

  /* Scoreboard (manual match) */
  .scoreboard { background:#f1f5f9;border-radius:12px;padding:16px;
    display:flex;justify-content:space-around;align-items:center;
    text-align:center;margin-bottom:18px; }
  .score-team-liv { color:#b91c1c;font-weight:800;font-size:17px; }
  .score-team-che { color:#1d4ed8;font-weight:800;font-size:17px; }
  .score-num { color:#0f172a;font-weight:900;font-size:42px;line-height:1; }
  .score-vs  { color:#64748b;font-weight:700;font-size:22px; }

  /* Timeline */
  .tl-row { display:flex;margin-bottom:12px; }
  .tl-min { width:40px;flex-shrink:0;color:#475569;font-weight:700;font-size:12px;padding-top:3px; }
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
  .quote-text { font-size:15px;font-style:italic;color:#1e293b;margin-bottom:10px;line-height:1.6; }
  .quote-bold { font-size:18px;font-weight:800;color:#0f172a;margin-bottom:10px; }
  .quote-note { font-size:13px;color:#4b5563;line-height:1.5; }

  .romano-box { background:#1e293b;border-radius:14px;padding:20px;
    display:flex;align-items:flex-start;gap:12px;margin-top:12px; }
  .romano-title { color:#F6EB61;font-weight:700;margin-bottom:4px;font-size:14px; }
  .romano-text  { color:#cbd5e1;font-size:13px;line-height:1.6; }
  .romano-text strong { color:#fff; }

  .grav-card { background:#fff;border-radius:14px;padding:16px;
    border:1px solid #e5e7eb;display:flex;gap:12px;align-items:flex-start;margin-top:10px; }
  .grav-icon { font-size:30px;flex-shrink:0; }
  .grav-label { color:#475569;font-size:11px;font-weight:700;
    text-transform:uppercase;letter-spacing:.08em; }
  .grav-quote { color:#1e293b;font-weight:600;font-size:14px;margin:4px 0; }
  .grav-desc  { color:#475569;font-size:13px;line-height:1.5; }

  /* Headings */
  .drama-heading { color:#0f172a;font-size:19px;font-weight:800;
    border-left:4px solid #C8102E;padding-left:12px;margin-bottom:14px; }
  .sec-heading { color:#0f172a;font-size:24px;font-weight:800;
    text-transform:uppercase;text-align:center;margin-bottom:6px; }
  .sec-sub { color:#475569;font-size:14px;text-align:center;
    max-width:660px;margin:0 auto 22px;line-height:1.6; }
  .subsec-heading { color:#0f172a;font-size:16px;font-weight:800;
    border-bottom:2px solid #C8102E;padding-bottom:6px;
    margin-bottom:14px;display:inline-block; }

  /* Stat cards */
  .stat-card-red  { background:#fef2f2;border:1px solid #fecaca;border-radius:12px;padding:14px;text-align:center; }
  .stat-card-blue { background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;padding:14px;text-align:center; }
  .stat-card-gray { background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:14px;text-align:center;margin-top:10px; }
  .stat-num-red   { color:#b91c1c;font-size:36px;font-weight:900; }
  .stat-num-blue  { color:#1d4ed8;font-size:36px;font-weight:900; }
  .stat-num-gray  { color:#0f172a;font-size:26px;font-weight:900; }
  .stat-label     { color:#374151;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-top:3px; }

  /* Compare */
  .compare-box { background:linear-gradient(135deg,#7f1d1d,#000);
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
  .comment-box   { background:#f1f5f9;border:1px solid #e2e8f0;border-radius:14px;padding:16px; }
  .comment-title { color:#0f172a;font-weight:700;margin-bottom:10px;font-size:14px; }
  .comment-item  { background:#fff;border-radius:8px;padding:9px 13px;
    margin-bottom:7px;box-shadow:0 1px 3px rgba(0,0,0,.06);font-size:13px;color:#374151;line-height:1.5; }
  .comment-item-red { border-left:3px solid #C8102E; }
  .comment-ts { font-size:10px;color:#94a3b8;float:right;margin-top:2px; }
  .sheets-badge { display:inline-flex;align-items:center;gap:5px;
    background:#e8f5e9;border:1px solid #a5d6a7;border-radius:8px;
    padding:4px 10px;font-size:11px;font-weight:700;color:#2e7d32;margin-bottom:10px; }

  /* Editor */
  .editor-card  { background:#fff;border-radius:14px;padding:26px;
    border-top:4px solid #C8102E;box-shadow:0 1px 5px rgba(0,0,0,.07); }
  .editor-title { color:#0f172a;font-size:19px;font-weight:900;margin-bottom:10px; }
  .editor-body  { color:#374151;line-height:1.8;margin-bottom:10px;font-size:14px; }
  .editor-quote { color:#1e293b;font-weight:600;line-height:1.8;font-size:14px; }

  /* Footer */
  .lfc-footer { background:#111827;padding:20px;text-align:center;border-radius:14px;margin-top:32px; }
  .footer-title { color:#fff;font-weight:700;font-size:15px;margin-bottom:4px; }
  .footer-ref   { color:#9ca3af;font-size:12px;margin-bottom:3px; }
  .footer-copy  { color:#6b7280;font-size:11px; }

  @media (max-width:768px) {
    .lfc-title { font-size:15px; }
    .sec-heading { font-size:18px; }
    .score-num { font-size:32px; }
    .card { padding:14px; }
    .live-score { font-size:26px; }
  }
`;
const s = window.parent.document.createElement('style');
s.textContent = css;
window.parent.document.head.appendChild(s);
</script>
""", height=0, scrolling=False)

# ══════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════
if "tab" not in st.session_state:
    st.session_state.tab = "live"    # Phase 4 default tab = Live
if "comments" not in st.session_state:
    st.session_state.comments = fetch_comments()

# ── helpers ──
def render_comment(c: dict) -> str:
    color  = c.get("user_color", "#1e293b")
    user   = c.get("user", "Fan")
    text   = c.get("text", "")
    ts     = c.get("timestamp", "")[:10]
    border = "comment-item-red" if c.get("border") else ""
    ts_html = f'<span class="comment-ts">{ts}</span>' if ts else ""
    return (f'<div class="comment-item {border}">'
            f'<span style="color:{color};font-weight:700;">{user}:</span> {text}'
            f'{ts_html}</div>')

def tl_cls(t: str):
    return {"goal_liv": ("tl-title-red","red"),
            "goal_che": ("tl-title-blue","blue")}.get(t, ("tl-title-gray",""))

# ══════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════
live_fix = fetch_live_fixture()
live_label = (
    '<span class="badge badge-live">🔴 LIVE</span>'
    if live_fix else
    '<span class="badge badge-green">Phase 4 🔗 API</span>'
)
st.markdown(
    f'<div class="lfc-header">'
    f'<div class="lfc-logo">JP</div>'
    f'<div>'
    f'<div class="lfc-title">เจมส์ป๊อก LFC {live_label}</div>'
    f'<div class="lfc-sub">ขยี้ทุกประเด็นหงส์แดง • {META["competition"]} MW{META["matchweek"]}</div>'
    f'</div></div>',
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════
# TAB NAV  (Phase 4 เพิ่ม Live & Stats tabs)
# ══════════════════════════════════════════════════
tabs = st.columns([1.6, 1.8, 1.4, 1.8, 2.1])
tab_defs = [
    ("live",     "📡 Live & ผล"),
    ("standing", "🏆 ตารางคะแนน"),
    ("stats",    "📊 สถิติ"),
    ("players",  "👟 นักเตะ"),
    ("analysis", "🗒️ วิเคราะห์โต๊ะรก"),
]
for col, (tid, label) in zip(tabs, tab_defs):
    with col:
        if st.button(label, use_container_width=True, key=f"btn_{tid}",
                     type="primary" if st.session_state.tab == tid else "secondary"):
            st.session_state.tab = tid; st.rerun()

st.markdown("<hr style='border:none;border-top:1px solid #e5e7eb;margin:10px 0 20px;'>",
            unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB: LIVE & ผลล่าสุด  ← Phase 4 ใหม่
# ══════════════════════════════════════════════════════════════
if st.session_state.tab == "live":
    st.markdown('<p class="sec-heading">📡 Live & ผลล่าสุด</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">ข้อมูลจาก API-Football อัปเดตทุก 1 ชั่วโมง (วันแข่งทุก 5 นาที)</p>', unsafe_allow_html=True)

    col_live, col_next = st.columns([3, 2], gap="large")

    with col_live:
        # ── LIVE MATCH BANNER ──
        if live_fix:
            f  = live_fix["fixture"]
            g  = live_fix["goals"]
            ht = live_fix["teams"]["home"]
            at = live_fix["teams"]["away"]
            elapsed = f["status"].get("elapsed", "?")
            st.markdown(
                f'<div class="live-banner">'
                f'<div>'
                f'<div><span class="live-dot"></span><b>LIVE — {elapsed}\'</b></div>'
                f'<div class="live-teams">{ht["name"]} vs {at["name"]}</div>'
                f'<div style="font-size:11px;opacity:.7;">{f.get("venue",{}).get("name","")} • {COMPETITIONS.get(live_fix["league"]["id"],"")}</div>'
                f'</div>'
                f'<div class="live-score">{g["home"]} - {g["away"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            # ── NEXT MATCH ──
            next_fix = fetch_next_fixture()
            if next_fix:
                nf = next_fix["fixture"]
                nh = next_fix["teams"]["home"]["name"]
                na = next_fix["teams"]["away"]["name"]
                nd = fmt_date(nf["date"])
                nv = nf.get("venue", {}).get("name", "")
                nc = COMPETITIONS.get(next_fix["league"]["id"], next_fix["league"]["name"])
                st.markdown(
                    f'<div class="next-match">'
                    f'<div class="next-label">⏰ แมตช์ถัดไป</div>'
                    f'<div class="next-teams">{nh} vs {na}</div>'
                    f'<div class="next-detail">{nd} • {nv}</div>'
                    f'<div class="next-detail" style="margin-top:4px;">{nc}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # ── ผลล่าสุด 5 แมตช์ ──
        st.markdown('<div class="subsec-heading">ผลล่าสุด 5 แมตช์</div>', unsafe_allow_html=True)
        fixtures = fetch_last_fixtures(5)

        if fixtures:
            for fx in fixtures:
                f   = fx["fixture"]
                g   = fx["goals"]
                ht  = fx["teams"]["home"]
                at  = fx["teams"]["away"]
                comp = COMPETITIONS.get(fx["league"]["id"], fx["league"]["name"])
                date = fmt_date(f["date"])
                gh, ga = g.get("home") or 0, g.get("away") or 0
                wdl, wdl_color = result_badge(gh, ga, ht["id"])
                st.markdown(
                    f'<div class="fix-card">'
                    f'<div style="flex:1;">'
                    f'<div class="fix-teams">{ht["name"]} {gh} – {ga} {at["name"]}</div>'
                    f'<div class="fix-comp">{comp}</div>'
                    f'</div>'
                    f'<div style="text-align:right;">'
                    f'<span class="wdl-badge" style="background:{wdl_color};">{wdl}</span>'
                    f'<div class="fix-date">{date[:10]}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("ยังไม่มีข้อมูลผลแมตช์ — กด Refresh ด้านล่าง")

        if st.button("🔄 Refresh ผล", key="refresh_fix"):
            # ต้องย่อหน้า (Tab) ถอยเข้ามาด้านในของบล็อก if ทั้งหมดตามนี้ครับ 👇
            for k in ["_cache_all_fixtures_all", "_cache_all_fixtures_all_ts",
                      "_cache_live", "_cache_live_ts"]:
                st.session_state.pop(k, None)
            st.rerun()

    with col_next:
        # ── สถิติ 5 แมตช์ล่าสุด ──
        st.markdown('<div class="subsec-heading">ฟอร์ม 5 แมตช์ล่าสุด</div>', unsafe_allow_html=True)
        if fixtures:
            w = d = l = gf = ga_count = 0
            form_html = ""
            for fx in fixtures[:5]:
                g   = fx["goals"]
                ht  = fx["teams"]["home"]
                gh, ga = g.get("home") or 0, g.get("away") or 0
                wdl, wdl_color = result_badge(gh, ga, ht["id"])
                if wdl == "W": w += 1
                elif wdl == "D": d += 1
                else: l += 1
                gf += gh if ht["id"] == LIVERPOOL_ID else ga
                ga_count += ga if ht["id"] == LIVERPOOL_ID else gh
                form_html += f'<span class="wdl-badge" style="background:{wdl_color};margin:2px;">{wdl}</span> '

            st.markdown(f'<div class="card"><div style="margin-bottom:12px;">{form_html}</div>', unsafe_allow_html=True)
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                st.markdown(f'<div style="text-align:center;"><div style="font-size:24px;font-weight:900;color:#16a34a;">{w}</div><div style="font-size:11px;color:#475569;">ชนะ</div></div>', unsafe_allow_html=True)
            with fc2:
                st.markdown(f'<div style="text-align:center;"><div style="font-size:24px;font-weight:900;color:#ca8a04;">{d}</div><div style="font-size:11px;color:#475569;">เสมอ</div></div>', unsafe_allow_html=True)
            with fc3:
                st.markdown(f'<div style="text-align:center;"><div style="font-size:24px;font-weight:900;color:#C8102E;">{l}</div><div style="font-size:11px;color:#475569;">แพ้</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="margin-top:10px;font-size:13px;color:#374151;">⚽ ยิง <b>{gf}</b> ประตู · เสีย <b>{ga_count}</b> ประตู</div></div>', unsafe_allow_html=True)

        # ── Cache status ──
        ts = st.session_state.get("_cache_fixtures_ts", 0)
        if ts:
            age_min = int((time.time() - ts) / 60)
            next_min = max(0, 60 - age_min)
            st.markdown(
                f'<div style="background:#f0fdf4;border:1px solid #86efac;border-radius:10px;'
                f'padding:10px 14px;font-size:12px;color:#166534;margin-top:8px;">'
                f'🔄 Cache อายุ {age_min} นาที · จะดึงใหม่ใน {next_min} นาที<br>'
                f'💡 Free plan 100 req/day — cache ช่วยประหยัด quota</div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════
# TAB: ตารางคะแนน  ← Phase 4 ใหม่
# ══════════════════════════════════════════════════════════════
elif st.session_state.tab == "standing":
    st.markdown('<p class="sec-heading">🏆 ตารางคะแนน</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">ตารางล่าสุดจาก API-Football ทุก competition ที่ Liverpool เล่น</p>', unsafe_allow_html=True)

    standings = fetch_standings()

    if standings:
        for comp_name, table in standings.items():
            st.markdown(f'<div class="card"><div class="subsec-heading">{comp_name}</div>', unsafe_allow_html=True)

            # แสดงแค่ 10 อันดับแรก + Liverpool ถ้าอยู่นอก top 10
            lfc_row = next((r for r in table if r["team"]["id"] == LIVERPOOL_ID), None)
            show_rows = table[:10]
            lfc_in_top10 = any(r["team"]["id"] == LIVERPOOL_ID for r in show_rows)

            rows_html = ""
            for r in show_rows:
                is_lfc = r["team"]["id"] == LIVERPOOL_ID
                cls    = "highlight-lfc" if is_lfc else ""
                name   = r["team"]["name"]
                rows_html += (
                    f'<tr class="{cls}">'
                    f'<td>{r["rank"]}. {name}</td>'
                    f'<td>{r["all"]["played"]}</td>'
                    f'<td>{r["all"]["win"]}</td>'
                    f'<td>{r["all"]["draw"]}</td>'
                    f'<td>{r["all"]["lose"]}</td>'
                    f'<td>{r["goalsDiff"]}</td>'
                    f'<td><b>{r["points"]}</b></td>'
                    f'</tr>'
                )

            # แสดง LFC แยกถ้าอยู่นอก top 10
            if not lfc_in_top10 and lfc_row:
                rows_html += (
                    f'<tr><td colspan="7" style="text-align:center;color:#94a3b8;font-size:11px;">...</td></tr>'
                    f'<tr class="highlight-lfc">'
                    f'<td>{lfc_row["rank"]}. {lfc_row["team"]["name"]}</td>'
                    f'<td>{lfc_row["all"]["played"]}</td>'
                    f'<td>{lfc_row["all"]["win"]}</td>'
                    f'<td>{lfc_row["all"]["draw"]}</td>'
                    f'<td>{lfc_row["all"]["lose"]}</td>'
                    f'<td>{lfc_row["goalsDiff"]}</td>'
                    f'<td><b>{lfc_row["points"]}</b></td>'
                    f'</tr>'
                )

            st.markdown(
                f'<table class="stand-table">'
                f'<thead><tr><th>ทีม</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr></thead>'
                f'<tbody>{rows_html}</tbody></table></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("ยังไม่มีข้อมูลตาราง — กด Refresh")

    if st.button("🔄 Refresh ตาราง", key="refresh_stand"):
        for k in ["_cache_standings", "_cache_standings_ts"]:
            st.session_state.pop(k, None)
        st.rerun()


# ══════════════════════════════════════════════════════════════
# TAB: สถิติแมตช์ (จาก match_data.json เดิม)
# ══════════════════════════════════════════════════════════════
elif st.session_state.tab == "stats":
    st.markdown('<p class="sec-heading">เจาะสถิติ ฟ้องด้วยตัวเลข</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">สถิติเจาะลึกแมตช์ล่าสุด Liverpool vs Chelsea</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="card"><p style="font-size:16px;font-weight:800;color:#0f172a;text-align:center;margin-bottom:6px;">สถิติภาพรวมเกมรุกและรับ</p>', unsafe_allow_html=True)
        rl = STATS["radar_labels"] + [STATS["radar_labels"][0]]
        hv = STATS["home_values"]  + [STATS["home_values"][0]]
        av = STATS["away_values"]  + [STATS["away_values"][0]]
        fr = go.Figure()
        fr.add_trace(go.Scatterpolar(r=hv, theta=rl, fill="toself", name=META["home_short"],
            line=dict(color="#C8102E",width=2), fillcolor="rgba(200,16,46,0.15)", marker=dict(color="#C8102E")))
        fr.add_trace(go.Scatterpolar(r=av, theta=rl, fill="toself", name=META["away_short"],
            line=dict(color="#1d4ed8",width=2), fillcolor="rgba(29,78,216,0.15)", marker=dict(color="#1d4ed8")))
        fr.update_layout(
            polar=dict(radialaxis=dict(visible=True,range=[0,100],tickfont=dict(size=10,color="#475569")),
                       angularaxis=dict(tickfont=dict(size=11,color="#1e293b")),bgcolor="#f8fafc"),
            legend=dict(orientation="h",y=-0.18,x=0.5,xanchor="center",font=dict(size=13,color="#1e293b")),
            paper_bgcolor="#ffffff", margin=dict(l=40,r=40,t=20,b=60), height=360)
        st.plotly_chart(fr, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        sm = {"red":('<div class="stat-card-red">','stat-num-red'),
              "blue":('<div class="stat-card-blue">','stat-num-blue'),
              "gray":('<div class="stat-card-gray">','stat-num-gray')}
        qs = STATS["quick"]
        s1, s2 = st.columns(2)
        with s1:
            t,n = sm[qs[0]["style"]]
            st.markdown(f'{t}<div class="{n}">{qs[0]["value"]}</div><div class="stat-label">{qs[0]["label"]}</div></div>', unsafe_allow_html=True)
        with s2:
            t,n = sm[qs[1]["style"]]
            st.markdown(f'{t}<div class="{n}">{qs[1]["value"]}</div><div class="stat-label">{qs[1]["label"]}</div></div>', unsafe_allow_html=True)
        t,n = sm[qs[2]["style"]]
        st.markdown(f'{t}<div class="{n}">{qs[2]["value"]}</div><div class="stat-label">{qs[2]["label"]}</div></div>', unsafe_allow_html=True)

        spot_rows = []
        for s in SPOT["stats"]:
            row = (f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;">'
                   f'<span style="font-size:13px;font-weight:600;color:#374151;">{s["label"]}</span>'
                   f'<span style="font-weight:800;color:#1e293b;">{s["value"]}</span></div>')
            if s["pct"] is not None:
                row += (f'<div style="background:#e5e7eb;border-radius:9999px;height:7px;margin:5px 0 10px;">'
                        f'<div style="background:#C8102E;border-radius:9999px;height:7px;width:{s["pct"]}%;"></div></div>')
            spot_rows.append(row)
        st.markdown(
            f'<div class="card card-gold-border" style="margin-top:12px;">'
            f'<div style="font-size:14px;font-weight:800;color:#1e293b;margin-bottom:7px;">🌟 Spotlight: {SPOT["name"]} ({SPOT["age"]} ปี)</div>'
            f'<div style="color:#374151;font-size:13px;margin-bottom:10px;">ดาวรุ่งที่โชว์ฟอร์มได้โดดเด่นที่สุดในแนวรุก</div>'
            f'{"".join(spot_rows)}'
            f'<div style="font-size:11px;color:#64748b;margin-top:8px;font-style:italic;">{SPOT["note"]}</div></div>',
            unsafe_allow_html=True,
        )

    dc, mc = st.columns([1, 2], gap="large")
    with dc:
        st.markdown('<div class="card"><p style="font-size:16px;font-weight:800;color:#0f172a;text-align:center;margin-bottom:6px;">การครองบอล</p>', unsafe_allow_html=True)
        poss = STATS["possession"]
        fd = go.Figure(go.Pie(
            labels=[META["home_short"], META["away_short"]], values=[poss["home"], poss["away"]],
            hole=0.6, marker=dict(colors=["#C8102E","#1d4ed8"],line=dict(color="#fff",width=3)),
            textinfo="label+percent", textfont=dict(size=14,color="#fff"), insidetextorientation="auto"))
        fd.add_annotation(text=f"<b>{poss['home']}%</b><br><span style='font-size:11px'>LIV</span>",
                          x=0.5, y=0.5, showarrow=False, font=dict(size=16,color="#C8102E"))
        fd.update_layout(showlegend=False, paper_bgcolor="#ffffff", margin=dict(l=10,r=10,t=10,b=10), height=220)
        st.plotly_chart(fd, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    with mc:
        st.markdown('<div class="card"><p style="font-size:16px;font-weight:800;color:#0f172a;text-align:center;margin-bottom:4px;">โมเมนตัมการบุก</p><p style="color:#64748b;font-size:12px;text-align:center;margin-bottom:8px;">บวก = หงส์บุก · ลบ = สิงห์บุก</p>', unsafe_allow_html=True)
        mx   = STATS["momentum_x"]
        my   = STATS["momentum_y"]
        tips = {int(k): v for k, v in STATS["momentum_tips"].items()}
        ptc  = ["#C8102E" if i in tips else "#1e293b" for i in range(len(my))]
        hov  = [tips.get(i, f"โมเมนตัม: {v}") for i, v in enumerate(my)]
        fm = go.Figure()
        fm.add_hrect(y0=0,y1=10,fillcolor="rgba(200,16,46,0.05)",line_width=0)
        fm.add_hrect(y0=-10,y1=0,fillcolor="rgba(29,78,216,0.05)",line_width=0)
        fm.add_trace(go.Scatter(x=mx,y=my,mode="lines+markers",
            line=dict(color="#1e293b",width=3,shape="spline"),fill="tozeroy",
            fillcolor="rgba(30,41,59,0.08)",
            marker=dict(size=9,color=ptc,line=dict(color="#fff",width=2)),
            hovertext=hov,hoverinfo="text"))
        fm.add_hline(y=0,line_color="#0f172a",line_width=1.5)
        fm.add_annotation(x="15",y=5,text="🔴 LFC",showarrow=False,font=dict(color="#C8102E",size=11),yshift=16)
        fm.add_annotation(x="75",y=-8,text="🔵 CHE",showarrow=False,font=dict(color="#1d4ed8",size=11),yshift=-18)
        fm.update_layout(
            xaxis=dict(title="นาที",tickfont=dict(size=11,color="#1e293b"),gridcolor="#e5e7eb"),
            yaxis=dict(range=[-10,10],showticklabels=False,gridcolor="#e5e7eb"),
            paper_bgcolor="#ffffff",plot_bgcolor="#ffffff",
            showlegend=False,margin=dict(l=16,r=16,t=8,b=36),height=220)
        st.plotly_chart(fm, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB: สถิตินักเตะ  ← Phase 4 ใหม่
# ══════════════════════════════════════════════════════════════
elif st.session_state.tab == "players":
    st.markdown('<p class="sec-heading">👟 สถิตินักเตะ Liverpool</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">ข้อมูลจาก API-Football · Premier League Season 2024</p>', unsafe_allow_html=True)

    players = fetch_player_stats(39)  # PL

    if players:
        # ── Bar Chart Goals+Assists ──
        names  = [p["player"]["name"].split(" ")[-1] for p in players]
        goals  = [p["statistics"][0]["goals"]["total"] or 0 for p in players]
        assists= [p["statistics"][0]["goals"]["assists"] or 0 for p in players]

        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(name="Goals",   x=names, y=goals,
            marker_color="#C8102E", text=goals, textposition="outside",
            textfont=dict(size=12,color="#0f172a")))
        fig_p.add_trace(go.Bar(name="Assists", x=names, y=assists,
            marker_color="#F6EB61", text=assists, textposition="outside",
            textfont=dict(size=12,color="#0f172a")))
        fig_p.update_layout(
            barmode="group",
            paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
            legend=dict(orientation="h",y=-0.2,font=dict(color="#1e293b")),
            xaxis=dict(tickfont=dict(size=12,color="#1e293b")),
            yaxis=dict(gridcolor="#e5e7eb",tickfont=dict(color="#475569")),
            margin=dict(l=10,r=10,t=20,b=60), height=320)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(fig_p, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Player Detail List ──
        st.markdown('<div class="card"><div class="subsec-heading">รายละเอียดนักเตะ</div>', unsafe_allow_html=True)
        for i, p in enumerate(players, 1):
            pl   = p["player"]
            st_  = p["statistics"][0]
            pos  = st_.get("games", {}).get("position", "")
            g    = st_.get("goals", {}).get("total") or 0
            a    = st_.get("goals", {}).get("assists") or 0
            apps = st_.get("games", {}).get("appearences") or 0
            mins = st_.get("games", {}).get("minutes") or 0
            shots= st_.get("shots", {}).get("total") or 0
            pas  = st_.get("passes", {}).get("accuracy") or 0

            st.markdown(
                f'<div class="player-row">'
                f'<div class="player-num">{i}</div>'
                f'<div class="player-name">{pl["name"]}'
                f'<span class="player-pos">({pos})</span></div>'
                f'<div class="player-stat"><div class="player-stat-val">{g}</div>'
                f'<div class="player-stat-lbl">Goals</div></div>'
                f'<div class="player-stat"><div class="player-stat-val">{a}</div>'
                f'<div class="player-stat-lbl">Assists</div></div>'
                f'<div class="player-stat"><div class="player-stat-val">{apps}</div>'
                f'<div class="player-stat-lbl">Apps</div></div>'
                f'<div class="player-stat" style="display:none" data-mobile-hide>'
                f'<div class="player-stat-val">{mins}</div>'
                f'<div class="player-stat-lbl">Mins</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("ยังไม่มีข้อมูลนักเตะ — กด Refresh")

    if st.button("🔄 Refresh นักเตะ", key="refresh_players"):
        for k in ["_cache_players", "_cache_players_ts"]:
            st.session_state.pop(k, None)
        st.rerun()


# ══════════════════════════════════════════════════════════════
# TAB: วิเคราะห์ + Comments (Phase 3)
# ══════════════════════════════════════════════════════════════
elif st.session_state.tab == "analysis":
    st.markdown('<p class="sec-heading">โต๊ะรก วิจารณ์</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">ถึงเวลาตบขมับ! วิเคราะห์เจาะลึกแบบไม่เกรงใจใคร สไตล์ เจมส์ป๊อก LFC</p>', unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(
            f'<div class="editor-card">'
            f'<div class="editor-title">{ANA["title"]}</div>'
            f'<div class="editor-body">{ANA["body"]}</div>'
            f'<div class="editor-quote">{ANA["quote"]}</div></div>',
            unsafe_allow_html=True,
        )
        # Quotes from JSON
        st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)
        for q in QUOTES:
            is_hot = q["style"] == "hot"
            st.markdown(
                f'<div class="{"card card-red-border" if is_hot else "card"}">'
                f'<span class="quote-label" style="color:#C8102E;">{q["speaker"]}</span>'
                f'<div class="{"quote-bold" if is_hot else "quote-text"}">{q["quote"]}</div>'
                f'<div class="quote-note">{q["note"]}</div></div>',
                unsafe_allow_html=True,
            )

    with right:
        riv_color = RIV.get("rival_color","#ef4444")
        st.markdown(
            f'<div class="compare-box">'
            f'<div class="compare-title">เปรียบเทียบคู่แค้น</div>'
            f'<div class="compare-body">{RIV["context"]}</div>'
            f'<div class="compare-row">'
            f'<div><div class="compare-liv">{META["home_short"]}</div>'
            f'<div class="compare-liv-sub">{RIV["home_desc"]}</div></div>'
            f'<div class="compare-vs">VS</div>'
            f'<div><div class="compare-riv" style="color:{riv_color};">{RIV["rival_short"]}</div>'
            f'<div class="compare-riv-sub">{RIV["rival_desc"]}</div></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        # Romano + Gravenberch
        st.markdown(
            f'<div class="grav-card"><div class="grav-icon">🗣️</div><div>'
            f'<div class="grav-label">ไรอัน กราเฟนแบร์ก</div>'
            f'<div class="grav-quote">{GRAV["quote"]}</div>'
            f'<div class="grav-desc">{GRAV["detail"]}</div></div></div>'
            f'<div class="romano-box"><div style="font-size:26px;flex-shrink:0;">📰</div><div>'
            f'<div class="romano-title">Fabrizio Romano Update</div>'
            f'<div class="romano-text">{ROM["update"]}</div></div></div>',
            unsafe_allow_html=True,
        )

        # ── Comment Box (Phase 3 Sheets) ──
        st.markdown(
            '<div class="comment-box" style="margin-top:14px;">'
            '<div class="sheets-badge">🗄️ Google Sheets — คอมเมนต์ถาวร</div>'
            '<div class="comment-title">เพื่อนๆ คิดยังไง?</div>',
            unsafe_allow_html=True,
        )
        nc, ac, dc = st.columns([2, 1.4, 1.8])
        with nc:
            username = st.text_input("ชื่อ", placeholder="เช่น Kopite_1989",
                                     label_visibility="collapsed", key="uname")
        with ac:
            if st.button("🔴 ไล่สล็อตออก!", key="agree_btn", use_container_width=True):
                name = username.strip() or f"Fan_{random.randint(1,999)}"
                if push_comment(name, AGREE_TEXT):
                    st.session_state.comments = fetch_comments()
                    st.rerun()
        with dc:
            if st.button("⚪ ให้โอกาสไปก่อน", key="disagree_btn", use_container_width=True):
                name = username.strip() or f"Fan_{random.randint(1,999)}"
                if push_comment(name, DISAGREE_TEXT):
                    st.session_state.comments = fetch_comments()
                    st.rerun()

        rc, _ = st.columns([1, 3])
        with rc:
            if st.button("🔄 โหลดใหม่", key="reload_btn", use_container_width=True):
                st.session_state.comments = fetch_comments()
                st.rerun()

        if st.session_state.comments:
            st.markdown("".join(render_comment(c) for c in st.session_state.comments[:10]),
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="comment-item" style="color:#94a3b8;text-align:center;">ยังไม่มีคอมเมนต์ เป็นคนแรกได้เลย! 👆</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════
st.markdown(
    f'<div class="lfc-footer">'
    f'<div class="footer-title">เจมส์ป๊อก LFC</div>'
    f'<div class="footer-ref">Data: API-Football • Google Sheets • {META["competition"]} {META["date"]}</div>'
    f'<div class="footer-copy">&copy; 2026 JamesPok LFC — Phase 4 · Full Stack Edition 🔗🗄️🐍</div>'
    f'</div>',
    unsafe_allow_html=True,
)
