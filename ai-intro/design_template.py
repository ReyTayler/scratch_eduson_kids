# -*- coding: utf-8 -*-
"""Каркас презентаций уроков вайб-кодинга в дизайн-системе Eduson Kids.

Использование: from deck_template import render_deck
render_deck(num, title, slides) -> полный HTML.
Слайд: {"notes": str, "html": str, "cls": "slide--violet"|"slide--green"|None}
Без cls слайд контентный (slide--content, белый, с номером страницы).
"""

CSS = r"""
/* ============ Дизайн-токены Eduson Kids ============ */
:root{
  --ek-violet:#8C7FF6; --ek-violet-soft:#A79EF9; --ek-violet-deep:#6F61E8; --ek-violet-bg:#F0EEFE;
  --ek-green:#3DF79D; --ek-green-soft:#7BF9BD; --ek-green-mint:#C9F7E3; --ek-green-pale:#E7FDF2; --ek-green-deep:#0FBF6E;
  --ek-ink:#17171C; --ek-gray:#8F8F98; --ek-gray-light:#EFEFF2; --ek-line:#E3E3EA;
  --ek-red:#FF6B6B; --ek-red-soft:#FF8A8A; --ek-red-deep:#E04848; --ek-red-pale:#FFECEC;
  --f-head:'Inter Tight','Inter','Segoe UI',system-ui,sans-serif;
  --f-body:'Inter','Segoe UI',system-ui,sans-serif;
  --f-mono:'JetBrains Mono','Cascadia Mono','Consolas',monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{font-family:var(--f-body);background:#E9E9F1;color:var(--ek-ink);-webkit-font-smoothing:antialiased}

/* ============ Хром: прогресс, счётчик, подсказка ============ */
.progress{position:fixed;top:0;left:0;right:0;height:4px;background:rgba(23,23,28,.08);z-index:100}
.progress__fill{height:100%;width:0%;background:var(--ek-violet);transition:width 300ms ease}
.counter{position:fixed;top:14px;right:18px;z-index:90;font:600 13px var(--f-body);color:var(--ek-gray);background:#fff;border:1px solid var(--ek-line);padding:6px 14px;border-radius:999px;font-variant-numeric:tabular-nums}
.counter b{color:var(--ek-ink)}
.hint{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);z-index:90;font:500 11px var(--f-body);color:var(--ek-gray);background:#fff;border:1px solid var(--ek-line);padding:6px 14px;border-radius:999px;letter-spacing:.03em}
.hint kbd{font-family:var(--f-mono);background:var(--ek-gray-light);padding:1px 6px;border-radius:4px;font-size:10px;margin:0 2px;color:var(--ek-ink)}

/* ============ Сцена 1280×720 ============ */
.stage{position:absolute;left:50%;top:50%;width:1280px;height:720px;transform:translate(-50%,-50%);border-radius:18px;overflow:hidden;box-shadow:0 30px 90px rgba(23,23,28,.18);background:#fff}
.slide{position:absolute;inset:0;background:#fff;opacity:0;transform:translateY(26px);transition:opacity 280ms ease,transform 280ms ease;pointer-events:none;font-family:var(--f-head)}
.slide.active{opacity:1;transform:none;pointer-events:auto}
.slide.prev{transform:translateY(-26px)}
.slide--violet{background:var(--ek-violet)}
.slide--green{background:var(--ek-green)}

/* Номер страницы на контентных слайдах */
.slide--content::after{content:attr(data-page);position:absolute;right:54px;bottom:30px;font:800 30px/1 var(--f-head);color:var(--ek-ink);opacity:.5}

/* ============ Декор «Орбита» ============ */
.sl-orbit{position:absolute;inset:0;pointer-events:none}
.slide--violet .sl-orbit{--decor:#A79EF9;--letter:#C4BEFA}
.slide--green .sl-orbit{--decor:#7BF9BD;--letter:#C4FCE0}
.sl-ring{position:absolute;left:50%;top:50%;width:1040px;height:660px;transform:translate(-50%,-50%);border:3px solid var(--decor);border-radius:50%;opacity:.9}
.sl-ico{position:absolute;color:var(--decor)}
.sl-letter{position:absolute;border-radius:50%;background:var(--decor);color:var(--letter);display:flex;align-items:center;justify-content:center;font:800 var(--fs,40px)/1 var(--f-head);font-style:normal}

/* ============ Каверы: карточка-окно и спич-бабл ============ */
.cover-center{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:2}
.cover-card{position:relative;width:860px;background:#fff;border-radius:28px;box-shadow:0 30px 80px rgba(23,23,28,.18)}
.card-top{display:flex;justify-content:space-between;align-items:center;padding:24px 30px 0}
.win-dots{display:flex;gap:9px}
.win-dots i{width:13px;height:13px;border-radius:50%;background:var(--ek-violet)}
.win-close{position:relative;width:22px;height:22px}
.win-close::before,.win-close::after{content:"";position:absolute;left:-1px;top:9px;width:24px;height:4px;border-radius:2px;background:var(--ek-violet)}
.win-close::before{transform:rotate(45deg)}
.win-close::after{transform:rotate(-45deg)}
.cover-card .badge{position:absolute;left:50%;top:-30px;transform:translateX(-50%) rotate(-4deg)}
.cover-card h1{padding:26px 64px 30px;text-align:center;font:800 50px/1.14 var(--f-head);letter-spacing:-.015em;color:var(--ek-ink)}
.cover-card .cover-sub{padding:0 80px 34px;text-align:center;font:500 19px/1.5 var(--f-body);color:#3C3C45}
.cover-card .cover-chips{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;padding:0 40px 40px}
.bubble{position:relative;width:660px;background:#EFEFF1;border-radius:30px;padding:56px 70px;text-align:center}
.bubble::after{content:"";position:absolute;right:56px;bottom:-24px;width:0;height:0;border-left:38px solid transparent;border-top:28px solid #EFEFF1}
.bubble h1{font:800 42px/1.25 var(--f-head);letter-spacing:-.01em;color:var(--ek-ink)}
.bubble p{margin-top:16px;font:500 18px/1.5 var(--f-body);color:#3C3C45}

/* ============ Стикер-бейдж и чипы ============ */
.badge{display:inline-block;background:var(--ek-green);color:var(--ek-ink);font:800 24px/1 var(--f-head);padding:13px 22px;border-radius:13px;transform:rotate(-3deg);box-shadow:0 10px 24px rgba(23,23,28,.10)}
.badge--violet{background:var(--ek-violet);color:#fff}
.badge--sm{font-size:16px;padding:9px 16px;border-radius:10px}
.chip{display:inline-block;font:700 14px/1 var(--f-body);padding:8px 14px;border-radius:999px;background:var(--ek-violet-bg);color:var(--ek-violet-deep)}
.chip--green{background:var(--ek-green-pale);color:var(--ek-green-deep)}
.chip--gray{background:var(--ek-gray-light);color:#3C3C45}

/* ============ Контентные слайды ============ */
.sl-body{position:absolute;inset:0;padding:56px 80px 62px;display:flex;flex-direction:column;gap:16px;overflow:hidden}
h2{font:800 38px/1.16 var(--f-head);letter-spacing:-.01em;color:var(--ek-ink)}
.acc{color:var(--ek-violet-deep)}
.sl-body>p, .col p{font:500 18px/1.5 var(--f-body);color:#3C3C45}
.code-chip{font-family:var(--f-mono);font-weight:700;font-size:.88em;background:var(--ek-violet-bg);color:var(--ek-violet-deep);padding:2px 8px;border-radius:8px;white-space:nowrap}
.hl{color:var(--ek-violet-deep);font-weight:700}
.out-chip{font-family:var(--f-mono);font-weight:700;font-size:.88em;background:var(--ek-green-pale);color:#0B7A48;padding:2px 8px;border-radius:8px;white-space:nowrap}

.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:22px;align-items:start}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;align-items:stretch}

.info-card{background:#F5F5F9;border-radius:18px;padding:18px 22px;font:500 16px/1.55 var(--f-body);color:#3C3C45}
.info-card h3{font:800 19px/1.3 var(--f-head);color:var(--ek-ink);margin-bottom:8px}
.ek-note{background:var(--ek-violet-bg);border-left:4px solid var(--ek-violet);border-radius:0 14px 14px 0;padding:14px 20px;font:600 17px/1.5 var(--f-body);color:#3C3560}
.ek-note--green{background:var(--ek-green-pale);border-left-color:var(--ek-green-deep);color:#0B5B39}
.ek-note--red{background:var(--ek-red-pale);border-left-color:var(--ek-red);color:#7A2E2E}

ul.clean{list-style:none;display:flex;flex-direction:column;gap:10px}
ul.clean li{display:flex;gap:14px;align-items:flex-start;font:500 17.5px/1.5 var(--f-body);color:#3C3C45}
ul.clean li::before{content:'—';flex:0 0 auto;color:var(--ek-violet-deep);font-weight:800}

ol.steps{list-style:none;counter-reset:step;display:flex;flex-direction:column;gap:12px}
ol.steps li{counter-increment:step;display:flex;gap:16px;align-items:center;padding:14px 20px;background:#F5F5F9;border-radius:16px;font:500 17.5px/1.45 var(--f-body);color:#2E2E36}
ol.steps li::before{content:counter(step);flex:0 0 40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;background:var(--ek-violet);font:800 18px var(--f-head);color:#fff}
ol.steps li:last-child::before{background:var(--ek-green);color:var(--ek-ink)}
ol.steps.steps--tight{gap:8px}
ol.steps.steps--tight li{padding:9px 16px;font-size:15.5px;gap:12px}
ol.steps.steps--tight li::before{flex-basis:32px;height:32px;font-size:14px}

.q-label{font:700 13px/1 var(--f-head);letter-spacing:.08em;text-transform:uppercase;color:var(--ek-gray)}

/* ============ План занятия (agenda) ============ */
.agenda{display:flex;flex-direction:column;gap:8px}
.agenda-row{display:flex;gap:16px;align-items:center;padding:10px 18px;background:#F5F5F9;border-radius:14px}
.agenda-row .t{flex:0 0 84px;text-align:center;font:800 14px/1 var(--f-mono);color:var(--ek-ink);background:var(--ek-green);border-radius:999px;padding:8px 0}
.agenda-row .tt{font:700 16.5px/1.3 var(--f-head);color:var(--ek-ink)}
.agenda-row .dd{font:500 14px/1.4 var(--f-body);color:var(--ek-gray)}

/* ============ Ключ-значение (привычки, шпаргалки) ============ */
.kv{display:flex;flex-direction:column}
.kv-row{display:grid;grid-template-columns:250px 1fr;gap:18px;align-items:start;padding:11px 4px;border-bottom:1.5px solid var(--ek-line)}
.kv-row:last-child{border-bottom:none}
.kv-row .k{font:800 14px/1.35 var(--f-head);letter-spacing:.05em;text-transform:uppercase;color:var(--ek-violet-deep);padding-top:2px}
.kv-row .v{font:500 16.5px/1.5 var(--f-body);color:#3C3C45}

/* ============ Окно кода (статичное) ============ */
.code-win{background:#fff;border:2.5px solid var(--ek-ink);border-radius:16px;overflow:hidden;font-family:var(--f-mono);box-shadow:10px 10px 0 rgba(140,127,246,.14)}
.code-head{display:flex;align-items:center;justify-content:space-between;padding:9px 16px;border-bottom:2px solid var(--ek-ink)}
.code-head .win-dots i{width:11px;height:11px}
.lang-badge{font:700 11px var(--f-mono);letter-spacing:.14em;color:var(--ek-gray)}
.code-body{padding:14px 20px;font:500 14.5px/1.6 var(--f-mono);color:var(--ek-ink);white-space:pre;overflow:auto;max-height:400px;tab-size:4}
.code-body .cm{color:var(--ek-gray)}
.code-body .st{color:var(--ek-green-deep)}
.code-body .kw{color:var(--ek-violet-deep);font-weight:700}

/* ============ Терминал (тёмное окно) ============ */
.term{background:var(--ek-ink);border-radius:16px;overflow:hidden;font-family:var(--f-mono);box-shadow:10px 10px 0 rgba(23,23,28,.12)}
.term-head{display:flex;align-items:center;justify-content:space-between;padding:9px 16px;border-bottom:1px solid rgba(255,255,255,.14)}
.term-head .win-dots i{width:11px;height:11px;background:var(--ek-green)}
.term-head .lang-badge{color:rgba(255,255,255,.5)}
.term-body{padding:14px 20px;font:500 14.5px/1.62 var(--f-mono);color:var(--ek-green);white-space:pre-wrap;word-break:break-word;overflow:auto;max-height:420px}
.term-body .usr{color:#fff}
.term-body .dim{color:rgba(255,255,255,.55)}

/* ============ Промпт-карточка (диалог с DeepSeek) ============ */
.prompt-card{position:relative;background:var(--ek-violet-bg);border:2.5px solid var(--ek-violet);border-radius:18px;padding:20px 26px 18px;box-shadow:10px 10px 0 rgba(140,127,246,.18)}
.prompt-card .pc-tag{position:absolute;top:-16px;left:22px;background:var(--ek-violet);color:#fff;font:800 14px/1 var(--f-head);padding:9px 16px;border-radius:10px;transform:rotate(-2deg);box-shadow:0 8px 18px rgba(23,23,28,.12)}
.prompt-card .pc-text{margin-top:6px;font:500 15px/1.62 var(--f-mono);color:#2E2A52;white-space:pre-wrap}
.prompt-card .pc-text .hl{color:var(--ek-violet-deep)}
.prompt-card--copy .pc-tag{background:var(--ek-green);color:var(--ek-ink)}

/* ============ Сравнение (vs) ============ */
.vs{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:stretch}
.vs-col{border-radius:18px;padding:20px 24px}
.vs-col h4{font:800 15px/1 var(--f-head);letter-spacing:.08em;text-transform:uppercase;margin-bottom:12px}
.vs-col p{font:500 16px/1.55 var(--f-body)}
.vs-col .note{margin-top:12px;font:500 13.5px/1.4 var(--f-body);opacity:.75}
.vs-col--plain{background:var(--ek-gray-light);color:#3C3C45}
.vs-col--plain h4{color:var(--ek-gray)}
.vs-col--win{background:var(--ek-green-pale);color:#124F35;border:2px solid var(--ek-green-soft)}
.vs-col--win h4{color:var(--ek-green-deep)}

/* ============ Квиз с раскрытием ответа ============ */
.quiz-box{background:#F5F5F9;border:2.5px solid var(--ek-ink);border-radius:18px;padding:22px 26px;box-shadow:10px 10px 0 rgba(61,247,157,.25)}
.quiz-box .q-num{display:inline-block;background:var(--ek-green);color:var(--ek-ink);font:800 13px/1 var(--f-head);letter-spacing:.08em;text-transform:uppercase;padding:8px 14px;border-radius:999px;margin-bottom:14px}
.quiz-box .q-text{font:700 21px/1.42 var(--f-head);color:var(--ek-ink)}
.quiz-answer{margin-top:16px}
.quiz-btn{border:0;border-radius:12px;padding:12px 22px;font:800 15px/1 var(--f-head);cursor:pointer;background:var(--ek-violet);color:#fff;transition:background .15s}
.quiz-btn:hover{background:var(--ek-violet-deep)}
.quiz-reveal{display:none;margin-top:14px;background:var(--ek-green-pale);border-left:4px solid var(--ek-green-deep);border-radius:0 14px 14px 0;padding:14px 20px;font:500 16.5px/1.55 var(--f-body);color:#0B5B39}
.quiz-reveal.show{display:block}
.quiz-reveal p+p{margin-top:8px}

/* Появление контента */
.slide.active .info-card,.slide.active ul.clean li,.slide.active ol.steps li,.slide.active .grid-2>*,.slide.active .grid-3>*,.slide.active .agenda-row,.slide.active .kv-row{animation:reveal 450ms ease backwards}
.slide.active .info-card:nth-child(2),.slide.active ul.clean li:nth-child(2),.slide.active ol.steps li:nth-child(2),.slide.active .grid-2>*:nth-child(2),.slide.active .grid-3>*:nth-child(2),.slide.active .agenda-row:nth-child(2),.slide.active .kv-row:nth-child(2){animation-delay:80ms}
.slide.active ul.clean li:nth-child(3),.slide.active ol.steps li:nth-child(3),.slide.active .grid-3>*:nth-child(3),.slide.active .agenda-row:nth-child(3),.slide.active .kv-row:nth-child(3){animation-delay:160ms}
.slide.active ol.steps li:nth-child(4),.slide.active .agenda-row:nth-child(4),.slide.active .kv-row:nth-child(4){animation-delay:240ms}
.slide.active ol.steps li:nth-child(5),.slide.active .agenda-row:nth-child(5),.slide.active .kv-row:nth-child(5){animation-delay:320ms}
.slide.active .agenda-row:nth-child(6),.slide.active ol.steps li:nth-child(6),.slide.active .kv-row:nth-child(6){animation-delay:400ms}
.slide.active .agenda-row:nth-child(7),.slide.active ol.steps li:nth-child(7),.slide.active .kv-row:nth-child(7){animation-delay:480ms}
@keyframes reveal{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@media (prefers-reduced-motion:reduce){.slide.active .info-card,.slide.active ul.clean li,.slide.active ol.steps li,.slide.active .grid-2>*,.slide.active .grid-3>*,.slide.active .agenda-row,.slide.active .kv-row{animation:none}}

/* ============ Заметки преподавателя ============ */
.notes{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid var(--ek-line);box-shadow:0 -16px 40px rgba(23,23,28,.10);padding:20px 40px;z-index:95;max-height:40vh;overflow-y:auto;transform:translateY(100%);transition:transform 300ms ease}
.notes.active{transform:translateY(0)}
.notes__header{font:800 11px var(--f-head);letter-spacing:.2em;text-transform:uppercase;color:var(--ek-violet-deep);margin-bottom:8px}
.notes__body{font:500 15px/1.55 var(--f-body);color:#3C3C45}

:focus-visible{outline:3px solid var(--ek-violet-soft);outline-offset:2px;border-radius:6px}
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(23,23,28,.15);border-radius:4px}
"""

SPRITE = r"""<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<symbol id="ek-i-trophy" viewBox="0 0 100 100"><path fill="currentColor" d="M24 16h52v12h8c6 0 10 4 10 10 0 15-11 25-23 27-3 5-8 9-14 10v8h14c4 0 7 3 7 7v4H22v-4c0-4 3-7 7-7h14v-8c-6-1-11-5-14-10C17 63 6 53 6 38c0-6 4-10 10-10h8V16zM24 36h-7c-2 0-4 2-4 4 0 8 5 15 12 18-1-5-1-10-1-16v-6zM76 36v6c0 6 0 11-1 16 7-3 12-10 12-18 0-2-2-4-4-4h-7z"/></symbol>
<symbol id="ek-i-heart" viewBox="0 0 100 100"><path fill="currentColor" d="M50 88C28 72 10 56 10 38 10 24 21 14 34 14c6 0 12 3 16 8 4-5 10-8 16-8 13 0 24 10 24 24 0 18-18 34-40 50z"/></symbol>
<symbol id="ek-i-star" viewBox="0 0 100 100"><path fill="currentColor" d="M50 8l12 27 29 3-22 20 6 29-25-15-25 15 6-29L9 38l29-3z"/></symbol>
<symbol id="ek-i-gem" viewBox="0 0 100 100"><path fill="currentColor" d="M30 12h40l18 24-38 52L12 36zM36 20l-12 16h20zM64 20l-8 16h20zM50 22l-9 14h18zM26 44l20 30-8-30zM62 44l-8 30 20-30zM46 44h8l-4 26z"/></symbol>
</defs></svg>"""

JS = r"""
/* ============ Автомасштаб сцены ============ */
(function(){
  'use strict';
  var stage = document.getElementById('deck');
  function fit(){
    var w = window.innerWidth, h = window.innerHeight;
    if (!w || !h) return;
    var s = Math.min(w / 1320, h / 780);
    if (document.fullscreenElement) s = Math.min(w / 1280, h / 720);
    stage.style.transform = 'translate(-50%,-50%) scale(' + s + ')';
    stage.style.borderRadius = document.fullscreenElement ? '0' : '18px';
  }
  window.addEventListener('resize', fit);
  document.addEventListener('fullscreenchange', fit);
  fit();
})();

/* ============ Навигация по слайдам ============ */
(function(){
  'use strict';
  var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));
  var total = slides.length;
  var idx = 0;
  document.getElementById('total').textContent = total;

  var progressEl = document.getElementById('progress');
  var currentEl = document.getElementById('current');
  var notesPanel = document.getElementById('notes');
  var notesBody = document.getElementById('notesBody');

  slides.forEach(function(s, i){
    if (s.classList.contains('slide--content')) s.setAttribute('data-page', i + 1);
  });

  function render(){
    slides.forEach(function(s, i){
      s.classList.remove('active', 'prev');
      if (i === idx) s.classList.add('active');
      else if (i < idx) s.classList.add('prev');
    });
    progressEl.style.width = ((idx + 1) / total * 100).toFixed(2) + '%';
    currentEl.textContent = idx + 1;
    notesBody.textContent = slides[idx].getAttribute('data-notes') || '—';
  }

  function go(n){ idx = Math.max(0, Math.min(total - 1, n)); render(); }
  function next(){ go(idx + 1); }
  function prev(){ go(idx - 1); }

  document.addEventListener('keydown', function(e){
    var active = document.activeElement;
    if (active && (active.isContentEditable || active.tagName === 'TEXTAREA' || active.tagName === 'INPUT')) return;
    switch (e.key){
      case 'ArrowRight': case 'PageDown': case ' ':
        e.preventDefault(); next(); break;
      case 'ArrowLeft': case 'PageUp':
        e.preventDefault(); prev(); break;
      case 'Home': e.preventDefault(); go(0); break;
      case 'End': e.preventDefault(); go(total - 1); break;
      case 'f': case 'F': case 'а': case 'А':
        e.preventDefault();
        if (!document.fullscreenElement){ if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen(); }
        else if (document.exitFullscreen) document.exitFullscreen();
        break;
      case 'n': case 'N': case 'т': case 'Т':
        e.preventDefault(); notesPanel.classList.toggle('active'); break;
      case 'Escape':
        if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen();
        notesPanel.classList.remove('active'); break;
    }
  });

  var tx = 0, ty = 0;
  document.addEventListener('touchstart', function(e){ tx = e.changedTouches[0].screenX; ty = e.changedTouches[0].screenY; }, { passive: true });
  document.addEventListener('touchend', function(e){
    var dx = e.changedTouches[0].screenX - tx, dy = e.changedTouches[0].screenY - ty;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)){ if (dx < 0) next(); else prev(); }
  }, { passive: true });

  document.addEventListener('click', function(e){
    if (e.target.closest('a,button,input,textarea,code,pre,[contenteditable],.code-win,.term,.prompt-card,.quiz-box,.notes')) return;
    var x = e.clientX, w = window.innerWidth;
    if (x < w * 0.25) prev();
    else if (x > w * 0.75) next();
  });

  render();
})();

/* ============ Квизы: показать ответ ============ */
(function(){
  'use strict';
  Array.prototype.slice.call(document.querySelectorAll('.quiz-btn')).forEach(function(btn){
    btn.addEventListener('click', function(e){
      e.stopPropagation();
      var box = btn.closest('.quiz-box');
      var reveal = box && box.querySelector('.quiz-reveal');
      if (!reveal) return;
      var shown = reveal.classList.toggle('show');
      btn.textContent = shown ? 'Скрыть ответ' : 'Показать ответ';
    });
  });
})();
"""


def render_deck(num: int, title: str, slides: list) -> str:
    out = []
    for i, s in enumerate(slides):
        cls = s.get('cls') or 'slide--content'
        classes = 'slide ' + cls + (' active' if i == 0 else '')
        notes = (s.get('notes') or '').replace('"', '&quot;')
        out.append('<section class="%s"\n  data-notes="%s">\n%s\n</section>' % (classes, notes, s['html']))
    body = '\n\n'.join(out)

    return """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Урок %d — %s | Eduson Kids</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@600;700;800;900&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap">

<style>%s</style>
</head>
<body>

<div class="progress"><div class="progress__fill" id="progress"></div></div>
<div class="counter"><b id="current">1</b> / <span id="total">%d</span></div>

<main class="stage" id="deck">
%s
</main>

<div class="notes" id="notes">
  <div class="notes__header">Заметки преподавателя &middot; N — скрыть</div>
  <div class="notes__body" id="notesBody">—</div>
</div>

<div class="hint"><kbd>←</kbd><kbd>→</kbd> слайды &middot; <kbd>N</kbd> заметки &middot; <kbd>F</kbd> весь экран</div>

%s

<script>%s</script>
</body>
</html>
""" % (num, title, CSS, len(slides), body, SPRITE, JS)
