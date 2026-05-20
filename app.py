"""
เจมส์ป๊อก LFC Dashboard — Phase 4
✅ Phase 1: UI/UX Streamlit Cloud
✅ Phase 2: JSON Data, Charts, Mobile
✅ Phase 3: Google Sheets Comments
✅ Phase 4: API-Football Real-time (ผล + ตาราง + สถิตินักเตะ) -> ย้ายสู่ Football-Data.org สมบูรณ์แบบ
"""
import json, random, pathlib, datetime, requests, time
import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components

# สองบรรทัดนี้ต้องอยู่แยกกัน และต้องสมบูรณ์
from google.oauth2 import service_account
from googleapiclient.discovery import build

# เพิ่ม Library นี้แยกออกมา
import google.generativeai as genai

# 2. นำฟังก์ชันมาวางไว้ในโซน "API CORE" หรือ "GOOGLE SHEETS"
def get_match_timeline_from_gemini(home_team, away_team, date):
    genai.configure(api_key=st.secrets["gemini_api_key"]["token"])
    model = genai.GenerativeModel('gemini-1.0-flash')
    
    prompt = f"""
    วิเคราะห์เหตุการณ์สำคัญของแมตช์ {home_team} พบ {away_team} วันที่ {date} 
    ขอรายละเอียด: นาทีที่ทำประตู, ใบเหลือง/แดง, การเปลี่ยนตัว 
    ตอบเป็น JSON ตามโครงสร้างนี้: [ {{"minute": "นาที", "title": "เหตุการณ์", "detail": "รายละเอียด"}} ]
    """
    
    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    return json.loads(response.text)
# ... (ฟังก์ชันอื่นๆ ตามเดิม)

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
# CONSTANTS (ปรับปรุงสำหรับ Football-Data.org)
# ══════════════════════════════════════════════════
LIVERPOOL_ID  = 64            # ไอดีของลิเวอร์พูลในค่ายใหม่
SEASON        = 2024          # ปีฤดูกาลปัจจุบัน
CACHE_TTL_SEC = 3600          # 1 ชั่วโมง (ประหยัด quota)
LIVE_TTL_SEC  = 300           # 5 นาที (วันแข่ง)

# รหัสการแข่งขันย่อ (Competition Codes) ตามมาตรฐานของค่ายใหม่
COMPETITIONS = {
    "PL": "Premier League",
    "CL": "Champions League"
}

# ข้อความและคำถามสำหรับการโหวต
POLL_QUESTION = "คุณคิดว่า อาร์เนอ สล็อต ดื้อเกินไปไหมในเกมนี้?"
AGREE_TEXT    = "ดื้อจริง! เปลี่ยนตัวแปลกๆ ทำทีมเสียสมดุล"
DISAGREE_TEXT = "ให้โอกาสไปก่อน ระบบยังใหม่ ต้องปรับจูนกันอีก"

# ══════════════════════════════════════════════════
# API CORE — Phase 4 (Football-Data.org)
# ══════════════════════════════════════════════════
def _api_headers() -> dict:
    return {
        "X-Auth-Token": st.secrets["football_data"]["token"],
        "Content-Type": "application/json"
    }

def _get(endpoint: str, params: dict = None) -> dict | None:
    """raw GET — จัดการ error ให้ครบตามกฎ Football-Data.org"""
    try:
        r = requests.get(
            f"https://api.football-data.org/v4/{endpoint}",
            headers=_api_headers(),
            params=params,
            timeout=10,
        )
        
        # ดักจับกรณีเรียกข้อมูลถี่เกินไป (Rate Limit 10 ครั้ง/นาที ของค่ายนี้)
        if r.status_code == 429:
            st.error("⚠️ เรียกข้อมูลถี่เกินไป (Rate Limit) กรุณารอ 1 นาทีแล้วลองกดใหม่อีกครั้งครับ")
            return None
            
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
        if " " in iso_str:
            return iso_str
        dt = datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
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

# ── ฟังก์ชันดึงข้อมูลการแข่งขัน (เวอร์ชันแก้ปัญหา KeyError ถาวรสำหรับ Football-Data.org) ──
def fetch_all_fixtures_data() -> list:
    """ดึงข้อมูลแมตช์ทั้งหมดของ Liverpool จาก Football-Data.org"""
    def _fetch():
        data = _get(f"teams/{LIVERPOOL_ID}/matches")
        if data and data.get("matches"):
            return data["matches"]
        return []
    return _cached("all_fixtures_all", CACHE_TTL_SEC, _fetch) or []

def fetch_last_fixtures(n: int = 5) -> list:
    """กรองผลการแข่งขันล่าสุด n แมตช์จากข้อมูลรวมด้วย Python"""
    all_fix = fetch_all_fixtures_data()
    if not all_fix:
        return []
    past_fixtures = [f for f in all_fix if f.get("status") == "FINISHED"]
    past_fixtures.sort(key=lambda f: f.get("utcDate", ""), reverse=True)
    
    formatted = []
    for f in past_fixtures[:n]:
        comp_name = f.get("competition", {}).get("name", "Premier League")
        comp_code = f.get("competition", {}).get("code", "PL")
        
        formatted.append({
            "fixture": {
                "date": f.get("utcDate"), 
                "status": {"short": "FT"},
                "venue": {"name": "Anfield"}
            },
            "teams": {
                "home": {"name": f["homeTeam"]["name"], "id": f["homeTeam"]["id"]},
                "away": {"name": f["awayTeam"]["name"], "id": f["awayTeam"]["id"]}
            },
            "goals": {
                "home": f["score"]["fullTime"]["home"], 
                "away": f["score"]["fullTime"]["away"]
            },
            "league": {
                "id": comp_code,
                "name": comp_name
            }
        })
    return formatted

def fetch_next_fixture() -> dict | None:
    """กรองหาแมตช์ถัดไปจากข้อมูลรวมด้วย Python"""
    all_fix = fetch_all_fixtures_data()
    if not all_fix:
        return None
    upcoming = [f for f in all_fix if f.get("status") in ["TIMED", "SCHEDULED"]]
    if upcoming:
        upcoming.sort(key=lambda f: f.get("utcDate", ""))
        nxt = upcoming[0]
        
        comp_name = nxt.get("competition", {}).get("name", "Premier League")
        comp_code = nxt.get("competition", {}).get("code", "PL")
        
        return {
            "fixture": {
                "date": nxt.get("utcDate"), 
                "venue": {"name": "Anfield"}
            }, 
            "teams": {
                "home": {"name": nxt["homeTeam"]["name"]},
                "away": {"name": nxt["awayTeam"]["name"]}
            },
            "league": {
                "id": comp_code,
                "name": comp_name
            }
        }
    return None

def fetch_live_fixture() -> dict | None:
    """กรองหาแมตช์ที่กำลังแข่งขันอยู่ (LIVE)"""
    all_fix = fetch_all_fixtures_data()
    if not all_fix:
        return None
    live_matches = [f for f in all_fix if f.get("status") in ["IN_PLAY", "PAUSED"]]
    if live_matches:
        lm = live_matches[0]
        comp_name = lm.get("competition", {}).get("name", "Premier League")
        comp_code = lm.get("competition", {}).get("code", "PL")
        return {
            "fixture": {
                "status": {"short": "LIVE"},
                "venue": {"name": "Anfield"}
            },
            "teams": {
                "home": {"name": lm["homeTeam"]["name"]},
                "away": {"name": lm["awayTeam"]["name"]}
            },
            "goals": {
                "home": lm["score"]["fullTime"]["home"], 
                "away": lm["score"]["fullTime"]["away"]
            },
            "league": {
                "id": comp_code,
                "name": comp_name
            }
        }
    return None

def fetch_standings() -> dict:
    """ดึงตารางคะแนนพรีเมียร์ลีกและตรวจสอบเงื่อนไขแชมป์ทางคณิตศาสตร์จาก Football-Data.org"""
    def _fetch():
        out = {}
        data = _get("competitions/PL/standings")
        if data and data.get("standings"):
            raw_table = data["standings"][0]["table"]
            
            # ⚽ ตรวจสอบเงื่อนไขแต้มขาดลอยเพื่อฉลองแชมป์
            is_champion_decided = False
            champion_team_name = ""
            if len(raw_table) >= 2:
                p1 = raw_table[0]  # ทีมอันดับ 1
                p2 = raw_table[1]  # ทีมอันดับ 2
                
                remaining_games_p2 = 38 - p2["playedGames"]
                max_possible_points_p2 = p2["points"] + (remaining_games_p2 * 3)
                
                # หากแต้มของอันดับ 1 มากกว่าแต้มสูงสุดเท่าที่อันดับ 2 จะทำได้ = แต้มขาด คว้าแชมป์ชัวร์!
                if p1["points"] > max_possible_points_p2:
                    is_champion_decided = True
                    champion_team_name = p1["team"]["name"]
            
            formatted_table = []
            for item in raw_table:
                formatted_table.append({
                    "rank": item["position"],
                    "team": {
                        "name": item["team"]["name"], 
                        "id": item["team"]["id"], 
                        "logo": item["team"].get("crest", "")
                    },
                    "points": item["points"],
                    "goalsDiff": item["goalDifference"],  # แก้ปัญหา KeyError: goalsDiff ประตูได้เสีย
                    "is_champion_decided": is_champion_decided,
                    "champion_name": champion_team_name,
                    "all": {
                        "played": item["playedGames"],
                        "win": item["won"],
                        "draw": item["draw"],
                        "lose": item["lost"],
                        "goals": {
                            "for": item["goalsFor"], 
                            "against": item["goalsAgainst"]
                        }
                    }
                })
            out["Premier League"] = formatted_table
        return out
    return _cached("standings", CACHE_TTL_SEC, _fetch) or {}

def fetch_player_stats(league_id: str = "PL") -> list:
    """สลับมาดึงอันดับดาวซัลโวรวมของลีกล่าสุด (Top Scorers) เพื่อให้หน้าเว็บไม่โล่งและไม่ติดข้อจำกัดสิทธิ์ค่ายฟรี"""
    def _fetch():
        data = _get("competitions/PL/scorers")
        if data and data.get("scorers"):
            raw_scorers = data["scorers"]
            
            formatted_players = []
            for item in raw_scorers[:8]:  # ดึงมาโชว์ 8 อันดับแรก
                player = item["player"]
                team = item["team"]
                
                formatted_players.append({
                    "player": {
                        "name": player.get("name", "Unknown"),
                        "photo": ""
                    },
                    "statistics": [{
                        "team": {"name": team.get("name", "LFC")},
                        "goals": {
                            "total": item.get("goals", 0),
                            "assists": item.get("assists", 0)
                        }
                    }]
                })
            return formatted_players
        return []
    return _cached("players_top_scorers", CACHE_TTL_SEC, _fetch) or []

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

def save_timeline_to_sheet2(match_name, timeline_data):
    """บันทึกข้อมูลไทม์ไลน์ลง Sheet2"""
    service = get_sheets_service()
    sheet_id = get_sheet_id()
    
    # เตรียมข้อมูลเป็นรายการ (List of lists)
    # สมมติหัวตารางคือ: | แมตช์ | นาที | เหตุการณ์ | รายละเอียด |
    values = []
    for item in timeline_data:
        values.append([
            match_name, 
            item.get("minute", ""), 
            item.get("title", ""), 
            item.get("detail", "")
        ])
    
    # คำสั่งเขียนข้อมูลเข้าต่อท้าย (Append)
    body = {"values": values}
    service.values().append(
        spreadsheetId=sheet_id,
        range="Sheet2!A:D", # กำหนดให้ลงที่ Sheet2 คอลัมน์ A ถึง D
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

def push_comment(user: str, text: str, border: bool = False) -> bool:
    try:
        # 💡 บังคับสร้างโซนเวลาประเทศไทย (UTC + 7) ให้หมดปัญหาเวลาบันทึกเบี้ยวเป็นเวลาเมืองนอก
        tz_th = datetime.timezone(datetime.timedelta(hours=7))
        ts = datetime.datetime.now(tz_th).strftime("%Y-%m-%d %H:%M:%S")
        
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

def fetch_comments() -> list:
    try:
        res = get_sheets_service().values().get(
            spreadsheetId=get_sheet_id(),
            range=f"{SHEET_TAB}!A:D"
        ).execute()
        rows = res.get("values", [])
        out = []
        for r in rows:
            if len(r) >= 3:
                out.append({
                    "ts": r[0],
                    "user": r[1],
                    "text": r[2],
                    "border": r[3] if len(r) > 3 else "False"
                })
        out.reverse()  # ล่าสุดอยู่บน
        return out
    except Exception as e:
        st.warning(f"⚠️ โหลดคอมเมนต์ไม่สำเร็จ: {e}")
        return []

# ══════════════════════════════════════════════════
# LOCAL DATA ENGINE — Phase 2
# ══════════════════════════════════════════════════
def load_match_data() -> dict:
    p = pathlib.Path("match_data.json")
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "meta": {
            "home_team": "Liverpool", "away_team": "Chelsea",
            "home_score": 0, "away_score": 0,
            "date": "2024-10-20", "venue": "Anfield",
            "competition": "Premier League", "matchweek": 8,
            "home_color": "#C8102E", "away_color": "#034694"
        },
        "timeline": [],
        "stats": {"home": {}, "away": {}},
        "spotlight": {"name": "", "age": 0, "stats": [], "note": ""},
        "analysis": {"title": "", "body": "", "quote": ""},
        "rival_compare": []
    }

md = load_match_data()

# ══════════════════════════════════════════════════
# INJECT CUSTOM CSS — Phase 1
# ══════════════════════════════════════════════════
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Sarabun', sans-serif;
        background-color: #0f172a;
        color: #f1f5f9;
    }
    .lfc-header {
        background: linear-gradient(135deg, #C8102E 0%, #8A081D 100%);
        padding: 2.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(200, 16, 46, 0.2);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .lfc-header::before {
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
    }
    .lfc-title { color: #ffffff; font-size: 2.8rem; font-weight: 700; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.4); }
    .lfc-subtitle { color: #fca5a5; font-size: 1.2rem; margin-top: 0.5rem; font-weight: 300; }
    
    .card { background-color: #1e293b; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .card-title { font-size: 1.3rem; font-weight: 600; color: #f1f5f9; margin-bottom: 1rem; border-left: 4px solid #C8102E; padding-left: 0.75rem; }
    
    .score-banner {
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 50%, #1e293b 100%);
        padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 1.5rem; text-align: center;
    }
    .score-team { flex: 1; font-size: 1.5rem; font-weight: 600; }
    .score-number { font-size: 3.5rem; font-weight: 700; color: #ffffff; padding: 0 1.5rem; min-width: 80px; text-shadow: 0 0 10px rgba(255,255,255,0.2); }
    .score-vs { color: #64748b; font-size: 1rem; font-weight: bold; margin-bottom: 0.5rem; }
    
    .timeline-item { display: flex; margin-bottom: 1rem; position: relative; padding-bottom: 1rem; border-bottom: 1px dashed #334155; }
    .timeline-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
    .tl-time { font-weight: 700; color: #f87171; min-width: 50px; }
    .tl-content { flex: 1; padding-left: 0.5rem; }
    
    .quote-box { background: rgba(200, 16, 46, 0.1); border-left: 4px solid #C8102E; padding: 1rem; font-style: italic; border-radius: 0 8px 8px 0; margin-top: 1rem; color: #fca5a5; }
    
    .comment-box { background-color: #0f172a; border-radius: 8px; border: 1px solid #334155; max-height: 400px; overflow-y: auto; padding: 1rem; }
    .comment-item { padding: 0.75rem; border-radius: 6px; background-color: #1e293b; margin-bottom: 0.75rem; border-left: 3px solid #64748b; }
    .comment-user { font-weight: 600; color: #f87171; font-size: 0.9rem; display: flex; justify-content: space-between; }
    .comment-time { color: #475569; font-size: 0.8rem; font-weight: 400; }
    .comment-text { margin-top: 0.25rem; font-size: 0.95rem; color: #cbd5e1; }
    
    .lfc-footer { text-align: center; margin-top: 3rem; padding: 1.5rem; border-top: 1px solid #334155; color: #64748b; font-size: 0.85rem; }
    
    /* HTML Table styling */
    .lfc-table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; font-size: 0.95rem; }
    .lfc-table th { background-color: #0f172a; color: #94a3b8; text-align: center; padding: 10px; font-weight: 600; border-bottom: 2px solid #334155; }
    .lfc-table th.left, .lfc-table td.left { text-align: left; }
    .lfc-table td { padding: 12px 10px; text-align: center; border-bottom: 1px solid #334155; }
    .lfc-table tr:hover { background-color: rgba(255,255,255,0.02); }
    
    .badge { padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 0.8rem; color: white; display: inline-block; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── HEADER ──
st.markdown(
    f'<div class="lfc-header">'
    f'  <div class="lfc-title">เจมส์ป๊อก LFC</div>'
    f'  <div class="lfc-subtitle">วิเคราะห์เจาะลึกหงส์แดง มิติใหม่แห่งการดูบอลหลังเกม</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════
# MAIN LAYOUT
# ══════════════════════════════════════════════════
col_main, col_side = st.columns([2, 1])

with col_main:
   # ── BANNER MATCHWEEK & SCORE (ปรับปรุงดึงแมตช์ทั้งฤดูกาล + ระบุบ้านใครอัตโนมัติ) ──
    all_fixtures = fetch_all_fixtures_data()
    
    if all_fixtures:
        # เรียงจากนัดแรกต้นฤดูกาล ไปจนถึงนัดสุดท้ายของปี
        all_fixtures.sort(key=lambda x: x.get("utcDate", ""))
        
        # สร้างตัวเลือกในกล่อง Dropdown
        fixture_options = []
        for index, fx in enumerate(all_fixtures):
            home_t = fx["homeTeam"]["name"].replace("Liverpool FC", "Liverpool")
            away_t = fx["awayTeam"]["name"].replace("Liverpool FC", "Liverpool")
            status = " (จบเกมแล้ว)" if fx.get("status") == "FINISHED" else " (ยังไม่แข่ง)"
            
            # เช่น "นัดที่ 8: Liverpool vs Chelsea (จบเกมแล้ว)"
            option_text = f"นัดที่ {index + 1}: {home_t} vs {away_t}{status}"
            fixture_options.append((option_text, fx, index + 1))
            
        # สร้างกล่องคอมโบสำหรับการเลือกแมตช์บนหน้าเว็บ
        selected_option = st.selectbox(
            "📅 เลือกแมตช์ที่ต้องการดูข้อมูลในฤดูกาลนี้ :",
            options=fixture_options,
            format_func=lambda x: x[0],
            index=7  # ตั้งค่าเป็นเลข 7 เพื่อให้เปิดหน้าเว็บมาแล้วล็อกอยู่ที่ นัดที่ 8 (Liverpool vs Chelsea) เสมอตามคอนเทนต์ในใจกลางเพจของคุณ
        )
        
        # ดึงข้อมูลแมตช์ที่แฟนบอลเลือก
        _, current_match, match_num = selected_option
        
        h_name = current_match["homeTeam"]["name"].replace("Liverpool FC", "Liverpool")
        a_name = current_match["awayTeam"]["name"].replace("Liverpool FC", "Liverpool")
        comp_name = current_match.get("competition", {}).get("name", "Premier League")
        m_status = current_match.get("status", "")
        m_date = fmt_date(current_match.get("utcDate", ""))
        
        # 🏟️ ระบบตรวจสอบสนามเตะและบอกว่าบ้านใครโดยอัตโนมัติ
        venue_info = f"🏟️ แข่งที่สนามของสโมสร {h_name} (บ้านของ {h_name})"
        
        # จัดการสีสันของตัวอักษรทีมลิเวอร์พูลให้เด่นด้วยสีแดง
        h_color = "#C8102E" if "Liverpool" in h_name else "#94a3b8"
        a_color = "#C8102E" if "Liverpool" in a_name else "#94a3b8"
        
        # ตรวจสอบว่าแมตช์แข่งเสร็จหรือยัง เพื่อแยกแสดงคะแนนกับเวลาเตะ
        if m_status == "FINISHED":
            h_score = current_match["score"]["fullTime"]["home"]
            a_score = current_match["score"]["fullTime"]["away"]
            sub_title_text = f"{comp_name} — นัดที่ {match_num} (แข่งขันเสร็จสิ้น)"
        else:
            h_score = "-"
            a_score = "-"
            sub_title_text = f"⏳ {comp_name} — โปรแกรมนัดที่ {match_num} (ยังไม่ได้แข่งขัน)"
            
        st.markdown(
            f'<div class="score-banner">'
            f'  <div class="score-team" style="color:{h_color}; text-align:right;">{h_name}</div>'
            f'  <div>'
            f'    <div class="score-vs">{sub_title_text}</div>'
            f'    <div style="display:flex; align-items:center; justify-content:center;">'
            f'      <span class="score-number">{h_score}</span>'
            f'      <span style="color:#475569; font-size:1.5rem; font-weight:700;">-</span>'
            f'      <span class="score-number">{a_score}</span>'
            f'    </div>'
            f'    <div style="color:#64748b; font-size:0.85rem; margin-top:0.5rem;">⏰ เวลาเตะ: {m_date} | {venue_info}</div>'
            f'  </div>'
            f'  <div class="score-team" style="color:{a_color}; text-align:left;">{a_name}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        # กรณี API ขัดข้อง ดึงข้อมูลสำรองจากไฟล์ json มาโชว์เพื่อไม่ให้หน้าเว็บระเบิด
        m = md["meta"]
        st.markdown(
            f'<div class="score-banner">'
            f'  <div class="score-team" style="color:{m["home_color"]}; text-align:right;">{m["home_team"]}</div>'
            f'  <div>'
            f'    <div class="score-vs">{m["competition"]} — นัดที่ {m["matchweek"]}</div>'
            f'    <div style="display:flex; align-items:center; justify-content:center;">'
            f'      <span class="score-number">{m["home_score"]}</span>'
            f'      <span style="color:#475569; font-size:1.5rem; font-weight:700;">-</span>'
            f'      <span class="score-number">{m["away_score"]}</span>'
            f'    </div>'
            f'    <div style="color:#64748b; font-size:0.85rem; margin-top:0.5rem;">🏟️ {m["venue"]} | 📅 {m["date"]}</div>'
            f'  </div>'
            f'  <div class="score-team" style="color:{m["away_color"]}; text-align:left;">{m["away_team"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── TAB MENU ──
    tab_timeline, tab_analysis, tab_stats, tab_standings = st.tabs([
        "⏱️ ไทม์ไลน์สำคัญ", "🧐 วิเคราะห์แทคติก", "📊 สถิติทีม & นักเตะ", "🏆 ตารางคะแนน พรีเมียร์ลีก"
    ])

    with tab_timeline:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⏱️ ลำดับเหตุการณ์สำคัญในเกม</div>', unsafe_allow_html=True)
        
        # 💡 เช็กว่าแมตช์ที่เลือกใน Dropdown ด้านบน ตรงกับทีมที่เราเขียนคอนเทนต์ไว้ใน match_data.json หรือไม่
        # (ตรวจสอบจากคำว่า Chelsea หรือชื่อทีมเยือน/เหย้าเพื่อให้แมตช์กัน)
        is_json_match = (md["meta"]["away_team"].lower() in a_name.lower()) or (md["meta"]["home_team"].lower() in h_name.lower())
        
        if m_status != "FINISHED":
            # กรณีเลือกแมตช์ที่ยังไม่ได้แข่งขัน
            st.info("⏳ แมตช์นี้ยังไม่ได้เริ่มแข่งขัน จะอัปเดตเหตุการณ์สำคัญ (ประตู, ใบเหลือง-แดง, เปลี่ยนตัว) ทันทีหลังจบเกมครับ")
        elif is_json_match and md.get("timeline"):
            # กรณีเลือกแมตช์ที่แข่งขันจบแล้ว และตรงกับแมตช์ที่เราวิเคราะห์ไว้ใน JSON (นัด Chelsea)
            for item in md["timeline"]:
                st.markdown(
                    f'<div class="timeline-item">'
                    f'  <div class="tl-time">{item["minute"]}</div>'
                    f'  <div class="tl-content">'
                    f'    <b style="color:#f1f5f9;">{item["title"]}</b>'
                    f'    <div class="comment-text">{item["detail"]}</div>'
                    f'  </div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            # กรณีเลือกแมตช์อื่น ๆ ที่แข่งจบแล้ว แต่เรายังไม่ได้เขียนเหตุการณ์ลงในไฟล์ JSON
            st.warning("📊 แมตช์นี้แข่งจบแล้ว แต่อยู่ระหว่างรอแอดมินอัปเดตข้อมูลเหตุการณ์เชิงลึก (ประตู/เปลี่ยนตัว) ลงในระบบหลังบ้านครับ")
            
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_analysis:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        an = md["analysis"]
        st.markdown(f'<div class="card-title">{an["title"]}</div>', unsafe_allow_html=True)
        st.write(an["body"])
        if an["quote"]:
            st.markdown(f'<div class="quote-box">{an["quote"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_stats:
        # สถิติเปรียบเทียบทีมเดิม (พล็อตด้วย Plotly)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">เปรียบเทียบสถิติทีมหลังเกม</div>', unsafe_allow_html=True)
        s_home = md["stats"].get("home", {})
        s_away = md["stats"].get("away", {})
        
        if s_home:
            categories = list(s_home.keys())
            home_vals  = [float(str(v).replace('%','')) for v in s_home.values()]
            away_vals  = [float(str(v).replace('%','')) for v in s_away.values()]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=categories, x=home_vals, name=m["home_team"],
                orientation='h', marker_color=m["home_color"], text=list(s_home.values()), textposition='auto'
            ))
            fig.add_trace(go.Bar(
                y=categories, x=away_vals, name=m["away_team"],
                orientation='h', marker_color=m["away_color"], text=list(s_away.values()), textposition='auto'
            ))
            fig.update_layout(
                barmode='group', height=350, margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8', family='Sarabun'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig.update_xaxes(showgrid=True, gridcolor='#334155')
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ไม่มีข้อมูลสถิติทีมสำหรับนัดนี้")
        st.markdown('</div>', unsafe_allow_html=True)

        # 👟 สถิตินักเตะดาวซัลโวพรีเมียร์ลีก (ดึงอัตโนมัติจากค่ายใหม่)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">👟 สถิติดาวซัลโวรวมพรีเมียร์ลีก</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#64748b; font-size:0.85rem; margin:-0.5rem 0 1rem 0;">ข้อมูลสดอัปเดตอัตโนมัติจากเซิร์ฟเวอร์</div>', unsafe_allow_html=True)
        
        p_stats = fetch_player_stats("PL")
        if p_stats:
            html_p = """<table class="lfc-table">
            <tr><th class="left">นักเตะ</th><th>สังกัดทีม</th><th>⚽ ประตู</th><th>🅰️ แอสซิสต์</th></tr>"""
            for row in p_stats:
                p_name = row["player"]["name"]
                t_name = row["statistics"][0]["team"]["name"]
                goals  = row["statistics"][0]["goals"]["total"]
                asst   = row["statistics"][0]["goals"]["assists"] or 0
                html_p += f'<tr><td class="left" style="font-weight:600; color:#f1f5f9;">{p_name}</td><td>{t_name}</td><td style="color:#eab308;font-weight:700;">{goals}</td><td>{asst}</td></tr>'
            html_p += "</table>"
            st.markdown(html_p, unsafe_allow_html=True)
        else:
            st.warning("⚠️ ไม่มีข้อมูลสถิตินักเตะดาวซัลโวในขณะนี้")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_standings:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🏆 ตารางคะแนน Premier League 2024/25</div>', unsafe_allow_html=True)
        
        standings_data = fetch_standings()
        if "Premier League" in standings_data and len(standings_data["Premier League"]) > 0:
            table_data = standings_data["Premier League"]
            
            # ตรวจดึงสถานะความขาดของแต้มจากแถวแรกสุดมาเช็กเอฟเฟคแชมป์
            has_champ = table_data[0].get("is_champion_decided", False)
            champ_name = table_data[0].get("champion_name", "")

            # 🎆 หากผลลัพธ์ผ่านเงื่อนไขแต้มขาดอย่างเป็นทางการ ยิงเอฟเฟคพลุฉลองรัวๆ 5 วินาทีทันที!
            if has_champ:
                components.html(
                    f"""
                    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
                    <div id="champ-popup" style="
                        text-align: center; 
                        padding: 20px; 
                        background: linear-gradient(135deg, #1e1b4b, #311015); 
                        border: 3px solid #eab308; 
                        border-radius: 12px;
                        box-shadow: 0 0 30px rgba(234, 179, 8, 0.4);
                        animation: popIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
                        font-family: sans-serif;
                        margin-bottom: 25px;
                    ">
                        <h1 style="color: #eab308; margin: 0; font-size: 2.5rem; text-transform: uppercase; letter-spacing: 2px;">
                            🏆 CHAMPION 🏆
                        </h1>
                        <p style="color: #ffffff; font-size: 1.2rem; margin: 10px 0 0 0;">
                            ยินดีด้วยกับสโมสร <b>{champ_name}</b> คว้าแชมป์พรีเมียร์ลีกฤดูกาลนี้อย่างเป็นทางการ! แต้มขาดลอยแล้ว!
                        </p>
                    </div>

                    <style>
                        @keyframes popIn {{
                            0% {{ transform: scale(0.7); opacity: 0; }}
                            100% {{ transform: scale(1); opacity: 1; }}
                        }}
                    </style>

                    <script>
                        var duration = 5 * 1000;
                        var end = Date.now() + duration;

                        (function frame() {{
                            confetti({{ particleCount: 5, angle: 60, spread: 55, origin: {{ x: 0, y: 0.8 }} }});
                            confetti({{ particleCount: 5, angle: 120, spread: 55, origin: {{ x: 1, y: 0.8 }} }});
                            if (Date.now() < end) {{
                                requestAnimationFrame(frame);
                            }}
                        }}());
                    </script>
                    """,
                    height=150,
                )

            # สร้างโครงสร้างตาราง HTML
            html_table = """<table class="lfc-table">
            <tr><th>อันดับ</th><th class="left">สโมสร</th><th>แข่ง</th><th>ชนะ</th><th>เสมอ</th><th>แพ้</th><th>ได้-เสีย</th><th>+/-</th><th style="color:#eab308;">แต้ม</th></tr>"""
            
            for r in table_data:
                # 💡 ไฮไลท์สีทองเฉพาะทีมอันดับ 1
                if r["rank"] == 1:
                    row_style = 'style="background: linear-gradient(90deg, rgba(234,179,8,0.15) 0%, rgba(0,0,0,0) 100%); font-weight: bold; border-left: 5px solid #eab308;"'
                    rank_badge = '<span style="background:#eab308; color:#000; padding:2px 6px; border-radius:4px; font-size:0.85rem; font-weight:bold;">1 🥇</span>'
                else:
                    row_style = ''
                    rank_badge = f'<span>{r["rank"]}</span>'

                t_name = r["team"]["name"]
                crest  = r["team"]["logo"]
                played = r["all"]["played"]
                win    = r["all"]["win"]
                draw   = r["all"]["draw"]
                lose   = r["all"]["lose"]
                gf     = r["all"]["goals"]["for"]
                ga     = r["all"]["goals"]["against"]
                gd     = r["goalsDiff"]
                pts    = r["points"]
                
                logo_html = f'<img src="{crest}" width="22" style="margin-right:8px; vertical-align:middle; max-height:22px;">' if crest else ""
                
                html_table += f"""<tr {row_style}>
                    <td>{rank_badge}</td>
                    <td class="left" style="font-weight:600;">{logo_html}{t_name}</td>
                    <td>{played}</td>
                    <td>{win}</td>
                    <td>{draw}</td>
                    <td>{lose}</td>
                    <td style="color:#64748b; font-size:0.85rem;">{gf}:{ga}</td>
                    <td style="color:{'#16a34a' if gd >= 0 else '#dc2626'}">{'+' if gd > 0 else ''}{gd}</td>
                    <td style="color:#eab308; font-weight:bold; font-size:1.05rem;">{pts}</td>
                </tr>"""
            html_table += "</table>"
            st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.info("ไม่พบข้อมูลตารางคะแนนพรีเมียร์ลีกในขณะนี้")
        st.markdown('</div>', unsafe_allow_html=True)

with col_side:
    # ── LIVE MATCH TICKER (เตะสด) ──
    live_fix = fetch_live_fixture()
    if live_fix:
        st.markdown('<div class="card" style="border: 1px solid #16a34a; background-color: rgba(22,163,74,0.05);">', unsafe_allow_html=True)
        st.markdown('<div class="card-title" style="color:#16a34a; border-left-color:#16a34a;">🔴 LIVE MATCH NOW</div>', unsafe_allow_html=True)
        lt = live_fix["teams"]
        lg = live_fix.get("goals")
        st.markdown(
            f'<div style="text-align:center; padding:0.5rem 0;">'
            f'  <div style="font-size:1.1rem; font-weight:600; color:#cbd5e1;">{lt["home"]["name"]} vs {lt["away"]["name"]}</div>'
            f'  <div style="font-size:2.5rem; font-weight:700; color:#16a34a; margin:0.25rem 0;">{lg["home"]} - {lg["away"]}</div>'
            f'  <span class="badge" style="background-color:#16a34a; animation: pulse 1.5s infinite;">กำลังแข่งขัน</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ── NEXT FIXTURE (นัดถัดไป) ──
    next_fix = fetch_next_fixture()
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📅 โปรแกรมนัดถัดไป</div>', unsafe_allow_html=True)
    if next_fix:
        nt = next_fix["teams"]
        nc = COMPETITIONS.get(next_fix["league"]["id"], next_fix["league"]["name"])
        st.markdown(
            f'<div style="font-size:0.85rem; color:#64748b; font-weight:600; text-transform:uppercase; margin-bottom:0.25rem;">🏆 {nc}</div>'
            f'<div style="font-size:1.1rem; font-weight:600; color:#f1f5f9; margin-bottom:0.5rem;">{nt["home"]["name"]} <span style="color:#64748b;font-size:0.9rem;">vs</span> {nt["away"]["name"]}</div>'
            f'<div style="font-size:0.9rem; color:#cbd5e1;">⏰ {fmt_date(next_fix["fixture"]["date"])}</div>'
            f'<div style="font-size:0.85rem; color:#64748b; margin-top:0.25rem;">🏟️ {next_fix["fixture"]["venue"]["name"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div style="color:#64748b;font-size:0.9rem;">ไม่พบโปรแกรมแข่งขันที่กำลังมาถึง</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── LAST 5 MATCHES (ฟอร์มล่าสุดย้อนหลัง) ──
    last_fixtures = fetch_last_fixtures(5)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🕒 ผลการแข่งขัน 5 นัดหลังสุด</div>', unsafe_allow_html=True)
    if last_fixtures:
        for fx in last_fixtures:
            t = fx["teams"]
            g = fx["goals"]
            comp = COMPETITIONS.get(fx["league"]["id"], fx["league"]["name"])
            badge_txt, badge_color = result_badge(g["home"], g["away"], t["home"]["id"])
            
            st.markdown(
                f'<div style="display:flex; align-items:center; justify-content:between; margin-bottom:0.75rem; font-size:0.9rem; border-bottom:1px solid #1e293b; padding-bottom:0.5rem;">'
                f'  <div style="flex:1; padding-right:0.5rem;">'
                f'    <div style="font-size:0.75rem; color:#475569; font-weight:600;">🏆 {comp}</div>'
                f'    <div style="font-weight:600; color:#cbd5e1; margin:0.1rem 0;">{t["home"]["name"]} {g["home"]}-{g["away"]} {t["away"]["name"]}</div>'
                f'    <div style="font-size:0.8rem; color:#64748b;">{fmt_date(fx["fixture"]["date"])}</div>'
                f'  </div>'
                f'  <div style="text-align:right;">'
                f'    <span class="badge" style="background-color:{badge_color}; min-width:24px; text-align:center;">{badge_txt}</span>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div style="color:#64748b;font-size:0.9rem;">ยังไม่มีบันทึกข้อมูลฟอร์มย้อนหลัง</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── RIVAL MONITOR ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👀 ซูมฟอร์มคู่แข่งทีมสำคัญ</div>', unsafe_allow_html=True)
    if md.get("rival_compare"):
        for rival in md["rival_compare"]:
            # 💡 เพิ่มระบบดักจับประเภทข้อมูล (ป้องกัน AttributeError ถาวร)
            if isinstance(rival, dict):
                # กรณีที่ก้อนข้อมูลมาเป็นดิกชันนารีมีคีย์ซ้อน
                rival_name = rival.get("team", "Unknown Team")
                rival_pts  = rival.get("points", "-")
                rival_play = rival.get("played", "-")
                rival_last = rival.get("last_match", "-")
                rival_comm = rival.get("status_comment", "")
            else:
                # กรณีที่ข้อมูลใน json ดั้งเดิมหลุดมาเป็น String ข้อความตรงๆ หรือแบบอื่น
                rival_name = str(rival)
                rival_pts  = "-"
                rival_play = "-"
                rival_last = "-"
                rival_comm = ""

            st.markdown(
                f'<div style="margin-bottom:0.75rem; font-size:0.9rem; padding-bottom:0.5rem; border-bottom:1px solid #1e293b;">'
                f'  <div style="display:flex; justify-content:space-between; font-weight:600; color:#e2e8f0;">'
                f'    <span>{rival_name}</span>'
                f'    <span style="color:#eab308;">{rival_pts} แต้ม (นัดที่ {rival_play})</span>'
                f'  </div>'
                f'  <div style="font-size:0.8rem; color:#64748b; margin-top:0.15rem;">📌 นัดล่าสุด: {rival_last}</div>'
                f'  <div style="font-size:0.85rem; color:#94a3b8; font-style:italic;">{rival_comm}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("ไม่มีข้อมูลฟอร์มทีมคู่แข่ง")
    st.markdown('</div>', unsafe_allow_html=True)
    # ── POLLING ENGINE & COMMENTS — Phase 3 ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">🗳️ โพลล์แฟนบอล: {POLL_QUESTION}</div>', unsafe_allow_html=True)

    if "comments" not in st.session_state:
        st.session_state.comments = fetch_comments()

    # นับคะแนนโหวตสดๆ จาก Sheets เพื่อสร้าง Real-time Chart
    agree_count = sum(1 for c in st.session_state.comments if c["text"] == AGREE_TEXT)
    disagree_count = sum(1 for c in st.session_state.comments if c["text"] == DISAGREE_TEXT)
    total_votes = agree_count + disagree_count

    if total_votes > 0:
        pct_agree = int((agree_count / total_votes) * 100)
        pct_disagree = 100 - pct_agree
        
        # แสดงผลแท่งสัดส่วนสไตล์โหวตสวยๆ
        st.markdown(
            f'<div style="margin-bottom: 1rem; font-size:0.9rem;">'
            f'  <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem;">'
            f'    <span style="color:#f87171;font-weight:600;">🔴 ดื้อ ({agree_count} คน)</span>'
            f'    <span style="color:#94a3b8;font-weight:600;">⚪ ให้โอกาส ({disagree_count} คน)</span>'
            f'  </div>'
            f'  <div style="display:flex; width:100%; height:12px; border-radius:6px; overflow:hidden; background-color:#334155;">'
            f'    <div style="width:{pct_agree}%; background-color:#C8102E; height:100%;"></div>'
            f'    <div style="width:{pct_disagree}%; background-color:#94a3b8; height:100%;"></div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ส่วนแสดงกล่องกรอกคอมเมนต์และกดโหวต
    username = st.text_input("💬 ชื่อเล่นของคุณ :", placeholder="เช่น บังโมเมืองนนท์", max_chars=20)

    def render_comment(c) -> str:
        border_cls = 'style="border-left: 4px solid #C8102E;"' if c["border"] == "True" else ""
        return (
            f'<div class="comment-item" {border_cls}>'
            f'  <div class="comment-user">{c["user"]} <span class="comment-time">🕒 {c["ts"]}</span></div>'
            f'  <div class="comment-text">{c["text"]}</div>'
            f'</div>'
        )

    st.markdown('<div class="comment-box">', unsafe_allow_html=True)
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        if st.button("🔴 ดื้อเกินไปจริง!", key="agree_btn", use_container_width=True):
            name = username.strip() or f"Fan_{random.randint(1,999)}"
            if push_comment(name, AGREE_TEXT, border=True):
                st.session_state.comments = fetch_comments()
                st.rerun()
    with col_v2:
        if st.button("⚪ ให้โอกาสไปก่อน", key="disagree_btn", use_container_width=True):
            name = username.strip() or f"Fan_{random.randint(1,999)}"
            if push_comment(name, DISAGREE_TEXT):
                st.session_state.comments = fetch_comments()
                st.rerun()

    # ช่องทางพิมพ์ข้อความคอมเมนต์อิสระ
    custom_comment = st.text_input("✍️ พิมพ์ข้อความแสดงความเห็นเพิ่มเติม :", placeholder="ใส่ความคิดเห็นหลังเกมของคุณที่นี่...", max_chars=100)
    if st.button("🚀 ส่งความเห็น", key="custom_msg_btn", use_container_width=True):
        txt = custom_comment.strip()
        if txt:
            name = username.strip() or f"Fan_{random.randint(1,999)}"
            if push_comment(name, txt, border=False):
                st.session_state.comments = fetch_comments()
                st.rerun()
        else:
            st.warning("⚠️ กรุณากรอกข้อความก่อนกดส่งครับ")

    rc, _ = st.columns([1, 3])
    with rc:
        if st.button("🔄 โหลดใหม่", key="reload_btn", use_container_width=True):
            st.session_state.comments = fetch_comments()
            st.rerun()

    if st.session_state.comments:
        st.markdown("".join(render_comment(c) for c in st.session_state.comments[:10]), unsafe_allow_html=True)
    else:
        st.markdown('<div class="comment-item" style="color:#94a3b8;text-align:center;">ยังไม่มีคอมเมนต์ เป็นคนแรกได้เลย! 👆</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if st.button("🤖 วิเคราะห์แมตช์ด้วย Gemini & บันทึกเข้า Sheet2"):
    with st.spinner("Gemini กำลังอ่านข้อมูล..."):
        # 1. ดึงข้อมูลจาก AI
        timeline_data = get_match_timeline_from_gemini(current_home_name, current_away_name, current_m_date)
        
        if timeline_data:
            # 2. บันทึกลง Sheet2
            save_timeline_to_sheet2(f"{current_home_name} vs {current_away_name}", timeline_data)
            st.success("✨ วิเคราะห์สำเร็จและบันทึกลง Sheet2 เรียบร้อยแล้ว!")
        else:
            st.error("ไม่สามารถดึงข้อมูลได้")
# ══════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════
st.markdown(
    f'<div class="lfc-footer">'
    f'  <div class="footer-credit">© 2026 JamesPok LFC Dashboard. All Rights Reserved.</div>'
    f'  <div style="margin-top:0.25rem; font-size:0.75rem; color:#475569;">Powered by Streamlit Cloud & Football-Data.org API</div>'
    f'</div>',
    unsafe_allow_html=True,
)
