"""
เจมส์ป๊อก LFC Dashboard — Phase 4 (แก้ไขบั๊ก Gemini 404 & ลอจิกปุ่มกดสัมพันธ์แมตช์)
"""
import json, random, pathlib, datetime, requests, time
import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components

# สองบรรทัดนี้ต้องอยู่แยกกัน และต้องสมบูรณ์
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ══════════════════════════════════════════════════
# GEMINI API ENGINE (ยิงตรงผ่าน HTTP Requests ไม่ผ่าน SDK ป้องกัน 404)
# ══════════════════════════════════════════════════
def get_match_timeline_from_gemini(home_team, away_team, date):
    import requests
    import json
    
    api_key = st.secrets["gemini_api_key"]["token"]
    
    # 🌟 URL ตัวเก่ง ยิงตรงเข้าโมเดล Flash เท่านั้น
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""
    ค้นหาข้อมูล Timeline (ลำดับเหตุการณ์จริง) ของการแข่งขันฟุตบอลระหว่าง {home_team} พบ {away_team} ที่แข่งขันในวันที่ {date}
    ให้ดึงเฉพาะข้อมูลเหตุการณ์สำคัญที่เกิดขึ้นจริงในเกมเท่านั้น (อ้างอิงตามสถิติการแข่งขันจริง) เช่น:
    - การเช็ค VAR (เช่น ยกเลิกลูกโทษ, ริบประตู)
    - การเปลี่ยนตัวผู้เล่น (ระบุชื่อคนเข้า และคนออก)
    - การทำประตู (ใครยิง, ใครแอสซิสต์)
    - ใบเหลือง / ใบแดง
    
    ตอบกลับเป็นภาษาไทย ในรูปแบบ JSON เท่านั้น ตามโครงสร้างนี้: 
    [ {{"minute": "นาที (เช่น 90', 90+1')", "title": "ประเภทเหตุการณ์", "detail": "รายละเอียด (เช่น ไม่ได้ลูกโทษ, เข้า: เทรย์ ไนโอนี ออก: เจเรมี ฟริมปง)"}} ]
    
    *เงื่อนไขสำคัญ:
    1. หากแมตช์นี้ยังไม่แข่งขัน หรือหาข้อมูลเหตุการณ์จริงไม่พบ ให้ตอบกลับเป็น [ {{"minute": "-", "title": "ไม่มีข้อมูล", "detail": "ยังไม่พบข้อมูลไทม์ไลน์การแข่งขันจริงของแมตช์นี้"}} ]
    2. ห้ามมีข้อความอธิบายอื่นใดเด็ดขาดนอกจากโครงสร้าง JSON นี้
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        res_data = response.json()
        
        if "error" in res_data:
            st.error(f"❌ Google API แจ้งเตือนข้อผิดพลาด: {res_data['error'].get('message', 'ไม่ทราบสาเหตุ')}")
            return []
            
        if "candidates" in res_data and len(res_data["candidates"]) > 0:
            content = res_data["candidates"][0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                ai_response_text = parts[0].get("text", "")
                clean_text = ai_response_text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_text)
                
        return []
    except Exception as e:
        st.error(f"⚠️ AI เกิดข้อผิดพลาดในการแกะข้อมูล: {e}")
        return []
        
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
LIVERPOOL_ID  = 64            
SEASON        = 2024          
CACHE_TTL_SEC = 3600          
LIVE_TTL_SEC  = 300           

COMPETITIONS = {
    "PL": "Premier League",
    "CL": "Champions League"
}

POLL_QUESTION = "คุณคิดว่า อาร์เนอ สล็อต ดื้อเกินไปไหมในเกมนี้?"
AGREE_TEXT    = "ดื้อจริง! เปลี่ยนตัวแปลกๆ ทำทีมเสียสมดุล"
DISAGREE_TEXT = "ให้โอกาสไปก่อน ระบบยังใหม่ ต้องปรับจูนกันอีก"

# ══════════════════════════════════════════════════
# API CORE (Football-Data.org)
# ══════════════════════════════════════════════════
def _api_headers() -> dict:
    return {
        "X-Auth-Token": st.secrets["football_data"]["token"],
        "Content-Type": "application/json"
    }

def _get(endpoint: str, params: dict = None) -> dict | None:
    try:
        r = requests.get(
            f"https://api.football-data.org/v4/{endpoint}",
            headers=_api_headers(),
            params=params,
            timeout=10,
        )
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
    except Exception as e:
        st.warning(f"⚠️ API error: {e}")
        return None

def _cache_key(name: str) -> str:
    return f"_cache_{name}"

def _cached(name: str, ttl: int, fetch_fn):
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

def fmt_date(iso_str: str) -> str:
    try:
        if " " in iso_str:
            return iso_str
        dt = datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        dt_th = dt.astimezone(datetime.timezone(datetime.timedelta(hours=7)))
        return dt_th.strftime("%d/%m/%Y %H:%M น.")
    except:
        return iso_str[:16]

def result_badge(home_goals: int, away_goals: int, home_id: int) -> tuple[str, str]:
    if home_goals == away_goals:
        return "D", "#ca8a04"
    is_lfc_home = (home_id == LIVERPOOL_ID)
    if home_goals > away_goals:
        return ("W", "#16a34a") if is_lfc_home else ("L", "#C8102E")
    else:
        return ("L", "#C8102E") if is_lfc_home else ("W", "#16a34a")

def fetch_all_fixtures_data() -> list:
    def _fetch():
        data = _get(f"teams/{LIVERPOOL_ID}/matches")
        if data and data.get("matches"):
            return data["matches"]
        return []
    return _cached("all_fixtures_all", CACHE_TTL_SEC, _fetch) or []

def fetch_last_fixtures(n: int = 5) -> list:
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
            "fixture": {"date": f.get("utcDate"), "status": {"short": "FT"}, "venue": {"name": "Anfield"}},
            "teams": {
                "home": {"name": f["homeTeam"]["name"], "id": f["homeTeam"]["id"]},
                "away": {"name": f["awayTeam"]["name"], "id": f["awayTeam"]["id"]}
            },
            "goals": {"home": f["score"]["fullTime"]["home"], "away": f["score"]["fullTime"]["away"]},
            "league": {"id": comp_code, "name": comp_name}
        })
    return formatted

def fetch_next_fixture() -> dict | None:
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
            "fixture": {"date": nxt.get("utcDate"), "venue": {"name": "Anfield"}}, 
            "teams": {"home": {"name": nxt["homeTeam"]["name"]}, "away": {"name": nxt["awayTeam"]["name"]}},
            "league": {"id": comp_code, "name": comp_name}
        }
    return None

def fetch_live_fixture() -> dict | None:
    all_fix = fetch_all_fixtures_data()
    if not all_fix:
        return None
    live_matches = [f for f in all_fix if f.get("status") in ["IN_PLAY", "PAUSED"]]
    if live_matches:
        lm = live_matches[0]
        comp_name = lm.get("competition", {}).get("name", "Premier League")
        comp_code = lm.get("competition", {}).get("code", "PL")
        return {
            "fixture": {"status": {"short": "LIVE"}, "venue": {"name": "Anfield"}},
            "teams": {"home": {"name": lm["homeTeam"]["name"]}, "away": {"name": lm["awayTeam"]["name"]}},
            "goals": {"home": lm["score"]["fullTime"]["home"], "away": lm["score"]["fullTime"]["away"]},
            "league": {"id": comp_code, "name": comp_name}
        }
    return None

def fetch_standings() -> dict:
    def _fetch():
        out = {}
        data = _get("competitions/PL/standings")
        if data and data.get("standings"):
            raw_table = data["standings"][0]["table"]
            is_champion_decided = False
            champion_team_name = ""
            if len(raw_table) >= 2:
                p1 = raw_table[0]  
                p2 = raw_table[1]  
                remaining_games_p2 = 38 - p2["playedGames"]
                max_possible_points_p2 = p2["points"] + (remaining_games_p2 * 3)
                if p1["points"] > max_possible_points_p2:
                    is_champion_decided = True
                    champion_team_name = p1["team"]["name"]
            
            formatted_table = []
            for item in raw_table:
                formatted_table.append({
                    "rank": item["position"],
                    "team": {"name": item["team"]["name"], "id": item["team"]["id"], "logo": item["team"].get("crest", "")},
                    "points": item["points"],
                    "goalsDiff": item["goalDifference"],  
                    "is_champion_decided": is_champion_decided,
                    "champion_name": champion_team_name,
                    "all": {
                        "played": item["playedGames"], "win": item["won"], "draw": item["draw"], "lose": item["lost"],
                        "goals": {"for": item["goalsFor"], "against": item["goalsAgainst"]}
                    }
                })
            out["Premier League"] = formatted_table
        return out
    return _cached("standings", CACHE_TTL_SEC, _fetch) or {}

def fetch_player_stats(league_id: str = "PL") -> list:
    def _fetch():
        data = _get("competitions/PL/scorers")
        if data and data.get("scorers"):
            raw_scorers = data["scorers"]
            formatted_players = []
            for item in raw_scorers[:8]:  
                player = item["player"]
                team = item["team"]
                formatted_players.append({
                    "player": {"name": player.get("name", "Unknown"), "photo": ""},
                    "statistics": [{"team": {"name": team.get("name", "LFC")}, "goals": {"total": item.get("goals", 0), "assists": item.get("assists", 0)}}]
                })
            return formatted_players
        return []
    return _cached("players_top_scorers", CACHE_TTL_SEC, _fetch) or []

# ══════════════════════════════════════════════════
# GOOGLE SHEETS CORE
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
    """บันทึกข้อมูลไทม์ไลน์ที่ AI สร้างลง Sheet2"""
    try:
        service = get_sheets_service()
        sheet_id = get_sheet_id()
        values = []
        for item in timeline_data:
            values.append([match_name, item.get("minute", ""), item.get("title", ""), item.get("detail", "")])
        
        body = {"values": values}
        service.values().append(
            spreadsheetId=sheet_id,
            range="Sheet2!A:D", 
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        return True
    except Exception as e:
        st.error(f"❌ บันทึกลง Sheet2 ไม่สำเร็จ: {e}")
        return False

def fetch_timeline_from_sheet2(match_name) -> list:
    """ดึงข้อมูลไทม์ไลน์เฉพาะของแมตช์ที่เลือกจาก Sheet2"""
    try:
        service = get_sheets_service()
        sheet_id = get_sheet_id()
        res = service.values().get(spreadsheetId=sheet_id, range="Sheet2!A:D").execute()
        rows = res.get("values", [])
        
        match_timeline = []
        for r in rows:
            if len(r) >= 4 and r[0] == match_name:
                match_timeline.append({
                    "minute": r[1],
                    "title": r[2],
                    "detail": r[3]
                })
        return match_timeline
    except Exception as e:
        return []

def push_comment(user: str, text: str, border: bool = False) -> bool:
    try:
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
        res = get_sheets_service().values().get(spreadsheetId=get_sheet_id(), range=f"{SHEET_TAB}!A:D").execute()
        rows = res.get("values", [])
        out = []
        for r in rows:
            if len(r) >= 3:
                out.append({"ts": r[0], "user": r[1], "text": r[2], "border": r[3] if len(r) > 3 else "False"})
        out.reverse()  
        return out
    except Exception as e:
        st.warning(f"⚠️ โหลดคอมเมนต์ไม่สำเร็จ: {e}")
        return []

# ══════════════════════════════════════════════════
# LOCAL DATA ENGINE
# ══════════════════════════════════════════════════
def load_match_data() -> dict:
    p = pathlib.Path("match_data.json")
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "meta": {
            "home_team": "Liverpool", "away_team": "Chelsea", "home_score": 0, "away_score": 0,
            "date": "2024-10-20", "venue": "Anfield", "competition": "Premier League", "matchweek": 8,
            "home_color": "#C8102E", "away_color": "#034694"
        },
        "timeline": [], "stats": {"home": {}, "away": {}}, "spotlight": {"name": "", "age": 0, "stats": [], "note": ""},
        "analysis": {"title": "", "body": "", "quote": ""}, "rival_compare": []
    }

md = load_match_data()

# ══════════════════════════════════════════════════
# INJECT CUSTOM CSS
# ══════════════════════════════════════════════════
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght=300;400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Sarabun', sans-serif; background-color: #0f172a; color: #f1f5f9; }
    .lfc-header { background: linear-gradient(135deg, #C8102E 0%, #8A081D 100%); padding: 2.5rem; border-radius: 16px; text-align: center; box-shadow: 0 10px 25px rgba(200, 16, 46, 0.2); margin-bottom: 2rem; position: relative; overflow: hidden; }
    .lfc-title { color: #ffffff; font-size: 2.8rem; font-weight: 700; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.4); }
    .lfc-subtitle { color: #fca5a5; font-size: 1.2rem; margin-top: 0.5rem; font-weight: 300; }
    .card { background-color: #1e293b; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .card-title { font-size: 1.3rem; font-weight: 600; color: #f1f5f9; margin-bottom: 1rem; border-left: 4px solid #C8102E; padding-left: 0.75rem; }
    .score-banner { display: flex; align-items: center; justify-content: center; background: linear-gradient(90deg, #1e293b 0%, #0f172a 50%, #1e293b 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 1.5rem; text-align: center; }
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
    .lfc-table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; font-size: 0.95rem; }
    .lfc-table th { background-color: #0f172a; color: #94a3b8; text-align: center; padding: 10px; font-weight: 600; border-bottom: 2px solid #334155; }
    .lfc-table th.left, .lfc-table td.left { text-align: left; }
    .lfc-table td { padding: 12px 10px; text-align: center; border-bottom: 1px solid #334155; }
    .badge { padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 0.8rem; color: white; display: inline-block; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── HEADER ──
st.markdown('<div class="lfc-header"><div class="lfc-title">เจมส์ป๊อก LFC</div><div class="lfc-subtitle">วิเคราะห์เจาะลึกหงส์แดง มิติใหม่แห่งการดูบอลหลังเกม</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# MAIN LAYOUT
# ══════════════════════════════════════════════════
col_main, col_side = st.columns([2, 1])

# ประกาศตัวแปร Global ไว้ล่วงหน้าเพื่อกัน NameError
current_home_name = "Liverpool"
current_away_name = "Opponent"
current_m_date = "2026-05-20"
m_status = "UNKNOWN"

with col_main:
    all_fixtures = fetch_all_fixtures_data()
    if all_fixtures:
        all_fixtures.sort(key=lambda x: x.get("utcDate", ""))
        fixture_options = []
        for index, fx in enumerate(all_fixtures):
            home_t = fx["homeTeam"]["name"].replace("Liverpool FC", "Liverpool")
            away_t = fx["awayTeam"]["name"].replace("Liverpool FC", "Liverpool")
            status = " (จบเกมแล้ว)" if fx.get("status") == "FINISHED" else " (ยังไม่แข่ง)"
            option_text = f"นัดที่ {index + 1}: {home_t} vs {away_t}{status}"
            fixture_options.append((option_text, fx, index + 1))
            
        selected_option = st.selectbox(
            "📅 เลือกแมตช์ที่ต้องการดูข้อมูลในฤดูกาลนี้ :",
            options=fixture_options,
            format_func=lambda x: x[0],
            index=7  
        )
        
        _, current_match, match_num = selected_option
        current_home_name = current_match["homeTeam"]["name"].replace("Liverpool FC", "Liverpool")
        current_away_name = current_match["awayTeam"]["name"].replace("Liverpool FC", "Liverpool")
        comp_name = current_match.get("competition", {}).get("name", "Premier League")
        m_status = current_match.get("status", "")
        current_m_date = current_match.get("utcDate", "").split("T")[0]
        m_date_display = fmt_date(current_match.get("utcDate", ""))
        
        venue_info = f"🏟️ แข่งที่สนามของสโมสร {current_home_name} (บ้านของ {current_home_name})"
        h_color = "#C8102E" if "Liverpool" in current_home_name else "#94a3b8"
        a_color = "#C8102E" if "Liverpool" in current_away_name else "#94a3b8"
        
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
            f'  <div class="score-team" style="color:{h_color}; text-align:right;">{current_home_name}</div>'
            f'  <div>'
            f'    <div class="score-vs">{sub_title_text}</div>'
            f'    <div style="display:flex; align-items:center; justify-content:center;">'
            f'      <span class="score-number">{h_score}</span>'
            f'      <span style="color:#475569; font-size:1.5rem; font-weight:700;">-</span>'
            f'      <span class="score-number">{a_score}</span>'
            f'    </div>'
            f'    <div style="color:#64748b; font-size:0.85rem; margin-top:0.5rem;">⏰ เวลาเตะ: {m_date_display} | {venue_info}</div>'
            f'  </div>'
            f'  <div class="score-team" style="color:{a_color}; text-align:left;">{current_away_name}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        m = md["meta"]
        current_home_name, current_away_name, current_m_date = m["home_team"], m["away_team"], m["date"]
        st.markdown(f'<div class="score-banner"><div class="score-team" style="color:{m["home_color"]}; text-align:right;">{m["home_team"]}</div><div><div class="score-vs">{m["competition"]}</div><div><span class="score-number">{m["home_score"]}</span>-<span>{m["away_score"]}</span></div></div><div class="score-team" style="color:{m["away_color"]};">{m["away_team"]}</div></div>', unsafe_allow_html=True)

    # ── TAB MENU ──
    tab_timeline, tab_analysis, tab_stats, tab_standings = st.tabs([
        "⏱️ ไทม์ไลน์สำคัญ", "🧐 วิเคราะห์แทคติก", "📊 สถิติทีม & นักเตะ", "🏆 ตารางคะแนน พรีเมียร์ลีก"
    ])

    with tab_timeline:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⏱️ ลำดับเหตุการณ์สำคัญในเกม</div>', unsafe_allow_html=True)
        
        match_title_key = f"{current_home_name} vs {current_away_name}"
        
        # 1. ปุ่มสั่ง AI วิเคราะห์ (ล้างลอจิกเก่าที่พังออกหมดแล้ว)
        if m_status != "FINISHED":
            st.info("⏳ แมตช์นี้ยังไม่ได้เริ่มแข่งขัน จะเปิดให้ AI วิเคราะห์เหตุการณ์ได้หลังจบเกมครับ")
        else:
            if st.button(f"🤖 สั่ง AI วิเคราะห์ไทม์ไลน์คู่ {match_title_key}", use_container_width=True):
                with st.spinner("Gemini กำลังเจาะลึกแมตช์และบันทึกลงฐานข้อมูล Sheet2..."):
                    # 🌟 เรียกใช้ฟังก์ชันตัวใหม่ล่าสุด ไม่วิ่งไปหาฟังก์ชันโบราณข้างล่างแล้ว
                    ai_timeline = get_match_timeline_from_gemini(current_home_name, current_away_name, current_m_date)
                    if ai_timeline:
                        save_timeline_to_sheet2(match_title_key, ai_timeline)
                        st.success("✨ AI สรุปประมวลผลและอัปเดตลง Sheet2 สำเร็จ!")
                        st.rerun()
            
            st.markdown("---")
            
            # 2. ดึงข้อมูลไทม์ไลน์มาแสดงผล (ย่อหน้าตรงเป๊ะ ไม่ขึ้น IndentationError แน่นอน)
            db_timeline = fetch_timeline_from_sheet2(match_title_key)
            is_json_match = (md["meta"]["away_team"].lower() in current_away_name.lower()) or (md["meta"]["home_team"].lower() in current_home_name.lower())
            
            if db_timeline:
                st.info("📊 ข้อมูลไทม์ไลน์นี้ดึงสดมาจาก Google Sheets (Sheet2) ที่ AI วิเคราะห์ไว้")
                for item in db_timeline:
                    st.markdown(f'<div class="timeline-item"><div class="tl-time">{item["minute"]}</div><div class="tl-content"><b>{item["title"]}</b><div class="comment-text">{item["detail"]}</div></div></div>', unsafe_allow_html=True)
            elif is_json_match and md.get("timeline"):
                st.info("คอลัมน์ข้อมูลสำรองจากไฟล์ระบบหลังบ้าน (นัดเจอ Chelsea)")
                for item in md["timeline"]:
                    st.markdown(f'<div class="timeline-item"><div class="tl-time">{item["minute"]}</div><div class="tl-content"><b>{item["title"]}</b><div class="comment-text">{item["detail"]}</div></div></div>', unsafe_allow_html=True)
            else:
                st.warning("💡 แมตช์นี้ยังไม่มีข้อมูลไทม์ไลน์ในระบบ กดปุ่มด้านบนเพื่อให้ AI ช่วยวิเคราะห์สร้างข้อมูลใหม่ได้เลยครับ")
            
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
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">เปรียบเทียบสถิติทีมหลังเกม</div>', unsafe_allow_html=True)
        s_home = md["stats"].get("home", {})
        s_away = md["stats"].get("away", {})
        
        if s_home:
            categories = list(s_home.keys())
            home_vals  = [float(str(v).replace('%','')) for v in s_home.values()]
            away_vals  = [float(str(v).replace('%','')) for v in s_away.values()]
            fig = go.Figure()
            fig.add_trace(go.Bar(y=categories, x=home_vals, name=current_home_name, orientation='h', marker_color="#C8102E", text=list(s_home.values()), textposition='auto'))
            fig.add_trace(go.Bar(y=categories, x=away_vals, name=current_away_name, orientation='h', marker_color="#034694", text=list(s_away.values()), textposition='auto'))
            fig.update_layout(barmode='group', height=350, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8', family='Sarabun'), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ไม่มีข้อมูลสถิติทีมสำหรับนัดนี้")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">👟 สถิติดาวซัลโวรวมพรีเมียร์ลีก</div>', unsafe_allow_html=True)
        p_stats = fetch_player_stats("PL")
        if p_stats:
            html_p = """<table class="lfc-table"><tr><th class="left">นักเตะ</th><th>สังกัดทีม</th><th>⚽ ประตู</th><th>🅰️ แอสซิสต์</th></tr>"""
            for row in p_stats:
                html_p += f'<tr><td class="left" style="font-weight:600; color:#f1f5f9;">{row["player"]["name"]}</td><td>{row["statistics"][0]["team"]["name"]}</td><td style="color:#eab308;font-weight:700;">{row["statistics"][0]["goals"]["total"]}</td><td>{row["statistics"][0]["goals"]["assists"] or 0}</td></tr>'
            html_p += "</table>"
            st.markdown(html_p, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_standings:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🏆 ตารางคะแนน Premier League 2024/25</div>', unsafe_allow_html=True)
        standings_data = fetch_standings()
        if "Premier League" in standings_data and len(standings_data["Premier League"]) > 0:
            table_data = standings_data["Premier League"]
            has_champ = table_data[0].get("is_champion_decided", False)
            champ_name = table_data[0].get("champion_name", "")
            if has_champ:
                components.html(f"""<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script><div id="champ-popup" style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1e1b4b, #311015); border: 3px solid #eab308; border-radius: 12px; font-family: sans-serif; margin-bottom: 25px;"><h1 style="color: #eab308; margin: 0; font-size: 2.5rem;">🏆 CHAMPION 🏆</h1><p style="color: #ffffff; font-size: 1.2rem; margin: 10px 0 0 0;">ยินดีด้วยกับสโมสร <b>{champ_name}</b> คว้าแชมป์พรีเมียร์ลีกฤดูกาลนี้อย่างเป็นทางการ!</p></div><script>var duration = 5 * 1000; var end = Date.now() + duration; (function frame() {{ confetti({{ particleCount: 5, angle: 60, spread: 55, origin: {{ x: 0, y: 0.8 }} }}); confetti({{ particleCount: 5, angle: 120, spread: 55, origin: {{ x: 1, y: 0.8 }} }}); if (Date.now() < end) {{ requestAnimationFrame(frame); }} }}());</script>""", height=150)
            
            html_table = """<table class="lfc-table"><tr><th>อันดับ</th><th class="left">สโมสร</th><th>แข่ง</th><th>ชนะ</th><th>เสมอ</th><th>แพ้</th><th>ได้-เสีย</th><th>+/-</th><th style="color:#eab308;">แต้ม</th></tr>"""
            for r in table_data:
                row_style = 'style="background: linear-gradient(90deg, rgba(234,179,8,0.15) 0%, rgba(0,0,0,0) 100%); font-weight: bold; border-left: 5px solid #eab308;"' if r["rank"] == 1 else ''
                rank_badge = '<span style="background:#eab308; color:#000; padding:2px 6px; border-radius:4px; font-size:0.85rem; font-weight:bold;">1 🥇</span>' if r["rank"] == 1 else f'<span>{r["rank"]}</span>'
                logo_html = f'<img src="{r["team"]["logo"]}" width="22" style="margin-right:8px; vertical-align:middle; max-height:22px;">' if r["team"]["logo"] else ""
                html_table += f"""<tr {row_style}><td>{rank_badge}</td><td class="left" style="font-weight:600;">{logo_html}{r["team"]["name"]}</td><td>{r["all"]["played"]}</td><td>{r["all"]["win"]}</td><td>{r["all"]["draw"]}</td><td>{r["all"]["lose"]}</td><td style="color:#64748b; font-size:0.85rem;">{r["all"]["goals"]["for"]}:{r["all"]["goals"]["against"]}</td><td style="color:{'#16a34a' if r["goalsDiff"] >= 0 else '#dc2626'}">{'+' if r["goalsDiff"] > 0 else ''}{r["goalsDiff"]}</td><td style="color:#eab308; font-weight:bold;">{r["points"]}</td></tr>"""
            html_table += "</table>"
            st.markdown(html_table, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with col_side:
    live_fix = fetch_live_fixture()
    if live_fix:
        st.markdown('<div class="card" style="border: 1px solid #16a34a; background-color: rgba(22,163,74,0.05);">', unsafe_allow_html=True)
        st.markdown('<div class="card-title" style="color:#16a34a; border-left-color:#16a34a;">🔴 LIVE MATCH NOW</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; padding:0.5rem 0;"><div style="font-size:1.1rem; font-weight:600;">{live_fix["teams"]["home"]["name"]} vs {live_fix["teams"]["away"]["name"]}</div><div style="font-size:2.5rem; font-weight:700; color:#16a34a;">{live_fix["goals"]["home"]} - {live_fix["goals"]["away"]}</div><span class="badge" style="background-color:#16a34a;">กำลังแข่งขัน</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    next_fix = fetch_next_fixture()
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📅 โปรแกรมนัดถัดไป</div>', unsafe_allow_html=True)
    if next_fix:
        st.markdown(f'<div style="font-size:0.85rem; color:#64748b; font-weight:600;">🏆 {COMPETITIONS.get(next_fix["league"]["id"], next_fix["league"]["name"])}</div><div style="font-size:1.1rem; font-weight:600;">{next_fix["teams"]["home"]["name"]} vs {next_fix["teams"]["away"]["name"]}</div><div style="font-size:0.9rem;">⏰ {fmt_date(next_fix["fixture"]["date"])}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    last_fixtures = fetch_last_fixtures(5)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🕒 ผลการแข่งขัน 5 นัดหลังสุด</div>', unsafe_allow_html=True)
    if last_fixtures:
        for fx in last_fixtures:
            badge_txt, badge_color = result_badge(fx["goals"]["home"], fx["goals"]["away"], fx["teams"]["home"]["id"])
            st.markdown(f'<div style="display:flex; align-items:center; justify-content:between; margin-bottom:0.75rem; font-size:0.9rem;"><div style="flex:1;"><div>🏆 {COMPETITIONS.get(fx["league"]["id"], fx["league"]["name"])}</div><div style="font-weight:600;">{fx["teams"]["home"]["name"]} {fx["goals"]["home"]}-{fx["goals"]["away"]} {fx["teams"]["away"]["name"]}</div></div><div><span class="badge" style="background-color:{badge_color};">{badge_txt}</span></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── POLLING ENGINE & COMMENTS ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">🗳️ โพลล์แฟนบอล: {POLL_QUESTION}</div>', unsafe_allow_html=True)
    if "comments" not in st.session_state:
        st.session_state.comments = fetch_comments()
    agree_count = sum(1 for c in st.session_state.comments if c["text"] == AGREE_TEXT)
    disagree_count = sum(1 for c in st.session_state.comments if c["text"] == DISAGREE_TEXT)
    total_votes = agree_count + disagree_count
    if total_votes > 0:
        pct_agree = int((agree_count / total_votes) * 100)
        st.markdown(f'<div style="margin-bottom:1rem; font-size:0.9rem;"><div style="display:flex; justify-content:between;"><span>🔴 ดื้อ ({agree_count})</span><span>⚪ ให้โอกาส ({disagree_count})</span></div><div style="display:flex; width:100%; height:12px; border-radius:6px; background-color:#334155; overflow:hidden;"><div style="width:{pct_agree}%; background-color:#C8102E;"></div></div></div>', unsafe_allow_html=True)

    username = st.text_input("💬 ชื่อเล่นของคุณ :", placeholder="เช่น บังโมเมืองนนท์", max_chars=20)
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        if st.button("🔴 ดื้อเกินไปจริง!", key="agree_btn", use_container_width=True):
            if push_comment(username.strip() or f"Fan_{random.randint(1,999)}", AGREE_TEXT, border=True):
                st.session_state.comments = fetch_comments()
                st.rerun()
    with col_v2:
        if st.button("⚪ ให้โอกาสไปก่อน", key="disagree_btn", use_container_width=True):
            if push_comment(username.strip() or f"Fan_{random.randint(1,999)}", DISAGREE_TEXT):
                st.session_state.comments = fetch_comments()
                st.rerun()

    custom_comment = st.text_input("✍️ พิมพ์ข้อความแสดงความเห็นเพิ่มเติม :", placeholder="ใส่ความคิดเห็นหลังเกมของคุณที่นี่...", max_chars=100)
    if st.button("🚀 ส่งความเห็น", key="custom_msg_btn", use_container_width=True):
        if custom_comment.strip():
            if push_comment(username.strip() or f"Fan_{random.randint(1,999)}", custom_comment.strip(), border=False):
                st.session_state.comments = fetch_comments()
                st.rerun()

    if st.session_state.comments:
        for c in st.session_state.comments[:10]:
            border_cls = 'style="border-left: 4px solid #C8102E;"' if c["border"] == "True" else ""
            st.markdown(f'<div class="comment-item" {border_cls}><div class="comment-user">{c["user"]} <span class="comment-time">🕒 {c["ts"]}</span></div><div class="comment-text">{c["text"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ──
st.markdown('<div class="lfc-footer"><div class="footer-credit">© 2026 JamesPok LFC Dashboard. All Rights Reserved.</div></div>', unsafe_allow_html=True)
