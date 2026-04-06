from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_NAME = "leaderboard.db"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>المقاييس الإحصائية والمدى</title>
  <style>
    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: Tahoma, Arial, sans-serif;
      background:
        radial-gradient(circle at top right, rgba(122, 201, 255, 0.25), transparent 25%),
        radial-gradient(circle at bottom left, rgba(183, 129, 255, 0.25), transparent 25%),
        linear-gradient(135deg, #eef8ff, #f9f2ff, #fffdf6);
      color: #24324a;
      min-height: 100vh;
      overflow-x: hidden;
    }

    .math-bg {
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: 0.08;
      font-size: 42px;
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      place-items: center;
      z-index: 0;
    }

    .container {
      position: relative;
      z-index: 1;
      width: min(1400px, 96%);
      margin: 18px auto;
    }

    .top-header {
      background: rgba(255,255,255,0.82);
      border: 2px solid rgba(120, 150, 255, 0.25);
      backdrop-filter: blur(8px);
      border-radius: 28px;
      box-shadow: 0 12px 35px rgba(61, 90, 128, 0.12);
      padding: 24px 18px;
      text-align: center;
    }

    .school {
      font-size: 2rem;
      font-weight: 800;
      color: #224c8f;
      margin-bottom: 6px;
    }

    .center-title {
      font-size: 1.4rem;
      font-weight: 700;
      color: #5b4ab1;
      margin-bottom: 6px;
    }

    .platform-title {
      font-size: 1.3rem;
      font-weight: 700;
      color: #1b9aaa;
      margin-bottom: 14px;
    }

    .lesson-title {
      font-size: 2rem;
      font-weight: 900;
      background: linear-gradient(90deg, #1d6fd6, #8b4fd9, #ff7c6d);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 8px;
    }

    .lesson-subtitle {
      font-size: 1.2rem;
      font-weight: 700;
      color: #334;
      line-height: 1.8;
    }

    .main-grid {
      display: grid;
      grid-template-columns: 330px 1fr;
      gap: 18px;
      margin-top: 18px;
    }

    .side-panel, .content-panel {
      background: rgba(255,255,255,0.85);
      border-radius: 26px;
      box-shadow: 0 12px 35px rgba(61, 90, 128, 0.12);
      border: 2px solid rgba(120, 150, 255, 0.18);
      backdrop-filter: blur(8px);
    }

    .side-panel {
      padding: 18px;
      position: sticky;
      top: 12px;
      height: fit-content;
    }

    .panel-title {
      font-size: 1.2rem;
      font-weight: 800;
      color: #234;
      margin-bottom: 12px;
      text-align: center;
    }

    .group-box {
      background: linear-gradient(135deg, #f4fbff, #fff8f1);
      border-radius: 18px;
      padding: 14px;
      margin-bottom: 14px;
      border: 1px solid rgba(0,0,0,0.06);
    }

    label {
      display: block;
      font-weight: 700;
      margin-bottom: 8px;
      color: #345;
    }

    input[type="text"] {
      width: 100%;
      border: 2px solid #d7e2f5;
      border-radius: 14px;
      padding: 12px 14px;
      font-size: 1rem;
      outline: none;
      transition: 0.25s;
    }

    input[type="text"]:focus {
      border-color: #7a9cff;
      box-shadow: 0 0 0 4px rgba(122,156,255,0.16);
    }

    .btn {
      width: 100%;
      border: none;
      border-radius: 14px;
      padding: 12px 16px;
      font-size: 1rem;
      font-weight: 800;
      cursor: pointer;
      transition: 0.2s ease;
      margin-top: 10px;
    }

    .btn:hover { transform: translateY(-2px); }

    .btn-primary {
      background: linear-gradient(90deg, #1d8cf8, #6a5cff);
      color: #fff;
      box-shadow: 0 10px 20px rgba(70, 90, 200, 0.22);
    }

    .btn-secondary {
      background: linear-gradient(90deg, #18b7a0, #42c96d);
      color: #fff;
    }

    .btn-danger {
      background: linear-gradient(90deg, #ff6c6c, #ff9248);
      color: #fff;
    }

    .timer-box, .status-box, .leaderboard-box {
      background: linear-gradient(135deg, #fbfdff, #f7f7ff);
      border: 1px solid rgba(0,0,0,0.06);
      border-radius: 18px;
      padding: 14px;
      margin-bottom: 14px;
    }

    .timer {
      font-size: 1.7rem;
      font-weight: 900;
      text-align: center;
      color: #2155a3;
    }

    .small-note {
      text-align: center;
      font-size: 0.95rem;
      color: #567;
      line-height: 1.8;
    }

    .leaderboard-list {
      margin: 0;
      padding: 0;
      list-style: none;
    }

    .leaderboard-list li {
      background: linear-gradient(135deg, #fffdf3, #f7fbff);
      border: 1px solid rgba(0,0,0,0.06);
      border-radius: 14px;
      padding: 10px 12px;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: center;
      font-weight: 700;
    }

    .content-panel { padding: 18px; }

    .section { display: none; animation: fadeUp 0.45s ease; }
    .section.active { display: block; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(18px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }

    .section-title {
      font-size: 1.55rem;
      font-weight: 900;
      color: #224;
    }

    .chip {
      background: linear-gradient(90deg, #fff6c5, #ffe5d2);
      color: #855400;
      border-radius: 999px;
      padding: 10px 14px;
      font-weight: 800;
      font-size: 0.95rem;
    }

    .intro-card {
      background: linear-gradient(135deg, #eef8ff, #fff7fb);
      border: 2px dashed #b6c8ef;
      border-radius: 22px;
      padding: 24px;
      text-align: center;
      line-height: 2;
      margin-bottom: 18px;
    }

    .intro-card h2 {
      margin: 0 0 10px;
      color: #274690;
      font-size: 1.8rem;
    }

    .intro-card p {
      margin: 6px 0;
      font-size: 1.15rem;
      font-weight: 700;
      color: #345;
    }

    .dataset-box {
      background: linear-gradient(135deg, #ffdce6, #ffd7dd);
      border-radius: 20px;
      padding: 18px;
      text-align: center;
      font-size: 2rem;
      font-weight: 900;
      color: #7a2647;
      letter-spacing: 4px;
      margin-bottom: 18px;
      line-height: 1.8;
      border: 2px solid rgba(122,38,71,0.08);
    }

    .activity-layout {
      display: grid;
      grid-template-columns: 240px 1fr;
      gap: 20px;
      align-items: start;
    }

    .scoops {
      display: flex;
      flex-direction: column;
      gap: 14px;
      align-items: center;
    }

    .scoop {
      width: 130px;
      height: 95px;
      border-radius: 65% 65% 50% 50% / 70% 70% 35% 35%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2.2rem;
      font-weight: 900;
      color: #1f1f1f;
      box-shadow: 0 10px 18px rgba(0,0,0,0.16);
      border: 3px solid rgba(0,0,0,0.14);
      cursor: grab;
      user-select: none;
      transition: transform 0.18s ease, box-shadow 0.18s ease;
    }

    .scoop:hover { transform: scale(1.05); }

    .scoop.dragging {
      opacity: 0.75;
      transform: scale(1.09);
      box-shadow: 0 18px 30px rgba(0,0,0,0.22);
    }

    .green { background: linear-gradient(135deg, #9de89e, #5fcf86); }
    .purple { background: linear-gradient(135deg, #d8a6ff, #ba76ff); }
    .pink { background: linear-gradient(135deg, #ffb5e0, #ff7fcb); }
    .blue { background: linear-gradient(135deg, #9feaff, #59d3ff); }
    .brown { background: linear-gradient(135deg, #d6b083, #b98556); }

    .cups-area {
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .instruction-box {
      background: linear-gradient(135deg, #f9fdff, #fffdf7);
      border: 1px solid rgba(0,0,0,0.06);
      border-radius: 18px;
      padding: 14px 18px;
      line-height: 2;
      font-size: 1.05rem;
      font-weight: 700;
      color: #345;
    }

    .cups {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      margin-top: 8px;
    }

    .drop-zone {
      min-height: 200px;
      border-radius: 18px;
      padding: 12px;
      background: linear-gradient(180deg, #fffef7, #fff5db);
      border: 2px dashed #d8b76f;
      text-align: center;
      position: relative;
      transition: 0.2s;
    }

    .drop-zone.over {
      transform: scale(1.02);
      box-shadow: 0 0 0 5px rgba(255, 215, 77, 0.22);
      border-color: #f1a208;
    }

    .cup-top {
      font-size: 1.45rem;
      font-weight: 900;
      background: linear-gradient(90deg, #d69328, #b37219);
      color: white;
      border-radius: 12px;
      padding: 10px;
      margin-bottom: 10px;
    }

    .drop-area {
      min-height: 110px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 16px;
      background:
        repeating-linear-gradient(
          45deg,
          rgba(226, 189, 126, 0.35),
          rgba(226, 189, 126, 0.35) 10px,
          rgba(255,255,255,0.35) 10px,
          rgba(255,255,255,0.35) 20px
        );
      color: #8b6d3b;
      font-weight: 800;
      font-size: 1rem;
      padding: 10px;
      overflow: hidden;
    }

    .drop-area .scoop {
      margin: auto;
      cursor: default;
    }

    .result-message {
      margin-top: 16px;
      border-radius: 16px;
      padding: 12px 14px;
      font-weight: 800;
      text-align: center;
      display: none;
    }

    .result-message.success {
      display: block;
      background: #e8fff0;
      color: #1d7a45;
      border: 1px solid #9ed8b2;
    }

    .result-message.error {
      display: block;
      background: #fff0f0;
      color: #b63a3a;
      border: 1px solid #efbbbb;
    }

    .question-card {
      background: linear-gradient(135deg, #f9fcff, #fff8fb);
      border-radius: 24px;
      padding: 22px;
      border: 1px solid rgba(0,0,0,0.06);
      margin-top: 12px;
    }

    .question-number {
      display: inline-block;
      background: linear-gradient(90deg, #5b9df9, #8b63ff);
      color: #fff;
      padding: 8px 14px;
      border-radius: 999px;
      font-weight: 900;
      margin-bottom: 14px;
    }

    .question-text {
      font-size: 1.45rem;
      font-weight: 900;
      color: #223;
      line-height: 2;
      margin-bottom: 18px;
    }

    .options {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
    }

    .option-btn {
      border: 2px solid #d8e2f5;
      border-radius: 18px;
      padding: 16px;
      background: #fff;
      cursor: pointer;
      font-size: 1.2rem;
      font-weight: 800;
      transition: 0.2s;
    }

    .option-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 18px rgba(80, 110, 180, 0.12);
    }

    .option-btn.correct {
      background: #eafff0;
      border-color: #52ba7a;
      color: #156a39;
    }

    .option-btn.wrong {
      background: #fff1f1;
      border-color: #e26868;
      color: #a92f2f;
    }

    .progress-wrap { margin-top: 18px; }

    .progress-bar {
      height: 16px;
      background: #e6edfb;
      border-radius: 999px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, #2ea5ff, #8f62ff, #ff8a65);
      transition: width 0.35s ease;
    }

    .progress-text {
      margin-top: 8px;
      font-weight: 800;
      color: #456;
      text-align: center;
    }

    .finish-card {
      text-align: center;
      padding: 36px 18px;
      background: linear-gradient(135deg, #effcff, #fff8ef);
      border-radius: 24px;
      border: 2px dashed #b7c8ea;
    }

    .finish-card h2 {
      margin: 0 0 12px;
      font-size: 2rem;
      color: #214f88;
    }

    .finish-card p {
      font-size: 1.15rem;
      font-weight: 700;
      line-height: 2;
      color: #345;
    }

    footer {
      margin-top: 18px;
      text-align: center;
      background: rgba(255,255,255,0.82);
      border: 2px solid rgba(120, 150, 255, 0.18);
      backdrop-filter: blur(8px);
      border-radius: 22px;
      padding: 16px;
      font-size: 1.05rem;
      font-weight: 800;
      color: #334;
      box-shadow: 0 12px 35px rgba(61, 90, 128, 0.1);
    }

    @media (max-width: 1100px) {
      .main-grid { grid-template-columns: 1fr; }
      .side-panel { position: static; }
      .activity-layout { grid-template-columns: 1fr; }
      .cups { grid-template-columns: 1fr; }
    }

    @media (max-width: 760px) {
      .school { font-size: 1.4rem; }
      .lesson-title { font-size: 1.45rem; }
      .dataset-box { font-size: 1.5rem; }
      .options { grid-template-columns: 1fr; }
      .question-text { font-size: 1.15rem; }
    }
  </style>
</head>
<body>
  <div class="math-bg">
    <div>∑</div><div>π</div><div>x̄</div><div>√</div><div>∞</div><div>Δ</div>
    <div>÷</div><div>∫</div><div>≈</div><div>±</div><div>∑</div><div>π</div>
    <div>x̄</div><div>√</div><div>∞</div><div>Δ</div><div>÷</div><div>∫</div>
  </div>

  <div class="container">
    <header class="top-header">
      <div class="school">مدرسة سلمى بنت قيس للتعليم الأساسي (5–12)</div>
      <div class="center-title">مركز مصادر التعلّم</div>
      <div class="platform-title">المكتبة الرقمية التفاعلية</div>
      <div class="lesson-title">الرياضيات – الفصل الدراسي الثاني – الصف السابع</div>
      <div class="lesson-subtitle">الوحدة والدرس: 14-2<br>المقاييس الإحصائية والمدى</div>
    </header>

    <div class="main-grid">
      <aside class="side-panel">
        <div class="panel-title">لوحة المجموعات والصدارة 🏆</div>

        <div class="group-box">
          <label for="groupName">اسم المجموعة</label>
          <input type="text" id="groupName" placeholder="اكتبي اسم المجموعة هنا" />
          <button class="btn btn-primary" onclick="startLesson()">ابدأ النشاط 🚀</button>
        </div>

        <div class="timer-box">
          <div class="panel-title" style="margin-bottom:8px;">⏱️ المؤقت</div>
          <div class="timer" id="timerDisplay">00:00</div>
        </div>

        <div class="status-box">
          <div class="panel-title" style="margin-bottom:8px;">حالة التقدم</div>
          <div class="small-note" id="statusText">أدخلي اسم المجموعة ثم ابدئي الدرس.</div>
        </div>

        <div class="leaderboard-box">
          <div class="panel-title" style="margin-bottom:8px;">صدارة النشاط الأول 🍦</div>
          <ul class="leaderboard-list" id="leaderboard1"></ul>
          <button class="btn btn-secondary" onclick="renderLeaderboards()">تحديث المجموعات</button>
          <button class="btn btn-danger" onclick="clearLeaderboard('activity1')">مسح المشاركين</button>
        </div>

        <div class="leaderboard-box">
          <div class="panel-title" style="margin-bottom:8px;">صدارة النشاط الثاني ⚡</div>
          <ul class="leaderboard-list" id="leaderboard2"></ul>
          <button class="btn btn-secondary" onclick="renderLeaderboards()">تحديث المجموعات</button>
          <button class="btn btn-danger" onclick="clearLeaderboard('activity2')">مسح المشاركين</button>
        </div>
      </aside>

      <main class="content-panel">
        <section class="section active" id="section-start">
          <div class="intro-card">
            <h2>🎯 درس تفاعلي: المقاييس الإحصائية والمدى</h2>
            <p>مرحبًا بكنَّ يا نجمات الرياضيات ✨</p>
            <p>في هذا الدرس ستخوض كل مجموعة نشاطين:</p>
            <p>🍦 النشاط الأول: سحب وإفلات</p>
            <p>⚡ النشاط الثاني: اختيار من متعدد</p>
            <p>وسيتم تسجيل أسرع مجموعة في قائمة الصدارة 🏆</p>
          </div>
        </section>

        <section class="section" id="section-activity1">
          <div class="section-header">
            <div class="section-title">🍦 النشاط الأول: اسحبي الرقم إلى الكوب الصحيح</div>
            <div class="chip">حددي المنوال والوسيط والمدى</div>
          </div>

          <div class="dataset-box">
            ٧ ، ٢ ، -١ ، ٣ ، ٢ ، -٢ ، ٠ ، ٢ ، ٦ ، ٦ <br>
            ٣ ، ٤ ، ٦ ، ٦ ، ٥ ، ٣ ، ٨ ، ٩ ، ٦ ، ٦ ، ٢
          </div>

          <div class="activity-layout">
            <div class="scoops" id="scoopsContainer">
              <div class="scoop green" draggable="true" data-value="7">٧</div>
              <div class="scoop purple" draggable="true" data-value="6">٦</div>
              <div class="scoop pink" draggable="true" data-value="4">٤</div>
              <div class="scoop blue" draggable="true" data-value="3">٣</div>
              <div class="scoop brown" draggable="true" data-value="11">١١</div>
            </div>

            <div class="cups-area">
              <div class="instruction-box">
                <strong>تعليمات النشاط:</strong><br>
                اسحبي كرة الآيسكريم التي تحمل الرقم الصحيح إلى الكوب المناسب.<br>
                المنوال = القيمة الأكثر تكرارًا<br>
                الوسيط = القيمة الوسطى بعد الترتيب<br>
                المدى = الفرق بين أكبر قيمة وأصغر قيمة
              </div>

              <div class="cups">
                <div class="drop-zone" data-answer="6">
                  <div class="cup-top">المنوال</div>
                  <div class="drop-area">اسحبي هنا</div>
                </div>

                <div class="drop-zone" data-answer="4">
                  <div class="cup-top">الوسيط</div>
                  <div class="drop-area">اسحبي هنا</div>
                </div>

                <div class="drop-zone" data-answer="11">
                  <div class="cup-top">المدى</div>
                  <div class="drop-area">اسحبي هنا</div>
                </div>
              </div>

              <div class="result-message" id="activity1Message"></div>

              <button class="btn btn-primary" id="toActivity2Btn" onclick="goToActivity2()" style="display:none; max-width:320px;">
                الانتقال إلى النشاط الثاني ⚡
              </button>
            </div>
          </div>
        </section>

        <section class="section" id="section-activity2">
          <div class="section-header">
            <div class="section-title">⚡ النشاط الثاني: اختيار من متعدد</div>
            <div class="chip">أسرع مجموعة تُسجّل في الصدارة</div>
          </div>

          <div class="question-card">
            <div class="question-number" id="questionNumber">السؤال 1</div>
            <div class="question-text" id="questionText"></div>
            <div class="options" id="optionsContainer"></div>

            <div class="progress-wrap">
              <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
              </div>
              <div class="progress-text" id="progressText">التقدم: 0 / 4</div>
            </div>
          </div>
        </section>

        <section class="section" id="section-finish">
          <div class="finish-card">
            <h2>🎉 أحسنتم يا نجمات الرياضيات!</h2>
            <p id="finishMessage"></p>
            <button class="btn btn-primary" style="max-width:320px; margin:auto;" onclick="restartLesson()">
              إعادة الدرس من البداية 🔄
            </button>
          </div>
        </section>
      </main>
    </div>

    <footer>
      تصميم وبرمجة المحتوى: أخصائية مركز مصادر التعلّم الأستاذة سامية المقبالية
    </footer>
  </div>

  <script>
    let currentGroup = "";
    let timerInterval = null;
    let secondsElapsed = 0;
    let activity1Solved = 0;
    let activity2Index = 0;
    let activity2Correct = 0;

    const questions = [
      {
        text: "إذا كان المنوال للقيم: ٥ ، ٩ ، ٢١ ، ١٧ ، ٣س هو ٢١، فما قيمة س؟",
        options: ["٧", "٩", "٢١", "٢٧"],
        correct: "٧"
      },
      {
        text: "المدى للقيم الآتية: ١٩ ، ٢٦ ، ١٧ ، ٣٢ ، ٢٦ يساوي:",
        options: ["١٥", "١٦", "٢٤", "٢٦"],
        correct: "١٥"
      },
      {
        text: "يعرض الإطار أطوال ستة أشخاص بالمتر: ١٫٤٢ ، ١٫٥٤ ، ١٫٥٤ ، ١٫٦٥ ، ١٫٧٠ ، ١٫٧٢. قيمة المدى تساوي:",
        options: ["٠٫٣٠", "٠٫٤٢", "٠٫٧٢", "١٫٥٤"],
        correct: "٠٫٣٠"
      },
      {
        text: "إذا كان الوسط الحسابي للقيم: ٣ ، ٤ ، ٧ ، ١٠ ، س يساوي ٦، فما قيمة س؟",
        options: ["٤", "٦", "٨", "١٠"],
        correct: "٦"
      }
    ];

    function showSection(id) {
      document.querySelectorAll(".section").forEach(sec => sec.classList.remove("active"));
      document.getElementById(id).classList.add("active");
    }

    function setStatus(text) {
      document.getElementById("statusText").textContent = text;
    }

    function updateTimerDisplay() {
      const min = String(Math.floor(secondsElapsed / 60)).padStart(2, "0");
      const sec = String(secondsElapsed % 60).padStart(2, "0");
      document.getElementById("timerDisplay").textContent = `${min}:${sec}`;
    }

    function startTimer() {
      clearInterval(timerInterval);
      secondsElapsed = 0;
      updateTimerDisplay();
      timerInterval = setInterval(() => {
        secondsElapsed++;
        updateTimerDisplay();
      }, 1000);
    }

    function stopTimer() {
      clearInterval(timerInterval);
    }

    function formatTime(seconds) {
      const min = Math.floor(seconds / 60);
      const sec = seconds % 60;
      return min > 0 ? `${min}د ${sec}ث` : `${sec}ث`;
    }

    async function saveScore(activity, groupName, seconds) {
      await fetch("/save_score", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          activity: activity,
          group_name: groupName,
          seconds: seconds
        })
      });
    }

    async function fetchLeaderboard(activity) {
      const response = await fetch(`/leaderboard/${activity}`);
      return await response.json();
    }

    async function renderLeaderboards() {
      const activity1 = await fetchLeaderboard("activity1");
      const activity2 = await fetchLeaderboard("activity2");
      renderSingleList("leaderboard1", activity1);
      renderSingleList("leaderboard2", activity2);
    }

    function renderSingleList(elementId, data) {
      const list = document.getElementById(elementId);
      list.innerHTML = "";

      if (!data.length) {
        list.innerHTML = `<li><span>لا توجد نتائج بعد</span><span>—</span></li>`;
        return;
      }

      data.forEach((item, index) => {
        const li = document.createElement("li");
        li.innerHTML = `<span>${index + 1}. ${item.group_name}</span><span>${formatTime(item.seconds)}</span>`;
        list.appendChild(li);
      });
    }

    async function clearLeaderboard(activity) {
      const ok = confirm("هل تريدين مسح المشاركين لهذه الصدارة؟");
      if (!ok) return;

      await fetch(`/clear_leaderboard/${activity}`, {
        method: "POST"
      });

      await renderLeaderboards();
    }

    function resetActivity1Board() {
      document.getElementById("scoopsContainer").innerHTML = `
        <div class="scoop green" draggable="true" data-value="7">٧</div>
        <div class="scoop purple" draggable="true" data-value="6">٦</div>
        <div class="scoop pink" draggable="true" data-value="4">٤</div>
        <div class="scoop blue" draggable="true" data-value="3">٣</div>
        <div class="scoop brown" draggable="true" data-value="11">١١</div>
      `;

      document.querySelectorAll(".drop-area").forEach(area => {
        area.innerHTML = "اسحبي هنا";
      });

      document.getElementById("activity1Message").className = "result-message";
      document.getElementById("activity1Message").style.display = "none";
      document.getElementById("toActivity2Btn").style.display = "none";

      enableDragDrop();
    }

    function startLesson() {
      const name = document.getElementById("groupName").value.trim();
      if (!name) {
        alert("من فضلك أدخلي اسم المجموعة أولًا.");
        return;
      }

      currentGroup = name;
      activity1Solved = 0;
      activity2Index = 0;
      activity2Correct = 0;

      resetActivity1Board();
      showSection("section-activity1");
      startTimer();
      setStatus(`بدأت المجموعة: ${currentGroup} النشاط الأول 🍦`);
    }

    function enableDragDrop() {
      const scoops = document.querySelectorAll(".scoop");
      const zones = document.querySelectorAll(".drop-zone");

      scoops.forEach(scoop => {
        scoop.addEventListener("dragstart", () => {
          scoop.classList.add("dragging");
        });

        scoop.addEventListener("dragend", () => {
          scoop.classList.remove("dragging");
        });
      });

      zones.forEach(zone => {
        zone.addEventListener("dragover", e => {
          e.preventDefault();
          zone.classList.add("over");
        });

        zone.addEventListener("dragleave", () => {
          zone.classList.remove("over");
        });

        zone.addEventListener("drop", async e => {
          e.preventDefault();
          zone.classList.remove("over");

          const dragged = document.querySelector(".dragging");
          if (!dragged) return;

          const value = dragged.dataset.value;
          const answer = zone.dataset.answer;
          const msg = document.getElementById("activity1Message");

          if (zone.querySelector(".drop-area .scoop")) {
            msg.className = "result-message error";
            msg.textContent = "هذا الكوب تم تعبئته بالفعل.";
            return;
          }

          if (value === answer) {
            zone.querySelector(".drop-area").innerHTML = "";
            const placed = dragged.cloneNode(true);
            placed.classList.remove("dragging");
            placed.setAttribute("draggable", "false");
            zone.querySelector(".drop-area").appendChild(placed);
            dragged.remove();
            activity1Solved++;

            msg.className = "result-message success";
            msg.textContent = "أحسنتِ! إجابة صحيحة ✅";

            if (activity1Solved === 3) {
              stopTimer();
              await saveScore("activity1", currentGroup, secondsElapsed);
              await renderLeaderboards();
              msg.className = "result-message success";
              msg.textContent = `🎉 ممتاز! أنهت المجموعة ${currentGroup} النشاط الأول في ${formatTime(secondsElapsed)}.`;
              document.getElementById("toActivity2Btn").style.display = "block";
              setStatus(`أكملت المجموعة ${currentGroup} النشاط الأول 🍦`);
            }
          } else {
            msg.className = "result-message error";
            msg.textContent = "المكان غير صحيح، حاولي مرة أخرى ✖";
          }
        });
      });
    }

    function goToActivity2() {
      activity2Index = 0;
      activity2Correct = 0;
      showSection("section-activity2");
      startTimer();
      loadQuestion();
      setStatus(`بدأت المجموعة ${currentGroup} النشاط الثاني ⚡`);
    }

    function loadQuestion() {
      const q = questions[activity2Index];
      document.getElementById("questionNumber").textContent = `السؤال ${activity2Index + 1}`;
      document.getElementById("questionText").textContent = q.text;

      const optionsContainer = document.getElementById("optionsContainer");
      optionsContainer.innerHTML = "";

      q.options.forEach(option => {
        const btn = document.createElement("button");
        btn.className = "option-btn";
        btn.textContent = option;
        btn.onclick = () => checkAnswer(btn, option);
        optionsContainer.appendChild(btn);
      });

      updateProgress();
    }

    function updateProgress() {
      const total = questions.length;
      const current = activity2Index;
      const percent = (current / total) * 100;
      document.getElementById("progressFill").style.width = percent + "%";
      document.getElementById("progressText").textContent = `التقدم: ${current} / ${total}`;
    }

    function checkAnswer(button, selected) {
      const q = questions[activity2Index];
      const buttons = document.querySelectorAll(".option-btn");
      buttons.forEach(btn => btn.disabled = true);

      if (selected === q.correct) {
        button.classList.add("correct");
        activity2Correct++;
      } else {
        button.classList.add("wrong");
        buttons.forEach(btn => {
          if (btn.textContent === q.correct) {
            btn.classList.add("correct");
          }
        });
      }

      setTimeout(() => {
        activity2Index++;
        if (activity2Index < questions.length) {
          loadQuestion();
        } else {
          finishActivity2();
        }
      }, 1100);
    }

    async function finishActivity2() {
      stopTimer();
      await saveScore("activity2", currentGroup, secondsElapsed);
      await renderLeaderboards();

      document.getElementById("progressFill").style.width = "100%";
      document.getElementById("progressText").textContent = `التقدم: ${questions.length} / ${questions.length}`;

      document.getElementById("finishMessage").innerHTML =
        `أنهت المجموعة <strong>${currentGroup}</strong> النشاط الثاني في <strong>${formatTime(secondsElapsed)}</strong>.<br>` +
        `عدد الإجابات الصحيحة: <strong>${activity2Correct}</strong> من <strong>${questions.length}</strong> 🌟`;

      showSection("section-finish");
      setStatus(`انتهت المجموعة ${currentGroup} من النشاط الثاني وتم حفظ النتيجة 🏆`);
    }

    function restartLesson() {
      stopTimer();
      secondsElapsed = 0;
      updateTimerDisplay();
      currentGroup = "";
      activity1Solved = 0;
      activity2Index = 0;
      activity2Correct = 0;
      document.getElementById("groupName").value = "";
      resetActivity1Board();
      showSection("section-start");
      setStatus("أدخلي اسم المجموعة ثم ابدئي الدرس.");
    }

    enableDragDrop();
    renderLeaderboards();

    setInterval(renderLeaderboards, 5000);
  </script>
</body>
</html>
"""

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity TEXT NOT NULL,
            group_name TEXT NOT NULL,
            seconds INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/save_score", methods=["POST"])
def save_score():
    data = request.get_json(force=True)
    activity = (data.get("activity") or "").strip()
    group_name = (data.get("group_name") or "").strip()
    seconds = data.get("seconds")

    if activity not in ["activity1", "activity2"]:
      return jsonify({"success": False, "message": "نوع نشاط غير صحيح"}), 400

    if not group_name:
      return jsonify({"success": False, "message": "اسم المجموعة مطلوب"}), 400

    try:
      seconds = int(seconds)
    except Exception:
      return jsonify({"success": False, "message": "الزمن غير صحيح"}), 400

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO leaderboard (activity, group_name, seconds, created_at) VALUES (?, ?, ?, ?)",
        (activity, group_name, seconds, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/leaderboard/<activity>")
def leaderboard(activity):
    if activity not in ["activity1", "activity2"]:
        return jsonify([])

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT group_name, seconds
        FROM leaderboard
        WHERE activity = ?
        ORDER BY seconds ASC, id ASC
        LIMIT 10
    """, (activity,)).fetchall()
    conn.close()

    results = [{"group_name": row["group_name"], "seconds": row["seconds"]} for row in rows]
    return jsonify(results)

@app.route("/clear_leaderboard/<activity>", methods=["POST"])
def clear_leaderboard(activity):
    if activity not in ["activity1", "activity2"]:
        return jsonify({"success": False, "message": "نوع نشاط غير صحيح"}), 400

    conn = get_db_connection()
    conn.execute("DELETE FROM leaderboard WHERE activity = ?", (activity,))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)