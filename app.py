<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>เจมส์ป๊อก LFC - ขยี้ทุกประเด็นหงส์แดง</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Font -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Noto Sans Thai', sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
        }

        /* === Liverpool Brand Colors === */
        .bg-liverpool-red { background-color: #C8102E; }
        .text-liverpool-red { color: #C8102E; }
        .border-liverpool-red { border-color: #C8102E; }
        .bg-liverpool-gold { background-color: #F6EB61; }
        .text-liverpool-gold { color: #F6EB61; }

        /* === Chart === */
        .chart-container {
            position: relative;
            width: 100%;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
            height: 350px;
            max-height: 400px;
        }
        @media (min-width: 768px) {
            .chart-container { height: 400px; }
        }

        /* === Tab Sections === */
        .section-hidden { display: none; }
        .section-active { display: block; animation: fadeIn 0.5s ease-in-out; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* === Stat Card Hover === */
        .stat-card {
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }

        /* =====================================================
           COLOR CONTRAST FIXES — สีฟอนต์ต้องตัดกับพื้นหลัง
           ===================================================== */

        /* Header (แดง) → ตัวอักษรขาว */
        header { color: #ffffff; }
        header h1 { color: #ffffff; }
        header p.text-liverpool-gold { color: #F6EB61; }   /* ทอง บน แดง → OK */
        header .nav-btn { color: #ffffff; }

        /* Mobile menu (red-800) → ตัวอักษรขาว */
        #mobile-menu button { color: #ffffff; }

        /* Logo circle: พื้นขาว → ตัวอักษรแดง */
        .logo-circle { color: #C8102E; background-color: #ffffff; }

        /* --- Section 1: ประเด็นร้อน --- */

        /* กล่องผลการแข่งขัน: bg-gray-50 (อ่อน) → สีเข้ม */
        .score-box { background-color: #f1f5f9; }
        .score-box .team-liv { color: #b91c1c; }   /* แดงเข้ม บน เทาอ่อน */
        .score-box .team-che { color: #1d4ed8; }   /* น้ำเงินเข้ม บน เทาอ่อน */
        .score-box .score-num { color: #0f172a; }  /* ดำ บน เทาอ่อน */
        .score-box .vs-text { color: #64748b; }    /* เทากลาง บน เทาอ่อน */

        /* Timeline นาที: bg ขาว → ตัวอักษรเทาเข้ม */
        .timeline-min { color: #475569; }          /* slate-600 บน ขาว */
        .timeline-goal-liv { color: #b91c1c; }     /* แดงเข้ม บน ขาว */
        .timeline-goal-che { color: #1d4ed8; }     /* น้ำเงินเข้ม บน ขาว */
        .timeline-event { color: #1e293b; }        /* slate-800 บน ขาว */
        .timeline-desc { color: #334155; }         /* slate-700 บน ขาว */

        /* การ์ด Slot Quote: bg-white → ข้อความเข้ม */
        .card-slot blockquote { color: #1e293b; font-style: italic; }
        .card-slot .card-label { color: #b91c1c; }
        .card-slot .card-note { color: #475569; }
        .card-slot .card-note strong { color: #1e293b; }

        /* การ์ด Salah: bg-red-50 → ข้อความต้องเข้มพอ */
        .card-salah { background-color: #fef2f2; border-color: #C8102E; }
        .card-salah .card-label { color: #b91c1c; }
        .card-salah blockquote { color: #0f172a; }       /* ดำสนิท บน ชมพูอ่อน */
        .card-salah .card-note { color: #374151; }
        .card-salah .card-note strong { color: #111827; }

        /* การ์ด Gravenberch: bg-white */
        .card-grav .card-label { color: #475569; }
        .card-grav .card-quote { color: #1e293b; font-weight: 600; }
        .card-grav .card-desc { color: #475569; }

        /* Romano Box: bg-slate-800 (เข้ม) → ตัวอักษรอ่อน */
        .romano-box { background-color: #1e293b; color: #e2e8f0; }   /* slate-200 บน slate-800 */
        .romano-box h4 { color: #F6EB61; }        /* ทอง บน เข้ม */
        .romano-box p { color: #cbd5e1; }         /* slate-300 บน slate-800 */
        .romano-box strong { color: #ffffff; }    /* ขาว บน เข้ม */

        /* --- Section 2: สถิติ --- */

        /* stat cards */
        .stat-card-red { background-color: #fef2f2; border-color: #fecaca; }
        .stat-card-red .stat-num { color: #b91c1c; }      /* แดงเข้ม บน ชมพูอ่อน */
        .stat-card-red .stat-label { color: #374151; }

        .stat-card-blue { background-color: #eff6ff; border-color: #bfdbfe; }
        .stat-card-blue .stat-num { color: #1d4ed8; }     /* น้ำเงินเข้ม บน ฟ้าอ่อน */
        .stat-card-blue .stat-label { color: #374151; }

        .stat-card-gray { background-color: #f8fafc; border-color: #e2e8f0; }
        .stat-card-gray .stat-num { color: #0f172a; }     /* ดำ บน เทาอ่อน */
        .stat-card-gray .stat-label { color: #374151; }

        /* Player Spotlight: bg-white border-gold */
        .spotlight-card h3 { color: #1e293b; }
        .spotlight-card p { color: #374151; }
        .spotlight-card .stat-label { color: #475569; }
        .spotlight-card .stat-value { color: #1e293b; }
        .spotlight-card .note-text { color: #64748b; }

        /* --- Section 3: วิเคราะห์ --- */

        /* Editor card: bg-white border-top-red */
        .editor-card h3 { color: #0f172a; }
        .editor-card p { color: #374151; }
        .editor-card p.highlight { color: #1e293b; font-weight: 600; }

        /* Comparison dark box: bg gradient red-900 to black → อ่อน */
        .compare-box { background: linear-gradient(to bottom right, #7f1d1d, #000000); }
        .compare-box h3 { color: #F6EB61; }         /* ทอง บน แดงเข้ม/ดำ */
        .compare-box p { color: #e2e8f0; }          /* slate-200 บน เข้ม */
        .compare-box .team-name { color: #ffffff; }
        .compare-box .team-desc-red { color: #fca5a5; }   /* แดงอ่อน (300) บน เข้ม → ตัดชัด */
        .compare-box .team-desc-mun { color: #94a3b8; }   /* slate-400 บน เข้ม */
        .compare-box .vs-label { color: #e2e8f0; }

        /* Comment area: bg-gray-50 → ข้อความเข้ม */
        .comment-area { background-color: #f1f5f9; border-color: #e2e8f0; }
        .comment-area h4 { color: #0f172a; }
        .comment-white { background-color: #ffffff; color: #1e293b; }
        .comment-white .commenter-kopite { color: #1d4ed8; }    /* น้ำเงิน บน ขาว */
        .comment-white .commenter-james { color: #1e293b; }
        .comment-text { color: #374151; }

        /* Section headings (บนพื้น f8fafc): ดำ/เข้ม */
        .section-heading { color: #0f172a; }
        .section-sub { color: #475569; }

        /* Footer: bg-gray-900 → ตัวอักษรอ่อน */
        footer { background-color: #111827; }
        footer .footer-title { color: #ffffff; }
        footer .footer-ref { color: #9ca3af; }
        footer .footer-copy { color: #6b7280; }

        /* Inline text helpers ที่อาจมีปัญหา */
        .text-gray-900-safe { color: #0f172a !important; }
        .text-gray-700-safe { color: #374151 !important; }
        .text-gray-600-safe { color: #4b5563 !important; }
        .text-gray-500-safe { color: #6b7280 !important; }
    </style>
</head>
<body class="antialiased min-h-screen flex flex-col">

    <!-- Header / Branding -->
    <header class="bg-liverpool-red shadow-md sticky top-0 z-50">
        <div class="container mx-auto px-4 py-4 flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <!-- Logo: พื้นขาว / ตัวอักษรแดง -->
                <div class="logo-circle w-10 h-10 rounded-full flex items-center justify-center font-bold text-xl border-2 border-yellow-300">
                    JP
                </div>
                <div>
                    <h1 class="text-2xl font-extrabold uppercase tracking-wider" style="color:#ffffff;">เจมส์ป๊อก LFC</h1>
                    <p class="text-xs font-semibold uppercase tracking-widest text-liverpool-gold">ขยี้ทุกประเด็นหงส์แดง</p>
                </div>
            </div>
            <nav class="hidden md:flex space-x-6">
                <button onclick="switchTab('hot-topics')" id="nav-hot-topics"
                    class="nav-btn font-semibold hover:text-yellow-300 transition-colors border-b-2 border-white pb-1"
                    style="color:#ffffff;">ประเด็นร้อน (Chelsea 1-1)</button>
                <button onclick="switchTab('match-stats')" id="nav-match-stats"
                    class="nav-btn font-semibold hover:text-yellow-300 transition-colors border-b-2 border-transparent pb-1"
                    style="color:#ffffff;">เจาะสถิติ</button>
                <button onclick="switchTab('analysis')" id="nav-analysis"
                    class="nav-btn font-semibold hover:text-yellow-300 transition-colors border-b-2 border-transparent pb-1"
                    style="color:#ffffff;">วิเคราะห์สไตล์โต๊ะรก</button>
            </nav>
            <!-- Mobile Menu Button -->
            <button class="md:hidden focus:outline-none" style="color:#ffffff;"
                onclick="document.getElementById('mobile-menu').classList.toggle('hidden')">
                <span class="text-2xl">☰</span>
            </button>
        </div>
        <!-- Mobile Menu: พื้น red-800 → ตัวอักษรขาว -->
        <div id="mobile-menu" class="hidden md:hidden pb-4" style="background-color:#991b1b;">
            <button onclick="switchTab('hot-topics'); document.getElementById('mobile-menu').classList.add('hidden')"
                class="block w-full text-left px-4 py-2 hover:bg-red-700" style="color:#ffffff;">ประเด็นร้อน</button>
            <button onclick="switchTab('match-stats'); document.getElementById('mobile-menu').classList.add('hidden')"
                class="block w-full text-left px-4 py-2 hover:bg-red-700" style="color:#ffffff;">เจาะสถิติ</button>
            <button onclick="switchTab('analysis'); document.getElementById('mobile-menu').classList.add('hidden')"
                class="block w-full text-left px-4 py-2 hover:bg-red-700" style="color:#ffffff;">วิเคราะห์สไตล์โต๊ะรก</button>
        </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-grow container mx-auto px-4 py-8">

        <!-- ===================================================
             SECTION 1: ประเด็นร้อน (Hot Topics)
             =================================================== -->
        <section id="hot-topics" class="section-active">
            <div class="mb-8 text-center">
                <h2 class="text-4xl font-bold mb-4 uppercase tracking-tight section-heading">หงส์สะดุดอีก! เสียงโห่ลั่นแอนฟิลด์</h2>
                <p class="text-xl max-w-3xl mx-auto section-sub">ควันหลงและดราม่าหลังเกมที่เครื่องจักรสีแดงทำได้แค่เปิดบ้านเสมอ เชลซี 1-1 สรุปเหตุการณ์สำคัญและระเบิดลูกใหญ่จากนักเตะ</p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

                <!-- Match Result & Timeline -->
                <div class="lg:col-span-1 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                    <h3 class="text-xl font-bold border-b-2 border-liverpool-red pb-2 mb-4 inline-block" style="color:#0f172a;">ผลการแข่งขัน &amp; ไทม์ไลน์</h3>

                    <!-- Score Box: พื้นเทาอ่อน → ตัวอักษรเข้ม -->
                    <div class="score-box flex justify-between items-center p-4 rounded-lg mb-6">
                        <div class="text-center">
                            <span class="block font-bold text-lg team-liv">LIV</span>
                            <span class="text-3xl font-black score-num">1</span>
                        </div>
                        <div class="vs-text font-bold text-xl">VS</div>
                        <div class="text-center">
                            <span class="block font-bold text-lg team-che">CHE</span>
                            <span class="text-3xl font-black score-num">1</span>
                        </div>
                    </div>

                    <!-- Timeline -->
                    <div class="space-y-4">
                        <!-- Goal LFC -->
                        <div class="flex">
                            <div class="w-12 text-sm font-bold pt-1 timeline-min">6'</div>
                            <div class="flex-1 border-l-2 border-liverpool-red pl-4 pb-4">
                                <span class="timeline-goal-liv text-xl font-black leading-none block mb-1">GOAL! (LIV)</span>
                                <p class="text-sm timeline-desc">ริโอ อึงูโมฮา ไหลบอลให้ <strong style="color:#0f172a;">ไรอัน กราเฟนแบร์ก</strong> ปั่นโค้งสุดสวย หงส์ขึ้นนำ!</p>
                            </div>
                        </div>
                        <!-- Goal CHE -->
                        <div class="flex">
                            <div class="w-12 text-sm font-bold pt-1 timeline-min">35'</div>
                            <div class="flex-1 border-l-2 border-blue-600 pl-4 pb-4">
                                <span class="timeline-goal-che text-xl font-black leading-none block mb-1">GOAL! (CHE)</span>
                                <p class="text-sm timeline-desc"><strong style="color:#0f172a;">เอ็นโซ เฟร์นานเดซ</strong> ปั่นฟรีคิกแฉลบเข้าประตู สิงห์บลูส์ตีเสมอ</p>
                            </div>
                        </div>
                        <!-- Drama -->
                        <div class="flex">
                            <div class="w-12 text-sm font-bold pt-1 timeline-min">67'</div>
                            <div class="flex-1 border-l-2 border-gray-300 pl-4 pb-4">
                                <span class="text-lg font-bold leading-none block mb-1 timeline-event">จุดเปลี่ยน &amp; ดราม่า</span>
                                <p class="text-sm timeline-desc">สล็อตถอด <strong style="color:#0f172a;">อึงูโมฮา</strong> ที่กำลังเล่นดีออก แฟนบอลในแอนฟิลด์เริ่มส่งเสียงโห่</p>
                            </div>
                        </div>
                        <!-- FT -->
                        <div class="flex">
                            <div class="w-12 text-sm font-bold pt-1 timeline-min">FT</div>
                            <div class="flex-1 border-l-2 border-gray-300 pl-4">
                                <span class="font-bold block timeline-event">จบเกม เสมอ 1-1</span>
                                <p class="text-sm" style="color:#64748b;">โซบอสซ์ไลยิงชนเสา ฟาน ไดจ์คโหม่งชนคาน เจาะไม่เข้า</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- The Drama -->
                <div class="lg:col-span-2 space-y-6">
                    <h3 class="text-2xl font-bold border-l-4 border-liverpool-red pl-3" style="color:#0f172a;">ประเด็นเดือดหลังเกม</h3>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <!-- Slot Quote: bg-white -->
                        <div class="card-slot bg-white p-6 rounded-xl shadow-sm border border-gray-100 relative overflow-hidden">
                            <div class="absolute top-0 right-0 w-16 h-16 bg-gray-100 rounded-bl-full -mr-8 -mt-8"></div>
                            <span class="card-label text-xs font-bold uppercase tracking-wider mb-2 block">อาร์เน่อ สล็อต</span>
                            <blockquote class="text-lg mb-4" style="font-style:italic; color:#1e293b;">
                                "พวกคุณคิดจริงๆ เหรอว่าผมสั่งให้ทีมถอยไปรับ? นี่คุณเห็นผมตะโกนสั่งข้างสนามว่า 'ถอยไปเดี๋ยวนี้! กลับไปเฝ้าเขตโทษตัวเอง' หรือไง?"
                            </blockquote>
                            <p class="text-sm" style="color:#475569;"><strong style="color:#1e293b;">เจมส์ป๊อกขยี้:</strong> กุนซือหงส์แดงตอบคำถามแบบติดประชดหลังโดนวิจารณ์เรื่องแทคติกครึ่งหลังที่ดูถอยไปตั้งรับมากเกินไป</p>
                        </div>

                        <!-- Salah Bomb: bg-red-50 → ต้องให้ข้อความเข้มพอ -->
                        <div class="card-salah p-6 rounded-xl shadow-sm relative overflow-hidden">
                            <div class="absolute top-0 right-0 w-16 h-16 rounded-bl-full -mr-8 -mt-8" style="background-color:#fecaca;"></div>
                            <span class="card-label text-xs font-bold uppercase tracking-wider mb-2 block animate-pulse">ระเบิดจากซาลาห์!</span>
                            <blockquote class="text-lg font-bold mb-4" style="color:#0f172a;">"ทีมชุดนี้ ขาดผู้นำ"</blockquote>
                            <p class="text-sm" style="color:#374151;"><strong style="color:#111827;">รายงานจาก Paul Gorst (Tier 1):</strong> โม ซาลาห์ ให้สัมภาษณ์แทงใจดำ ทำเอาสล็อตหัวเสียสุดๆ บ่งบอกถึงรอยร้าวในแคมป์</p>
                        </div>

                        <!-- Gravenberch Quote: bg-white -->
                        <div class="card-grav bg-white p-6 rounded-xl shadow-sm border border-gray-100 md:col-span-2">
                            <div class="flex flex-col sm:flex-row items-center gap-4">
                                <div class="text-4xl">🗣️</div>
                                <div>
                                    <span class="text-xs font-bold uppercase tracking-wider block card-label" style="color:#475569;">ไรอัน กราเฟนแบร์ก ตัดพ้อแฟนบอล</span>
                                    <p class="font-semibold mt-1" style="color:#1e293b;">"พวกเราไม่สมควรได้รับมัน (เสียงโห่)"</p>
                                    <p class="text-sm mt-1" style="color:#475569;">ผู้ทำประตูขึ้นนำออกมาปกป้องทีม หลังจากแฟนบอลในแอนฟิลด์ส่งเสียงโห่หลังจบเกมและจังหวะเปลี่ยนตัว</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Romano Box: bg-slate-800 → ตัวอักษรอ่อน -->
                    <div class="romano-box p-6 rounded-xl shadow-md mt-6 flex items-start gap-4">
                        <div class="text-3xl">📰</div>
                        <div>
                            <h4 class="font-bold mb-1" style="color:#F6EB61;">Fabrizio Romano Update</h4>
                            <p class="text-sm" style="color:#cbd5e1;">บอร์ดบริหารลิเวอร์พูลยังคง <strong style="color:#ffffff;">"หนุนหลัง"</strong> อาร์เน่อ สล็อต อย่างเต็มที่ ข่าวลือเรื่องการติดต่อ ชาบี อลอนโซ่ ไม่เป็นความจริง สล็อตยังได้ไปต่อ!</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- ===================================================
             SECTION 2: สถิติหลังเกม (Match Stats)
             =================================================== -->
        <section id="match-stats" class="section-hidden">
            <div class="mb-8 text-center">
                <h2 class="text-4xl font-bold mb-4 uppercase tracking-tight section-heading">เจาะสถิติ ฟ้องด้วยตัวเลข</h2>
                <p class="text-xl max-w-3xl mx-auto section-sub">สถิติจากเกมนี้บอกอะไรเรา? ลิเวอร์พูลถอยไปรับจริง หรือแค่เจาะเชลซีไม่เข้า มาดูตัวเลขเปรียบเทียบกัน</p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <!-- Main Comparison Chart -->
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 class="text-xl font-bold mb-6 text-center" style="color:#0f172a;">สถิติภาพรวมเกมรุกและรับ</h3>
                    <div class="chart-container">
                        <canvas id="matchStatsChart"></canvas>
                    </div>
                </div>

                <!-- Player Focus & Quick Stats -->
                <div class="space-y-6">
                    <!-- Quick Stats Cards -->
                    <div class="grid grid-cols-2 gap-4">
                        <!-- LFC shots: พื้นชมพูอ่อน → แดงเข้ม -->
                        <div class="stat-card stat-card-red p-4 rounded-xl border text-center">
                            <span class="block text-3xl font-black mb-1 stat-num" style="color:#b91c1c;">11</span>
                            <span class="text-xs font-bold uppercase tracking-wider stat-label" style="color:#374151;">โอกาสยิง (ลิเวอร์พูล)</span>
                        </div>
                        <!-- CHE shots: พื้นฟ้าอ่อน → น้ำเงินเข้ม -->
                        <div class="stat-card stat-card-blue p-4 rounded-xl border text-center">
                            <span class="block text-3xl font-black mb-1 stat-num" style="color:#1d4ed8;">14</span>
                            <span class="text-xs font-bold uppercase tracking-wider stat-label" style="color:#374151;">โอกาสยิง (เชลซี)</span>
                        </div>
                        <!-- Woodwork: พื้นเทาอ่อน → ดำ -->
                        <div class="stat-card stat-card-gray p-4 rounded-xl border text-center col-span-2">
                            <span class="block text-2xl font-black mb-1 stat-num" style="color:#0f172a;">2 ครั้ง</span>
                            <span class="text-xs font-bold uppercase tracking-wider stat-label" style="color:#374151;">ยิงชนเสา/คาน (โซบอสซ์ไล, ฟาน ไดจ์ค)</span>
                        </div>
                    </div>

                    <!-- Player Spotlight: bg-white border-gold -->
                    <div class="spotlight-card bg-white p-6 rounded-xl shadow-sm border border-yellow-400">
                        <h3 class="text-lg font-bold mb-4 flex items-center gap-2" style="color:#1e293b;">
                            <span class="text-xl">🌟</span> Spotlight: ริโอ อึงูโมฮา (17 ปี)
                        </h3>
                        <p class="text-sm mb-4" style="color:#374151;">ดาวรุ่งที่โชว์ฟอร์มได้โดดเด่นที่สุดในแนวรุก ก่อนถูกเปลี่ยนตัวออกจนเกิดเสียงโห่</p>

                        <div class="space-y-3">
                            <div class="flex justify-between items-end">
                                <span class="text-sm font-semibold" style="color:#374151;">เลี้ยงผ่านคู่แข่ง (สูงสุดในทีม)</span>
                                <span class="font-bold text-lg" style="color:#1e293b;">4/5 ครั้ง</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="bg-liverpool-red h-2 rounded-full" style="width: 80%"></div>
                            </div>

                            <div class="flex justify-between items-end mt-4">
                                <span class="text-sm font-semibold" style="color:#374151;">แอสซิสต์</span>
                                <span class="font-bold text-lg" style="color:#1e293b;">1</span>
                            </div>
                        </div>
                        <p class="text-xs mt-4 italic" style="color:#64748b;">*สล็อตอ้างว่าเปลี่ยนออกเพราะนักเตะมีอาการตะคริว</p>
                    </div>
                </div>
            </div>

            <!-- Timeline / Momentum Chart -->
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h3 class="text-xl font-bold mb-6 text-center" style="color:#0f172a;">โมเมนตัมการบุก (จำลอง)</h3>
                <p class="text-sm text-center mb-4" style="color:#64748b;">กราฟแสดงความกดดันในแต่ละช่วงเวลา (บวก = หงส์บุก, ลบ = สิงห์บุก)</p>
                <div class="chart-container h-64 md:h-80">
                    <canvas id="momentumChart"></canvas>
                </div>
            </div>
        </section>

        <!-- ===================================================
             SECTION 3: วิเคราะห์สไตล์โต๊ะรก (Analysis)
             =================================================== -->
        <section id="analysis" class="section-hidden">
            <div class="mb-8 text-center">
                <h2 class="text-4xl font-bold mb-4 uppercase tracking-tight section-heading">โต๊ะรก วิจารณ์</h2>
                <p class="text-xl max-w-3xl mx-auto section-sub">ถึงเวลาตบขมับ! วิเคราะห์เจาะลึกแบบไม่เกรงใจใคร สไตล์ เจมส์ป๊อก LFC</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <!-- Editor's Take: bg-white, border-top-red -->
                <div class="editor-card bg-white p-8 rounded-xl shadow-sm border-t-4 border-liverpool-red">
                    <h3 class="text-2xl font-black mb-4" style="color:#0f172a;">ถอด อึงูโมฮา... แทคติก หรือ พลาด?</h3>
                    <p class="leading-relaxed mb-4" style="color:#374151;">
                        เกมนี้ของกำลังมาแท้ๆ ไอ้หนู ริโอ เลื้อยจนแนวรับเชลซีหัวหมุน แต่สล็อตดันเลือกถอดออกนาที 67 แล้วส่ง อิซัค ลงมาแทน!
                        เข้าใจว่าอ้างเรื่องตะคริว แต่พอเปลี่ยนปุ๊บ เกมรุกฝั่งซ้ายบอดสนิททันที กลายเป็นว่าเราเสียโมเมนตัมไปดื้อๆ
                    </p>
                    <p class="leading-relaxed font-semibold" style="color:#1e293b;">
                        "การสัมภาษณ์หลังเกมที่สล็อตตอบแบบประชดนักข่าว ยิ่งทำให้เห็นว่าเขากำลังกดดัน และไม่พร้อมรับเสียงวิจารณ์ นี่แหละที่ทำให้เก้าอี้เริ่มร้อน!"
                    </p>
                </div>

                <!-- Right Column -->
                <div class="flex flex-col justify-between">
                    <!-- Comparison Box: พื้นเข้ม → ตัวอักษรอ่อน -->
                    <div class="compare-box p-8 rounded-xl shadow-lg mb-6">
                        <h3 class="text-xl font-bold mb-4" style="color:#F6EB61;">เปรียบเทียบคู่แค้น</h3>
                        <p class="mb-4" style="color:#e2e8f0;">แมนฯ ยูไนเต็ด เพิ่งเอาชนะเราไป 3-2 เมื่อเร็วๆ นี้... ลองมองภาพรวมตอนนี้</p>
                        <div class="flex justify-between items-center text-center">
                            <div>
                                <span class="block text-2xl font-black" style="color:#ffffff;">LIV</span>
                                <span class="text-sm" style="color:#fca5a5;">ทรงบอลอึดอัด โค้ชมีปัญหากับแฟน</span>
                            </div>
                            <div class="text-xl font-bold" style="color:#e2e8f0;">VS</div>
                            <div>
                                <span class="block text-2xl font-black" style="color:#ef4444;">MUN</span>
                                <span class="text-sm" style="color:#94a3b8;">ชนะบิ๊กแมตช์ โมเมนตัมกำลังมา?</span>
                            </div>
                        </div>
                    </div>

                    <!-- Mock Comment Section: bg-gray-50 → ข้อความเข้ม -->
                    <div class="bg-gray-50 p-6 rounded-xl border border-gray-200">
                        <h4 class="font-bold mb-4" style="color:#0f172a;">เพื่อนๆ คิดยังไง? (จำลองคอมเมนต์)</h4>

                        <div class="flex gap-2 mb-4">
                            <button onclick="addMockComment('agree')"
                                class="bg-liverpool-red hover:bg-red-800 px-4 py-2 rounded text-sm font-bold transition-colors"
                                style="color:#ffffff;">ไล่สล็อตออก!</button>
                            <button onclick="addMockComment('disagree')"
                                class="hover:bg-black px-4 py-2 rounded text-sm font-bold transition-colors"
                                style="background-color:#1f2937; color:#ffffff;">ให้โอกาสไปก่อน</button>
                        </div>

                        <div id="mock-comments-area" class="space-y-3 h-40 overflow-y-auto pr-2">
                            <div class="bg-white p-3 rounded shadow-sm text-sm">
                                <span class="font-bold" style="color:#1d4ed8;">Kopite_1989:</span>
                                <span style="color:#374151;"> ซาลาห์พูดถูก ทีมขาดผู้นำจริงๆ กัปตันหายไปไหนตอนทีมเป๋?</span>
                            </div>
                            <div class="bg-white p-3 rounded shadow-sm text-sm border-l-2 border-liverpool-red">
                                <span class="font-bold" style="color:#1e293b;">JamesPok LFC:</span>
                                <span style="color:#374151;"> ตบขมับเลยครับแมตช์นี้!</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <!-- Footer: bg-gray-900 → ขาว/เทาอ่อน -->
    <footer class="py-6 text-center" style="background-color:#111827;">
        <p class="font-bold mb-2" style="color:#ffffff;">เจมส์ป๊อก LFC</p>
        <p class="text-sm" style="color:#9ca3af;">ข้อมูลอ้างอิง: Paul Gorst (Tier 1), NBC Sports, Chelsea FC Official</p>
        <p class="text-xs mt-2" style="color:#6b7280;">&copy; 2026 เจมส์ป๊อก LFC Dashboard</p>
    </footer>

    <!-- ===================================================
         Interactive Logic & Chart Configuration
         =================================================== -->
    <script>
        // --- Navigation Logic ---
        function switchTab(tabId) {
            document.getElementById('hot-topics').classList.replace('section-active', 'section-hidden');
            document.getElementById('match-stats').classList.replace('section-active', 'section-hidden');
            document.getElementById('analysis').classList.replace('section-active', 'section-hidden');

            document.getElementById(tabId).classList.replace('section-hidden', 'section-active');

            const navBtns = document.querySelectorAll('.nav-btn');
            navBtns.forEach(btn => {
                btn.classList.remove('border-white');
                btn.classList.add('border-transparent');
            });

            document.getElementById('nav-' + tabId).classList.remove('border-transparent');
            document.getElementById('nav-' + tabId).classList.add('border-white');
        }

        // --- Mock Comments ---
        function addMockComment(type) {
            const container = document.getElementById('mock-comments-area');
            const commentDiv = document.createElement('div');
            commentDiv.className = 'bg-white p-3 rounded shadow-sm text-sm animate-pulse';

            let name = "Fan_" + Math.floor(Math.random() * 1000);
            let text = type === 'agree'
                ? "เห็นด้วยกับพี่เจมส์ป๊อก สล็อตดื้อเกินไป ไม่ยอมรับผิด!"
                : "ผมว่าใจเย็นๆ ขุมกำลังเราเจ็บเยอะ สล็อตทำได้เท่านี้ก็โอเคแล้ว";

            commentDiv.innerHTML = `<span class="font-bold" style="color:#1e293b;">${name}:</span> <span style="color:#374151;">${text}</span>`;
            container.insertBefore(commentDiv, container.firstChild);
            setTimeout(() => { commentDiv.classList.remove('animate-pulse'); }, 1000);
        }

        // --- Chart.js: Radar Chart ---
        const ctxStats = document.getElementById('matchStatsChart').getContext('2d');
        new Chart(ctxStats, {
            type: 'radar',
            data: {
                labels: ['การครองบอล (%)', 'โอกาสยิง', 'ยิงเข้ากรอบ', 'จ่ายบอลสำเร็จ (%)', 'เตะมุม', 'ฟาวล์'],
                datasets: [{
                    label: 'ลิเวอร์พูล',
                    data: [42, 11, 4, 81, 6, 12],
                    backgroundColor: 'rgba(200, 16, 46, 0.15)',
                    borderColor: '#C8102E',
                    pointBackgroundColor: '#C8102E',
                    borderWidth: 2
                }, {
                    label: 'เชลซี',
                    data: [58, 14, 5, 87, 5, 10],
                    backgroundColor: 'rgba(29, 78, 216, 0.15)',
                    borderColor: '#1d4ed8',
                    pointBackgroundColor: '#1d4ed8',
                    borderWidth: 2
                }]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                scales: {
                    r: {
                        angleLines: { display: true },
                        suggestedMin: 0,
                        pointLabels: {
                            color: '#1e293b',   /* ป้ายกำกับ: เข้ม บน ขาว */
                            font: { size: 12, family: "'Noto Sans Thai', sans-serif" }
                        },
                        ticks: {
                            color: '#475569',
                            backdropColor: 'transparent'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#1e293b' }  /* legend text: เข้ม บน ขาว */
                    }
                }
            }
        });

        // --- Chart.js: Line Chart (Momentum) ---
        const ctxMomentum = document.getElementById('momentumChart').getContext('2d');
        new Chart(ctxMomentum, {
            type: 'line',
            data: {
                labels: ['0', '15', '30', 'HT', '60', '75', '90'],
                datasets: [{
                    label: 'ดัชนีโมเมนตัม (บวก=LIV, ลบ=CHE)',
                    data: [0, 5, -2, -5, 2, -8, -4],
                    borderColor: '#1e293b',
                    backgroundColor: 'rgba(30, 41, 59, 0.08)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 5,
                    pointBackgroundColor: function(context) {
                        var index = context.dataIndex;
                        if (index === 0 || index === 2 || index === 5) return '#C8102E';
                        return '#1e293b';
                    }
                }]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                scales: {
                    x: {
                        ticks: { color: '#1e293b' },      /* แกน X: เข้ม บน ขาว */
                        grid: { color: '#e5e7eb' }
                    },
                    y: {
                        min: -10,
                        max: 10,
                        ticks: { display: false },
                        grid: {
                            color: function(context) {
                                return context.tick.value === 0 ? '#0f172a' : '#e5e7eb';
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = '';
                                if (context.dataIndex === 0) label = ' นาที 6: กราเฟนแบร์กยิงนำ';
                                if (context.dataIndex === 2) label = ' นาที 35: เอ็นโซ่ตีเสมอ';
                                if (context.dataIndex === 5) label = ' นาที 67: ถอดอึงูโมฮา โมเมนตัมตก';
                                return label || ` โมเมนตัม: ${context.parsed.y}`;
                            }
                        }
                    },
                    legend: {
                        display: true,
                        labels: { color: '#1e293b' }      /* legend text: เข้ม บน ขาว */
                    }
                }
            }
        });
    </script>
</body>
</html>
