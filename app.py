from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'math-lesson-secret-key'

DB_PATH = '/mnt/data/interactive_math_lesson.db' if os.path.exists('/mnt/data') else 'interactive_math_lesson.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            elapsed_seconds REAL NOT NULL,
            score INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


ACTIVITY_ONE_CORRECT = {
    'المنوال': '6',
    'الوسيط': '4',
    'المدى': '11'
}

QUESTIONS = [
    {
        'id': 1,
        'text': 'إذا كان المنوال للقيم ٥ ، ٩ ، ٢١ ، ١٧ ، ٣س هو ٢١ . حوط قيمة س',
        'choices': ['٧', '٩', '٢١', '٢٧'],
        'answer': '٧'
    },
    {
        'id': 2,
        'text': 'حوط الإجابة الصحيحة: المدى للقيم الآتية: ١٩ ، ٢٦ ، ١٧ ، ٣٢ ، ٢٦',
        'choices': ['١٥', '١٦', '٢٤', '٢٦'],
        'answer': '١٥'
    },
    {
        'id': 3,
        'text': 'يعرض الإطار المقابل أطوال ستة أشخاص (بالمتر): ١٫٤٢ ، ١٫٥٤ ، ١٫٥٤ ، ١٫٦٥ ، ١٫٧٠ ، ١٫٧٢ . حوط قيمة المدى للأطوال (بالمتر)',
        'choices': ['٠٫٣٠', '٠٫٤٢', '٠٫٧٢', '١٫٥٤'],
        'answer': '٠٫٣٠'
    }
]


PAGE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>درس تفاعلي - المقاييس الإحصائية والمدى</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Tahoma, Arial, sans-serif;
      background:
        radial-gradient(circle at top right, rgba(148, 87, 235, 0.18), transparent 26%),
        radial-gradient(circle at top left, rgba(65, 161, 255, 0.22), transparent 24%),
        linear-gradient(135deg, #0c1633, #132a61 45%, #163d80 100%);
      color: #fff;
      min-height: 100vh;
      overflow-x: hidden;
    }
    .math-bg {
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: .08;
      font-size: 56px;
      overflow: hidden;
    }
    .math-bg span {
      position: absolute;
      animation: floaty 14s linear infinite;
    }
    @keyframes floaty {
      from { transform: translateY(40px); opacity: 0; }
      15% { opacity: .6; }
      85% { opacity: .6; }
      to { transform: translateY(-120px); opacity: 0; }
    }
    .app-shell {
      position: relative;
      z-index: 1;
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 18px;
      min-height: 100vh;
      padding: 18px;
    }
    .sidebar {
      background: rgba(255,255,255,.09);
      border: 1px solid rgba(255,255,255,.15);
      border-radius: 24px;
      backdrop-filter: blur(10px);
      box-shadow: 0 18px 45px rgba(0,0,0,.24);
      padding: 18px;
      position: sticky;
      top: 18px;
      height: calc(100vh - 36px);
      overflow-y: auto;
    }
    .content {
      background: rgba(255,255,255,.08);
      border: 1px solid rgba(255,255,255,.14);
      border-radius: 28px;
      backdrop-filter: blur(8px);
      box-shadow: 0 18px 45px rgba(0,0,0,.2);
      padding: 18px 22px 28px;
      min-height: calc(100vh - 36px);
    }
    .hero {
      text-align: center;
      padding: 20px 16px 10px;
    }
    .hero h1, .hero h2, .hero h3, .hero p { margin: 8px 0; }
    .school { font-size: 31px; font-weight: 700; color: #fff; }
    .center { font-size: 22px; color: #c6f0ff; }
    .library { font-size: 22px; color: #ffe7a5; }
    .lesson-meta {
      margin-top: 18px;
      display: inline-block;
      padding: 16px 28px;
      border-radius: 22px;
      background: linear-gradient(135deg, rgba(255,255,255,.16), rgba(255,255,255,.08));
      border: 1px solid rgba(255,255,255,.2);
      box-shadow: 0 12px 28px rgba(0,0,0,.18);
    }
    .lesson-meta .big-title { font-size: 30px; color: #fff1b8; font-weight: 700; }
    .lesson-meta .small { font-size: 21px; color: #ecf7ff; }
    .card {
      background: rgba(255,255,255,.08);
      border: 1px solid rgba(255,255,255,.16);
      border-radius: 24px;
      padding: 18px;
      margin-bottom: 16px;
      box-shadow: 0 10px 25px rgba(0,0,0,.15);
    }
    .control-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-top: 18px;
    }
    input[type="text"] {
      width: 100%;
      padding: 14px 16px;
      border-radius: 16px;
      border: 1px solid rgba(255,255,255,.2);
      background: rgba(255,255,255,.95);
      color: #10234b;
      font-size: 18px;
      font-family: inherit;
      outline: none;
    }
    .btn {
      border: none;
      border-radius: 18px;
      padding: 14px 16px;
      font-family: inherit;
      font-size: 18px;
      cursor: pointer;
      color: #fff;
      transition: .2s ease;
      box-shadow: 0 10px 20px rgba(0,0,0,.18);
    }
    .btn:hover { transform: translateY(-2px); }
    .btn-primary { background: linear-gradient(135deg, #f39c12, #e67e22); }
    .btn-secondary { background: linear-gradient(135deg, #26a69a, #1e88e5); }
    .btn-danger { background: linear-gradient(135deg, #ef5350, #d81b60); }
    .btn-muted { background: linear-gradient(135deg, #7f8fa6, #57606f); }
    .stage { display: none; }
    .stage.active { display: block; }

    .activity-board {
      background: #f8f3fb;
      color: #1d2445;
      border-radius: 28px;
      padding: 26px 24px 20px;
      min-height: 640px;
      position: relative;
      overflow: hidden;
    }
    .notebook-rings {
      position: absolute;
      left: 10px;
      top: 100px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .notebook-rings span {
      width: 26px;
      height: 8px;
      border-radius: 8px;
      background: #d0d0d7;
      display: block;
    }
    .activity-header {
      text-align: center;
      margin-bottom: 18px;
    }
    .activity-banner {
      display: inline-flex;
      align-items: center;
      gap: 16px;
      background: #f7d67e;
      color: #d43f2f;
      padding: 10px 20px;
      border-radius: 18px;
      font-size: 28px;
      font-weight: 700;
      box-shadow: 0 6px 14px rgba(0,0,0,.12);
    }
    .activity-subline {
      color: #2f9d48;
      font-size: 17px;
      font-weight: 700;
      margin-top: 10px;
    }
    .activity-question {
      text-align: center;
      color: #4a61b3;
      font-size: 25px;
      line-height: 1.8;
      font-weight: 700;
      margin: 20px auto 18px;
      max-width: 980px;
    }
    .pink-box {
      background: #ef8fa1;
      max-width: 660px;
      margin: 0 auto 28px;
      padding: 22px 18px;
      color: #232323;
      font-size: 30px;
      letter-spacing: 10px;
      text-align: center;
      line-height: 1.7;
    }
    .a1-layout {
      display: grid;
      grid-template-columns: 190px 1fr;
      gap: 16px;
      align-items: start;
    }
    .draggables {
      display: flex;
      flex-direction: column;
      gap: 18px;
      align-items: center;
      padding-top: 6px;
    }
    .drag-item {
      width: 132px;
      height: 96px;
      border-radius: 48% 48% 42% 42% / 56% 56% 38% 38%;
      border: 3px solid rgba(0,0,0,.48);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 34px;
      font-weight: 700;
      cursor: grab;
      box-shadow: 0 7px 12px rgba(0,0,0,.14);
      position: relative;
      user-select: none;
    }
    .drag-item::before, .drag-item::after {
      content: '';
      position: absolute;
      bottom: 10px;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: inherit;
      border: 3px solid rgba(0,0,0,.48);
    }
    .drag-item::before { left: -3px; }
    .drag-item::after { right: -3px; }
    .c-green { background: #8dcf8b; }
    .c-purple { background: #d78cf3; }
    .c-pink { background: #f8a0d3; }
    .c-blue { background: #79daf1; }
    .c-brown { background: #c79a62; }

    .drop-section-title {
      text-align: right;
      color: #5569bf;
      font-size: 28px;
      font-weight: 700;
      margin: 10px 0 18px;
    }
    .cups-row {
      display: flex;
      justify-content: center;
      gap: 44px;
      flex-wrap: wrap;
      margin-top: 18px;
    }
    .cup-wrap { text-align: center; }
    .cup {
      width: 170px;
      height: 150px;
      position: relative;
      filter: drop-shadow(0 6px 10px rgba(0,0,0,.16));
    }
    .cup-top {
      position: absolute;
      top: 0;
      left: 10px;
      width: 150px;
      height: 34px;
      background: linear-gradient(180deg, #f8d48c, #ebbd66);
      border: 2px solid #9a6e2b;
      border-radius: 14px 14px 8px 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      font-weight: 700;
      color: #5a3912;
      z-index: 2;
    }
    .cup-body {
      position: absolute;
      top: 24px;
      left: 18px;
      width: 134px;
      height: 116px;
      background:
        linear-gradient(135deg, transparent 0 47%, rgba(180,126,50,.35) 48% 50%, transparent 51%),
        linear-gradient(45deg, transparent 0 47%, rgba(180,126,50,.35) 48% 50%, transparent 51%),
        linear-gradient(180deg, #f9e0ad, #e9b86f);
      clip-path: polygon(8% 0, 92% 0, 76% 100%, 24% 100%);
      border: 2px solid #9a6e2b;
    }
    .dropzone {
      position: absolute;
      inset: 38px 32px 18px 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      font-size: 30px;
      font-weight: 700;
      color: #5c4528;
      z-index: 3;
    }
    .dropzone.drag-over {
      outline: 3px dashed #d55a00;
      border-radius: 20px;
    }
    .placeholder {
      color: rgba(76,56,34,.45);
      font-size: 17px;
      line-height: 1.4;
      letter-spacing: normal;
    }

    .section-title {
      text-align: center;
      font-size: 28px;
      font-weight: 700;
      color: #ffe39c;
      margin: 18px 0 12px;
    }
    .question-card {
      background: #fff;
      color: #111;
      border: 3px solid #1f1f1f;
      border-radius: 20px;
      padding: 24px;
      margin-bottom: 18px;
      box-shadow: 0 12px 22px rgba(0,0,0,.14);
    }
    .q-num {
      font-size: 24px;
      font-weight: 700;
      margin-bottom: 10px;
    }
    .q-text {
      font-size: 30px;
      font-weight: 700;
      line-height: 1.9;
      margin-bottom: 18px;
    }
    .instruction {
      text-align: center;
      font-size: 24px;
      font-weight: 700;
      margin-bottom: 18px;
    }
    .choices {
      display: grid;
      grid-template-columns: repeat(2, minmax(180px, 1fr));
      gap: 16px;
      max-width: 780px;
      margin: 0 auto;
    }
    .choice-btn {
      background: #f7f7f7;
      border: 2px solid #222;
      color: #111;
      border-radius: 18px;
      padding: 18px;
      font-size: 34px;
      font-weight: 700;
      cursor: pointer;
      transition: .2s ease;
      min-height: 92px;
    }
    .choice-btn:hover { transform: translateY(-2px); }
    .choice-btn.correct { background: #d9f7d9; border-color: #2e7d32; color: #175e20; }
    .choice-btn.wrong { background: #ffe1e1; border-color: #d32f2f; color: #8b0000; }

    .result-box {
      text-align: center;
      background: linear-gradient(135deg, rgba(255,255,255,.18), rgba(255,255,255,.08));
      border: 1px solid rgba(255,255,255,.2);
      border-radius: 28px;
      padding: 34px 20px;
      margin-top: 22px;
    }
    .result-box h2 { font-size: 36px; margin: 0 0 10px; color: #ffe39c; }
    .result-box p { font-size: 24px; margin: 10px 0; }
    .footer-credit {
      margin-top: 18px;
      text-align: center;
      color: #eef7ff;
      font-size: 18px;
      line-height: 1.9;
      padding-top: 12px;
      border-top: 1px solid rgba(255,255,255,.15);
    }
    .leader-block h3 {
      margin: 0 0 12px;
      font-size: 22px;
      color: #ffe39c;
    }
    .leader-item {
      display: grid;
      grid-template-columns: 34px 1fr auto;
      align-items: center;
      gap: 10px;
      background: rgba(255,255,255,.08);
      padding: 10px 12px;
      border-radius: 16px;
      margin-bottom: 10px;
      font-size: 16px;
    }
    .medal {
      width: 34px;
      height: 34px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      background: rgba(255,255,255,.18);
    }
    .tiny {
      color: #d6e7ff;
      font-size: 15px;
      line-height: 1.7;
    }
    .timer-box, .group-box {
      background: rgba(255,255,255,.08);
      border-radius: 20px;
      padding: 14px;
      margin-bottom: 14px;
    }
    .timer-value {
      font-size: 38px;
      font-weight: 700;
      color: #ffe39c;
      text-align: center;
    }
    @media (max-width: 1100px) {
      .app-shell { grid-template-columns: 1fr; }
      .sidebar { position: static; height: auto; }
      .a1-layout { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="math-bg">
    <span style="right:5%; top:82%; animation-delay:0s;">∑</span>
    <span style="right:18%; top:90%; animation-delay:2s;">π</span>
    <span style="right:72%; top:88%; animation-delay:5s;">√</span>
    <span style="right:48%; top:92%; animation-delay:8s;">÷</span>
    <span style="right:88%; top:87%; animation-delay:3s;">+</span>
    <span style="right:33%; top:85%; animation-delay:7s;">%</span>
    <span style="right:58%; top:94%; animation-delay:10s;">x̄</span>
  </div>

  <div class="app-shell">
    <aside class="sidebar">
      <div class="group-box">
        <div class="tiny">اسم المجموعة الحالية</div>
        <div id="currentGroup" style="font-size:26px;font-weight:700;text-align:center;margin-top:8px;">—</div>
      </div>

      <div class="timer-box">
        <div class="tiny" style="text-align:center;">المؤقت</div>
        <div class="timer-value" id="timerDisplay">00:00</div>
      </div>

      <div class="card leader-block">
        <h3>🏆 صدارة النشاط</h3>
        <div id="leaderboard"></div>
      </div>

      <div class="card">
        <button class="btn btn-secondary" style="width:100%;margin-bottom:10px;" onclick="refreshLeaderboard()">🔄 تحديث المجموعات</button>
        <button class="btn btn-danger" style="width:100%;" onclick="clearAllParticipants()">🗑 مسح المشاركين</button>
      </div>

      <div class="card tiny">
        <div>• النشاط صار واحد فقط.</div>
        <div>• يبدأ بالسحب والإفلات ثم الاختيار المتعدد.</div>
        <div>• الصدارة مشتركة بين جميع الأجهزة.</div>
      </div>
    </aside>

    <main class="content">
      <section id="stage-home" class="stage active">
        <div class="hero">
          <h1 class="school">مدرسة سلمى بنت قيس للتعليم الأساسي (5–12)</h1>
          <h2 class="center">مركز مصادر التعلّم</h2>
          <h3 class="library">المكتبة الرقمية التفاعلية</h3>
          <div class="lesson-meta">
            <div class="small">الرياضيات – الفصل الدراسي الثاني – الصف السابع</div>
            <div class="big-title">الوحدة والدرس: 14-2 | المقاييس الإحصائية والمدى</div>
          </div>
        </div>

        <div class="card" style="max-width:760px;margin:18px auto 0;">
          <div style="font-size:24px;font-weight:700;margin-bottom:12px;text-align:center;">ابدئي باسم المجموعة</div>
          <input type="text" id="groupNameInput" placeholder="اكتبي اسم المجموعة هنا">
          <div class="control-grid">
            <button class="btn btn-primary" onclick="startUnifiedActivity()">🚀 ابدأ النشاط</button>
          </div>
        </div>
      </section>

      <section id="stage-activity" class="stage">
        <div class="activity-board">
          <div class="notebook-rings">
            <span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span>
          </div>

          <div class="activity-header">
            <div class="activity-banner">◀ نشاط جماعي : استراتيجية النصف والنصف الآخر ▶</div>
            <div class="activity-subline">كتاب الطالب صفحة (١٠٠) رقم (١)</div>
          </div>

          <div class="activity-question">
            يوضح الإطار المقابل درجات الحرارة التي سجلها بدرى الجبل الأخضر<br>
            خلال شهري يناير ولمدة ثلاثة أسابيع يوميًا.
          </div>

          <div class="pink-box">٧ ٢ ١- ٣ ٢ ٢- ٠ ٢ ٦ ٦ &nbsp;&nbsp; ٣ ٤ ٦ ٦ ٥ ٣ ٨ ٩ ٦ ٦ ٢</div>

          <div class="a1-layout">
            <div class="draggables" id="dragContainer">
              <div class="drag-item c-green" draggable="true" data-value="7">٧</div>
              <div class="drag-item c-purple" draggable="true" data-value="4">٤</div>
              <div class="drag-item c-pink" draggable="true" data-value="3">٣</div>
              <div class="drag-item c-blue" draggable="true" data-value="6">٦</div>
              <div class="drag-item c-brown" draggable="true" data-value="11">١١</div>
            </div>

            <div>
              <div class="drop-section-title">أوجد ما يلي :</div>
              <div class="cups-row">
                <div class="cup-wrap">
                  <div class="cup">
                    <div class="cup-top">المنوال</div>
                    <div class="cup-body"></div>
                    <div class="dropzone" data-zone="المنوال"><span class="placeholder">اسحبي هنا</span></div>
                  </div>
                </div>
                <div class="cup-wrap">
                  <div class="cup">
                    <div class="cup-top">الوسيط</div>
                    <div class="cup-body"></div>
                    <div class="dropzone" data-zone="الوسيط"><span class="placeholder">اسحبي هنا</span></div>
                  </div>
                </div>
                <div class="cup-wrap">
                  <div class="cup">
                    <div class="cup-top">المدى</div>
                    <div class="cup-body"></div>
                    <div class="dropzone" data-zone="المدى"><span class="placeholder">اسحبي هنا</span></div>
                  </div>
                </div>
              </div>

              <div class="control-grid" style="margin-top:26px;">
                <button class="btn btn-secondary" onclick="checkDragAndUnlock()">✅ تحقق من السحب والإفلات</button>
                <button class="btn btn-muted" onclick="resetUnifiedActivity()">↺ إعادة النشاط</button>
              </div>
              <div id="activityMsg" style="margin-top:14px;font-size:22px;font-weight:700;text-align:center;"></div>
            </div>
          </div>
        </div>

        <div id="mcqSection" style="display:none; margin-top:18px;">
          <div class="section-title">الآن أكملي نفس النشاط بالاختيار المتعدد</div>
          <div id="questionsContainer"></div>
          <div class="control-grid">
            <button class="btn btn-primary" onclick="finishUnifiedActivity()">🏁 إنهاء النشاط كاملاً</button>
          </div>
        </div>
      </section>

      <section id="stage-result" class="stage">
        <div class="result-box">
          <h2>🎉 انتهى النشاط!</h2>
          <p id="resultText"></p>
          <p id="resultRank"></p>
          <div class="control-grid" style="max-width:700px;margin:18px auto 0;">
            <button class="btn btn-primary" onclick="goToStage('stage-home')">العودة للرئيسية</button>
            <button class="btn btn-secondary" onclick="resetUnifiedActivity(); goToStage('stage-activity')">إعادة النشاط</button>
          </div>
        </div>
      </section>

      <div class="footer-credit">
        <div><strong>برمجة وتصميم المحتوى:</strong></div>
        <div>أخصائية مركز مصادر التعلّم</div>
        <div><strong>الأستاذة سامية المقبالية</strong></div>
      </div>
    </main>
  </div>

  <script>
    let currentGroup = '';
    let startTime = null;
    let timerInterval = null;
    let dragAnswers = { 'المنوال': null, 'الوسيط': null, 'المدى': null };
    const questions = {{ questions_json | safe }};

    function goToStage(id) {
      document.querySelectorAll('.stage').forEach(s => s.classList.remove('active'));
      document.getElementById(id).classList.add('active');
    }

    function setGroup(name) {
      currentGroup = name.trim();
      document.getElementById('currentGroup').textContent = currentGroup || '—';
    }

    function formatTime(totalSeconds) {
      const s = Math.floor(totalSeconds % 60).toString().padStart(2, '0');
      const m = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
      return `${m}:${s}`;
    }

    function startTimer() {
      startTime = Date.now();
      clearInterval(timerInterval);
      timerInterval = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        document.getElementById('timerDisplay').textContent = formatTime(elapsed);
      }, 250);
    }

    function stopTimer() {
      clearInterval(timerInterval);
      const elapsed = startTime ? (Date.now() - startTime) / 1000 : 0;
      document.getElementById('timerDisplay').textContent = formatTime(elapsed);
      return elapsed;
    }

    function startUnifiedActivity() {
      const name = document.getElementById('groupNameInput').value;
      if (!name.trim()) {
        alert('اكتبي اسم المجموعة أولًا');
        return;
      }
      setGroup(name);
      resetUnifiedActivity(false);
      renderQuestions();
      goToStage('stage-activity');
      startTimer();
    }

    function resetUnifiedActivity(clearMsg = true) {
      dragAnswers = { 'المنوال': null, 'الوسيط': null, 'المدى': null };
      document.querySelectorAll('.dropzone').forEach(zone => {
        zone.innerHTML = '<span class="placeholder">اسحبي هنا</span>';
      });
      document.querySelectorAll('.drag-item').forEach(item => {
        item.style.visibility = 'visible';
        item.style.pointerEvents = 'auto';
      });
      document.getElementById('mcqSection').style.display = 'none';
      if (clearMsg) document.getElementById('activityMsg').textContent = '';
      renderQuestions();
    }

    function checkDragAndUnlock() {
      const msg = document.getElementById('activityMsg');
      if (!dragAnswers['المنوال'] || !dragAnswers['الوسيط'] || !dragAnswers['المدى']) {
        msg.style.color = '#b32121';
        msg.textContent = 'أكملي سحب جميع القيم أولًا.';
        return;
      }
      const ok = dragAnswers['المنوال'] === '6' && dragAnswers['الوسيط'] === '4' && dragAnswers['المدى'] === '11';
      if (!ok) {
        msg.style.color = '#b32121';
        msg.textContent = 'بعض الإجابات غير صحيحة. حاولي مرة أخرى.';
        return;
      }
      msg.style.color = '#16752c';
      msg.textContent = 'أحسنتِ! تم فتح جزء الاختيار المتعدد.';
      document.getElementById('mcqSection').style.display = 'block';
      document.getElementById('mcqSection').scrollIntoView({ behavior: 'smooth' });
    }

    function renderQuestions() {
      const container = document.getElementById('questionsContainer');
      container.innerHTML = '';
      questions.forEach((q, idx) => {
        const card = document.createElement('div');
        card.className = 'question-card';
        let html = `<div class="q-num">${idx + 1}</div><div class="q-text">${q.text}</div>`;
        html += `<div class="instruction">حوط الإجابة الصحيحة</div><div class="choices">`;
        q.choices.forEach(choice => {
          html += `<button class="choice-btn" data-qid="${q.id}" data-value="${choice}" onclick="answerMCQ(this)">${choice}</button>`;
        });
        html += `</div>`;
        card.innerHTML = html;
        container.appendChild(card);
      });
    }

    function answerMCQ(btn) {
      const qid = Number(btn.dataset.qid);
      const q = questions.find(x => x.id === qid);
      const parent = btn.parentElement;
      [...parent.querySelectorAll('.choice-btn')].forEach(b => {
        b.disabled = true;
        if (b.dataset.value === q.answer) b.classList.add('correct');
      });
      if (btn.dataset.value !== q.answer) btn.classList.add('wrong');
    }

    function finishUnifiedActivity() {
      const answeredCount = document.querySelectorAll('.choices').length;
      const completedCount = [...document.querySelectorAll('.choices')].filter(box =>
        [...box.querySelectorAll('.choice-btn')].some(btn => btn.disabled)
      ).length;

      if (document.getElementById('mcqSection').style.display === 'none') {
        alert('أنهي السحب والإفلات أولًا.');
        return;
      }
      if (completedCount < answeredCount) {
        alert('أكملي جميع أسئلة الاختيار المتعدد أولًا.');
        return;
      }

      let score = 3;
      questions.forEach(q => {
        const buttons = document.querySelectorAll(`.choice-btn[data-qid="${q.id}"]`);
        const clickedWrong = [...buttons].some(b => b.classList.contains('wrong'));
        if (!clickedWrong) score += 1;
      });

      const elapsed = stopTimer();
      saveAttempt(currentGroup, elapsed, score).then(rank => {
        document.getElementById('resultText').textContent = `المجموعة: ${currentGroup} | الزمن: ${formatTime(elapsed)} | الدرجة: ${score}/6`;
        document.getElementById('resultRank').textContent = rank ? `ترتيبكم الحالي: ${rank}` : '';
        goToStage('stage-result');
        refreshLeaderboard();
      });
    }

    async function saveAttempt(groupName, elapsed, score) {
      const res = await fetch('/api/save_attempt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ group_name: groupName, elapsed_seconds: elapsed, score })
      });
      const data = await res.json();
      return data.rank;
    }

    async function refreshLeaderboard() {
      const res = await fetch('/api/leaderboard');
      const data = await res.json();
      const holder = document.getElementById('leaderboard');
      if (!data.length) {
        holder.innerHTML = '<div class="tiny">لا توجد نتائج بعد.</div>';
        return;
      }
      const medals = ['🥇', '🥈', '🥉'];
      holder.innerHTML = data.map((row, idx) => `
        <div class="leader-item">
          <div class="medal">${medals[idx] || (idx + 1)}</div>
          <div>
            <div style="font-weight:700;">${row.group_name}</div>
            <div class="tiny">درجة: ${row.score}</div>
          </div>
          <div style="font-weight:700;">${formatTime(row.elapsed_seconds)}</div>
        </div>
      `).join('');
    }

    async function clearAllParticipants() {
      const ok = confirm('هل تريدين بالفعل مسح جميع المشاركين والنتائج؟');
      if (!ok) return;
      await fetch('/api/clear_attempts', { method: 'POST' });
      refreshLeaderboard();
      alert('تم مسح المشاركين بنجاح.');
    }

    document.addEventListener('DOMContentLoaded', () => {
      refreshLeaderboard();

      let dragged = null;
      document.querySelectorAll('.drag-item').forEach(item => {
        item.addEventListener('dragstart', e => {
          dragged = item;
          e.dataTransfer.setData('text/plain', item.dataset.value);
        });
      });

      document.querySelectorAll('.dropzone').forEach(zone => {
        zone.addEventListener('dragover', e => {
          e.preventDefault();
          zone.classList.add('drag-over');
        });
        zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
        zone.addEventListener('drop', e => {
          e.preventDefault();
          zone.classList.remove('drag-over');
          if (!dragged) return;
          const value = dragged.dataset.value;
          const zoneName = zone.dataset.zone;

          const previousZone = Object.keys(dragAnswers).find(k => dragAnswers[k] === value);
          if (previousZone) {
            dragAnswers[previousZone] = null;
            const prevZoneEl = document.querySelector(`.dropzone[data-zone="${previousZone}"]`);
            prevZoneEl.innerHTML = '<span class="placeholder">اسحبي هنا</span>';
          }

          dragAnswers[zoneName] = value;
          zone.textContent = dragged.textContent;
          dragged.style.visibility = 'hidden';
          dragged.style.pointerEvents = 'none';
          dragged = null;
        });
      });
    });
  </script>
</body>
</html>
'''


@app.route('/')
def home():
    return render_template_string(PAGE, questions_json=json.dumps(QUESTIONS, ensure_ascii=False))


@app.route('/api/save_attempt', methods=['POST'])
def save_attempt():
    data = request.get_json(force=True)
    group_name = data.get('group_name', '').strip()
    elapsed_seconds = float(data.get('elapsed_seconds', 0))
    score = int(data.get('score', 0))

    if not group_name or elapsed_seconds <= 0:
        return jsonify({'ok': False, 'error': 'بيانات غير صالحة'}), 400

    created_at = datetime.utcnow().isoformat()
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO attempts (group_name, elapsed_seconds, score, created_at) VALUES (?, ?, ?, ?)',
        (group_name, elapsed_seconds, score, created_at)
    )
    conn.commit()

    cur.execute(
        '''
        SELECT group_name, MIN(elapsed_seconds) AS best_time, MAX(score) AS best_score
        FROM attempts
        GROUP BY group_name
        ORDER BY best_time ASC, best_score DESC, group_name ASC
        '''
    )
    rows = cur.fetchall()
    conn.close()

    rank = None
    for idx, row in enumerate(rows, start=1):
        if row['group_name'] == group_name:
            rank = idx
            break

    return jsonify({'ok': True, 'rank': rank})


@app.route('/api/leaderboard')
def leaderboard():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        '''
        SELECT group_name,
               MIN(elapsed_seconds) AS elapsed_seconds,
               MAX(score) AS score
        FROM attempts
        GROUP BY group_name
        ORDER BY elapsed_seconds ASC, score DESC, group_name ASC
        LIMIT 10
        '''
    )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/api/clear_attempts', methods=['POST'])
def clear_attempts():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM attempts')
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

