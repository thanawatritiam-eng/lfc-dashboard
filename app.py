import streamlit as st

# --- 1. CONFIG ---
st.set_page_config(page_title="เจมส์ป๊อก LFC - ขยี้ทุกประเด็นหงส์แดง", layout="wide")

# --- 2. THE MASTER HTML & CSS (ดึงจาก newslfc.html มา 100%) ---
# ผมใช้สไตล์จากไฟล์ที่คุณส่งมา ทั้งสี #C8102E และ #F6EB61

st.markdown("""
    <style>
    /* บังคับลบ Padding ของ Streamlit ออกให้หมดเพื่อให้เหมือนหน้าเว็บจริง */
    .block-container { padding: 0 !important; max-width: 100% !important; }
    iframe { display: block; }
    footer {visibility: hidden;}
    header {visibility: hidden;}

    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap');
    
    .main-body {
        font-family: 'Noto Sans Thai', sans-serif;
        background-color: #f8fafc;
        color: #1e293b;
        margin: 0;
        padding-bottom: 50px;
    }

    /* Header: แดงเข้ม ตัวหนังสือทองขาว [ตามสั่งเป๊ะ] */
    .header-section {
        background-color: #C8102E;
        color: #ffffff;
        padding: 40px 20px;
        text-align: center;
        border-bottom: 8px solid #F6EB61; /* เส้นทองล่าง Header */
    }
    .header-section h1 { color: #ffffff !important; font-size: 3rem; font-weight: 800; margin: 0; }
    .header-section p { color: #F6EB61 !important; font-size: 1.2rem; margin-top: 10px; }

    /* Container สถิติ */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        padding: 20px;
        max-width: 1200px;
        margin: -30px auto 0 auto; /* ยกขึ้นไปทับ Header นิดๆ ให้ดูล้ำ */
    }

    .stat-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-top: 5px solid #C8102E;
    }
    .stat-card h4 { color: #64748b; margin: 0; font-size: 1rem; }
    .stat-card h2 { color: #1e293b; font-size: 2rem; font-weight: 800; margin: 10px 0; }

    /* คอนเทนเนอร์เนื้อหา พื้นหลังดำ-ตัวหนังสือทอง [ตามสั่ง] */
    .content-dark {
        background-color: #1e293b;
        color: #F6EB61;
        padding: 30px;
        border-radius: 15px;
        margin: 20px auto;
        max-width: 1160px;
    }
    .content-dark h3 { color: #ffffff !important; border-bottom: 2px solid #C8102E; padding-bottom: 10px; }

    /* คอนเทนเนอร์เนื้อหา พื้นหลังขาว-ตัวหนังสือดำ [ตามสั่ง] */
    .content-light {
        background-color: #ffffff;
        color: #1e293b;
        padding: 30px;
        border-radius: 15px;
        margin: 20px auto;
        max-width: 1160px;
        border-left: 8px solid #C8102E;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>

    <div class="main-body">
        <div class="header-section">
            <h1>🔴 เจมส์ป๊อก LFC</h1>
            <p>วิเคราะห์เจาะลึกประเด็นหงส์แดงแบบ "โต๊ะรก" - ขยี้ทุกสถิติ</p>
        </div>

        <div class="stats-container">
            <div class="stat-card">
                <h4>ผลการแข่งขัน</h4>
                <h2>1 - 1</h2>
            </div>
            <div class="stat-card">
                <h4>ครองบอล</h4>
                <h2 style="color: #C8102E;">42%</h2>
            </div>
            <div class="stat-card">
                <h4>โอกาสยิง (เข้ากรอบ)</h4>
                <h2>11 (4)</h2>
            </div>
            <div class="stat-card">
                <h4>คะแนนความล้ำ</h4>
                <h2 style="color: #f59e0b;">9.5</h2>
            </div>
        </div>

        <div class="content-dark">
            <h3>🔥 ประเด็นร้อน: นาทีที่ 67 เปลี่ยนเกม!</h3>
            <p>ในช่วงที่เกมกำลังสูสี สล็อตตัดสินใจถอด "อึงูโมฮา" ออก ซึ่งส่งผลต่อโมเมนตัมของทีมอย่างมหาศาล 
            นี่คือจุดเปลี่ยนที่ทำให้เชลซีเริ่มครองเกมได้มากขึ้น และเป็นบทเรียนสำคัญสำหรับการจัดตัวในนัดถัดไป</p>
        </div>

        <div class="content-light">
            <h3 style="color: #C8102E;">🧠 วิเคราะห์หลังเกม (Tactical Insight)</h3>
            <p>ลิเวอร์พูลใช้แผนการเล่นที่เน้นการบีบพื้นที่สูง แต่ความผิดพลาดในแดนกลางช่วงนาทีสุดท้ายเกือบทำให้ทีมต้องเสียแต้ม 
            สิ่งที่ต้องชมคือความมุ่งมั่นของแนวรับที่ยังช่วยกันประคองจนจบเกมด้วยผลเสมอ</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 3. STREAMLIT INTERACTIVE (ส่วนที่ทำให้เว็บทำงานได้) ---
# ส่วนนี้เราใช้ฟีเจอร์ของ Streamlit แทรกลงไปใต้ HTML เพื่อให้คนโหวตได้
st.markdown("<div style='max-width:1160px; margin:auto; padding:0 20px;'>", unsafe_allow_html=True)
st.subheader("🗳️ แฟนบอลคิดอย่างไร?")
vote = st.selectbox("นัดหน้าควรเปลี่ยนแผนหรือไม่?", ["ควรเปลี่ยน (เน้นเกมรับ)", "คงเดิม (บุกแหลก)", "ปรับบางตำแหน่ง"])
if st.button("ส่งคะแนนโหวต"):
    st.balloons()
    st.success("ขอบคุณสำหรับข้อมูล! เราจะนำไปขยี้ต่อในคลิปหน้า")
st.markdown("</div>", unsafe_allow_html=True)
