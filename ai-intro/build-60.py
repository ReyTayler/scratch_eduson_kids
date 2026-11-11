"""Render the already authored script as a private presenter and public slides."""
import json, re
from html import escape as e
from pathlib import Path
R = Path(__file__).resolve().parent
D = R/'dist'
D.mkdir(exist_ok=True)
lesson=json.loads((R/'lesson-60.json').read_text(encoding='utf-8'))
slides=lesson['slides']
import runpy
import board
art_module=runpy.run_path(str(R/'slide-art-60.py'))
art=art_module['art']
cover_art=art_module['cover_art']
sprite=(R/'designbook-sprite.svg').read_text(encoding='utf-8')
waves=(R/'designbook-waves.svg').read_text(encoding='utf-8')
chrome='<div class="card-top"><span class="win-dots"><i></i><i></i><i></i></span><span class="win-close" aria-hidden="true"></span></div>'
def orbit(full=True):
    if not full:
        return '<div class="sl-orbit orbit-sparse" aria-hidden="true"><svg class="sl-ico" viewBox="0 0 100 100" style="left:-35px;top:450px;width:220px;height:220px"><use href="#ek-i-heart"/></svg><svg class="sl-ico" viewBox="0 0 100 100" style="left:1140px;top:28px;width:180px;height:180px"><use href="#ek-i-gem"/></svg></div>'
    return '''<div class="sl-orbit" aria-hidden="true"><i class="sl-ring"></i>
    <svg class="sl-ico" viewBox="0 0 100 100" style="left:75px;top:20px;width:150px;height:150px;transform:rotate(-10deg)"><use href="#ek-i-trophy"/></svg>
    <i class="sl-letter" style="left:466px;top:13px;width:78px;height:78px;--fs:36px">S</i>
    <svg class="sl-ico" viewBox="0 0 100 100" style="left:1040px;top:15px;width:130px;height:130px;transform:rotate(12deg)"><use href="#ek-i-heart"/></svg>
    <i class="sl-letter" style="left:68px;top:268px;width:100px;height:100px;--fs:46px">A</i>
    <i class="sl-letter" style="left:1137px;top:327px;width:95px;height:95px;--fs:44px">I</i>
    <svg class="sl-ico" viewBox="0 0 100 100" style="left:102px;top:532px;width:125px;height:125px;transform:rotate(-15deg)"><use href="#ek-i-star"/></svg>
    <i class="sl-letter" style="left:726px;top:613px;width:78px;height:78px;--fs:36px">N</i>
    <svg class="sl-ico" viewBox="0 0 100 100" style="left:1045px;top:540px;width:110px;height:110px;transform:rotate(8deg)"><use href="#ek-i-gem"/></svg></div>'''
accents={2:'60 минут',3:'урока',4:'нейросети',5:'и нейросеть',6:'на примерах',7:'обучение',8:'цвет?',9:'не хватает?',10:'догадкой',11:'новый текст?',12:'в чат?',14:'порядок работы',15:'Алису AI',16:'запрос',17:'ответ',18:'ответ',19:'сочинить',20:'свой запрос',21:'без подсказки',22:'урока',23:'своё',24:'выглядеть'}
labels={'agenda':'Agenda · план занятия','goals':'Цель · что будет в конце','results':'Итоги · что получилось','home':'Домашнее задание · около 15 минут','home-example':'Домашнее задание · пример'}
# Интерактив прямо на слайде: кнопки-ответы и вопросы с меткой «Нажмите». Пошагового показа нет.
QUIZ={7:[('Хватит',0),('Не хватит',1)],12:[('Нужен',0),('Не нужен',1)],14:[('1, 2, 3',0),('2, 3, 1',1),('3, 1, 2',0)]}
CHIP='<svg viewBox="0 0 14 18" aria-hidden="true"><path d="M0 0 L0 15 L4.2 11.2 L7 17.4 L9.6 16.2 L6.8 10.2 L12.6 10.2 Z" fill="#fff"/></svg>Нажмите'
sections=[]
for i,s in enumerate(slides):
    lead='' if s['kind'] in ['prompt','response','revision','practice','own','agenda','goals','results'] else f'<p class="lead">{e(s["lead"])}</p>'
    answer=''
    cls='slide--content'
    title=e(s['title'])
    if i+1 in accents: title=title.replace(e(accents[i+1]),'<span class="acc">'+e(accents[i+1])+'</span>')
    q=''
    if s['question'] and s['kind']!='results':
        if s['answer'] and i+1 in QUIZ:
            opts=''.join(f'<button type="button" class="qz-opt"{" data-ok=1" if ok else ""}>{e(a)}</button>' for a,ok in QUIZ[i+1])
            q=f'<div class="lesson-question ek-note qz qz-line"><div class="qz-text"><p class="qz-q">{e(s["question"])}</p><p class="qz-fb">{e(s["answer"])}</p></div><div class="qz-opts">{opts}</div></div>'
        elif s['answer'] and s['kind']=='exit':
            q=f'<div class="lesson-question ek-note"><p>{e(s["question"])}</p></div>'
        elif s['answer']:
            q=f'<div class="lesson-question ek-note qa tap" data-tap="a" role="button" tabindex="0"><div class="qa-text"><p>{e(s["question"])}</p><p class="qa-answer" data-show="a">{e(s["answer"])}</p></div><span class="tap-chip" data-hide="a">{CHIP}</span></div>'
        else:
            q=f'<div class="lesson-question ek-note"><p>{e(s["question"])}</p></div>'
    if s['kind']=='cover':
        cls='slide--violet'
        chips=''.join(f'<span class="chip">{e(a)}</span>' for a,b in s['cards'])
        body=orbit()+f'<div class="cover-center"><div class="cover-card"><div class="badge">Урок №1</div>{chrome}<h1>{title}</h1><p class="cover-sub">{e(s["lead"])}</p>{cover_art()}<div class="cover-chips">{chips}</div></div></div>'
    elif s['kind']=='break':
        cls='slide--green'
        details='<ol class="steps">'+''.join(f'<li>{e(b)}</li>' for a,b in s['cards'])+'</ol>'
        movement=''
        body=orbit()+f'<div class="cover-center"><div class="bubble"><h1>{title}</h1><p class="divider-lead">{e(s["lead"])}</p>{details}{movement}</div></div>'
    else:
        is_window=s['block']=='Практика' or s['kind'] in ['new-case','order']
        is_waves=s['kind'] in ['exit','feedback']
        label=labels.get(s['kind']) or f'{e(s["block"])} · {s["minutes"]} мин'
        label=f'<span class="badge badge--sm badge--violet">{label}</span>' if is_window else f'<div class="q-label">{label}</div>'
        visual=art(s)
        if s['kind']=='exit' and s['answer']:
            # Каждый вопрос нажимается отдельно, ответ появляется под ним.
            replies=[x.strip() for x in re.split(r'\s*\d\.\s+',s['answer']) if x.strip()]
            assert len(replies)==len(s['cards']),'ответов столько же, сколько вопросов'
            visual='<ol class="steps">'+''.join(f'<li class="tap" data-tap="{k}" role="button" tabindex="0"><div>{e(b)}<em class="reply" data-show="{k}">{e(r)}</em></div><span class="tap-chip" data-hide="{k}">{CHIP}</span></li>' for k,((a,b),r) in enumerate(zip(s['cards'],replies),1))+'</ol>'
        content=f'{label}<h2>{title}</h2>{lead}<div class="visual">{visual}</div>{q}'
        if is_window:
            cls='slide--violet slide--window'
            body=orbit(False)+f'<div class="lesson-window">{chrome}<div class="sl-body">{content}</div></div><span class="sl-pagenum">{i+1}</span>'
        else:
            decor=f'<div class="sl-waves" aria-hidden="true">{waves}</div>' if is_waves else '<div class="corner-decor" aria-hidden="true"><svg viewBox="0 0 100 100"><use href="#ek-i-star"/></svg></div>'
            body=decor+f'<div class="sl-body{ " wave-layout" if is_waves else ""}">{content}</div>'
    sections.append(f'<section class="slide {cls} kind-{s["kind"]}" data-index="{i}" data-page="{i+1}" aria-label="Слайд {i+1}: {e(s["title"])}" hidden>{body}{answer}</section>')
css='\n'.join((R/f).read_text(encoding='utf-8') for f in ['designbook-fonts.css','designbook-base.css','web-60.css','designbook-slides.css','interactive.css'])
js=(R/'web-60.js').read_text(encoding='utf-8')
audience=f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Введение в нейросети · Экран показа</title><style>{css}</style></head><body class="audience"><main class="stage" id="stage">{''.join(sections)}</main>{sprite}<script>{js}</script></body></html>'''
(D/'audience.html').write_text(board.inject(audience,'#stage'),encoding='utf-8')
def formatted(t):
    return ''.join('<p>'+re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',e(p))+'</p>' for p in t.split('\n\n'))
notes=''.join(f'<article class="speaker" data-index="{i}" hidden><h2>{e(s["title"])}</h2><div class="note-meta">{s["start"]:02}–{s["end"]:02} мин · {s["minutes"]} мин на слайд</div>{formatted(s["speech"])}<details><summary>Организация и ожидаемые ответы</summary><h3>Проведение</h3><p>{e(s["activity"])}</p><h3>Наблюдение</h3><p>{e(s["expected"])}</p><h3>Визуальное решение</h3><p>{e(s["visual"])}</p></details></article>' for i,s in enumerate(slides))
nav=''.join(f'<button class="jump" data-to="{i}"><span>{i+1:02}</span><span>{e(s["title"])}</span><small>{s["start"]:02}–{s["end"]:02}</small></button>' for i,s in enumerate(slides))
public_data=[{k:s[k] for k in ['title','start','end','minutes','answer','kind','lead']} for s in slides]
public_json=json.dumps(public_data,ensure_ascii=False).replace('</', '<'+chr(92)+'/')
html=f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Введение в нейросети · Eduson Kids</title><style>{css}</style></head><body class="audience lesson-deck"><main class="stage" id="stage">{''.join(sections)}</main><div class="deck-toolbar"><button id="notesBtn" aria-expanded="false" aria-controls="notesPanel">Преподавателю</button><button id="fullBtn" aria-label="Весь экран">⛶</button></div><nav class="deck-controls" aria-label="Управление слайдами"><button id="prev" aria-label="Предыдущий слайд">←</button><span id="counter" aria-live="polite"></span><button id="next" aria-label="Следующий слайд">→</button></nav><aside id="notesPanel" class="speaker-panel" aria-label="Заметки преподавателя" hidden><header class="speaker-toolbar"><span>Преподавателю</span><div><button id="contentsBtn">Слайды</button><button id="fontDown" aria-label="Уменьшить шрифт заметок">А−</button><button id="fontUp" aria-label="Увеличить шрифт заметок">А+</button><button id="closeNotes" aria-label="Закрыть заметки">Закрыть ×</button></div></header><div id="notesScroll">{notes}</div><footer class="speaker-actions"><button id="copyPrompt" hidden>Скопировать запрос</button><button id="showFallback" hidden>Учебная исправленная версия</button><span id="copyStatus" role="status"></span></footer></aside><dialog id="contents"><div class="dialog-top"><h2>План урока · 60 минут</h2><button id="closeContents">Закрыть</button></div><nav>{nav}</nav></dialog><dialog id="fallback"><div class="dialog-top"><h2>Учебная исправленная версия</h2><button id="closeFallback">Закрыть</button></div><p class="fallback-text">Кошка — домашнее животное. Она хорошо видит в темноте. Кошки любят много спать.</p><p>Ровно три предложения, ответ про кошку. Это подготовленный текст, а не ответ сервиса.</p></dialog>{sprite}<script>const lessonData={public_json};</script><script>{js}</script></body></html>'''
(D/'index.html').write_text(board.inject(html,'#stage'),encoding='utf-8')
print('Built slide-only deck with optional notes: 24 slides, 60 minutes. Public copy contains no notes.')
