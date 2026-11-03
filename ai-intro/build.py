import json,sys
from pathlib import Path
from html import escape as e
from design_template import CSS, SPRITE

here = Path(__file__).parent
root = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else here
slides = json.loads((root/'lesson.json').read_text(encoding='utf-8'))
cover = slides[0]
lesson_label = cover['tags'][1]
lesson_title = e(cover['title'])
orbit = '''<div class="sl-orbit" aria-hidden="true"><i class="sl-ring"></i><svg class="sl-ico" viewBox="0 0 100 100" style="left:60px;top:30px;width:150px;height:150px"><use href="#ek-i-trophy"/></svg><i class="sl-letter" style="left:480px;top:22px;width:78px;height:78px;--fs:36px">S</i><svg class="sl-ico" viewBox="0 0 100 100" style="right:60px;top:28px;width:130px;height:130px"><use href="#ek-i-heart"/></svg><i class="sl-letter" style="left:55px;top:330px;width:96px;height:96px;--fs:44px">A</i><i class="sl-letter" style="right:48px;top:330px;width:96px;height:96px;--fs:44px">I</i><svg class="sl-ico" viewBox="0 0 100 100" style="left:95px;bottom:40px;width:120px;height:120px"><use href="#ek-i-star"/></svg><svg class="sl-ico" viewBox="0 0 100 100" style="right:80px;bottom:40px;width:120px;height:120px"><use href="#ek-i-gem"/></svg></div>'''
chrome = '<div class="card-top"><span class="win-dots"><i></i><i></i><i></i></span><span class="win-close" aria-hidden="true"></span></div>'
out=[]
for i,s in enumerate(slides):
    kind=s['kind']; title=e(s['title']); text=e(s.get('text','')).replace('\n','<br>'); extra=e(s.get('extra',''))
    cls='slide--content'
    if kind=='cover':
        cls='slide--violet'
        body=orbit+'<div class="cover-center"><div class="cover-card"><div class="badge">'+e(s['badge'])+'</div>'+chrome+f'<h1>{title}</h1><p class="cover-sub">{text}</p><div class="cover-chips">'+''.join(f'<span class="chip">{e(t)}</span>' for t in s['tags'])+'</div></div></div>'
    elif kind=='final':
        cls='slide--green';body=orbit+f'<div class="cover-center"><div class="bubble"><h1>{title}</h1><p>{text}</p><p class="optional">{extra}</p></div></div>'
    else:
        body=f'<div class="sl-body"><div class="lesson-label">Scratch и нейросети <span>{e(lesson_label)}</span></div><h2>{title}</h2>'
        if kind in ['cards','compare']:
            if text: body+=f'<p>{text}</p>'
            body+=f'<div class="grid-{len(s["cards"])} card-row">'+''.join(f'<div class="info-card"><span class="card-num">0{n+1}</span><h3>{e(c[0])}</h3><p>{e(c[1])}</p></div>' for n,c in enumerate(s['cards']))+'</div>'
        elif kind=='goals':
            body+=f'<div class="goals"><div class="goal-card"><span class="goal-label">Цель урока</span><p>{e(s["goal"])}</p></div><div class="goal-list"><span class="goal-label">К концу урока вы</span><ul>'+''.join(f'<li>{e(t)}</li>' for t in s['outcomes'])+'</ul></div></div>'
        elif kind in ['big','break']:
            body+=f'<div class="statement">{text}</div>'
        elif kind in ['steps','work']:
            if text:body+=f'<p>{text}</p>'
            body+='<ol class="steps">'+''.join(f'<li>{e(t)}</li>' for t in s['items'])+'</ol>'
        elif kind=='quiz':
            body+=f'<div class="quiz-box" data-correct="{s["correct"]}"><p class="q-text">{text}</p><div class="options">'+''.join(f'<button class="option" data-answer="{n}"><span>{chr(65+n)}</span>{e(t)}</button>' for n,t in enumerate(s['options']))+f'</div><p class="feedback" aria-live="polite" data-answer="{e(s["answer"],quote=True)}"></p><button class="reset small" hidden>Попробовать снова</button></div>'
        elif kind=='reveal':
            body+=f'<div class="quiz-box"><p class="q-text">{text}</p><button class="reveal" aria-expanded="false">Обсудили? Открыть ответ</button><p class="reveal-text" hidden>{e(s["answer"])}</p></div>'
        elif kind=='sample':
            body+=f'<div class="sample-window">{chrome}<p>{text}</p></div>'
        elif kind=='prompt':
            body+=f'<p>{text}</p><div class="practice-prompt"><p>{e(s["prompt"])}</p><button class="copy-prompt">Скопировать запрос</button><span class="copy-status" aria-live="polite"></span></div>'
        elif kind=='worksheet':
            body+='<div class="worksheet">'+''.join(f'<label>{e(t)}<input maxlength="140" placeholder="Запишите выдуманную деталь" name="hero-{n}"></label>' for n,t in enumerate(s['fields']))+'</div><button id="saveHero">Сохранить карточку .txt</button>'
        if extra:body+=f'<div class="ek-note">{extra}</div>'
        if s.get('action'):
            body+='<div class="slide-actions">'
            for key in ['action','secondary']:
                if s.get(key):
                    a=s[key]
                    body+=f'<a class="action-link" href="{e(a["href"],quote=True)}" target="_blank" rel="noopener">{e(a["label"]) } ↗</a>'
            body+='</div>'
        body+='</div>'
    out.append(f'<section class="slide {cls}" data-page="{i+1}" aria-label="Слайд {i+1}: {title}" data-notes="{e(s["notes"],quote=True)}">{body}</section>')
extra_css=(here/'style.css').read_text(encoding='utf-8')
js=(here/'app.js').read_text(encoding='utf-8')
html='''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'''+lesson_title+''' · Eduson Kids</title><meta name="description" content="'''+e(cover['description'],quote=True)+'''"><style>'''+CSS+extra_css+'''</style></head><body><div class="progress"><div id="progress" class="progress__fill"></div></div><header class="toolbar"><span class="brand">eduson <b>kids</b></span><div><button id="menuBtn" aria-expanded="false">Содержание</button><button id="notesBtn" aria-expanded="false">Преподавателю</button><button id="fullBtn">Весь экран</button></div></header><main class="stage" id="deck">'''+''.join(out)+'''</main><footer class="controls"><button id="prev" aria-label="Предыдущий слайд">←</button><span id="counter" aria-live="polite"></span><button id="next" aria-label="Следующий слайд">→</button><span class="key-hint">← → слайды · N заметки · F весь экран</span></footer><aside id="notes" class="notes" aria-label="Заметки преподавателя" hidden><button class="close-panel" id="closeNotes">Закрыть ×</button><div class="notes__header">Преподавателю</div><p id="notesBody" class="notes__body"></p></aside><dialog id="contents"><div class="dialog-head"><h2>Содержание урока</h2><button id="closeMenu">Закрыть ×</button></div><nav>'''+''.join(f'<button data-slide="{i}"><b>{i+1:02}</b>{e(s["title"])}</button>' for i,s in enumerate(slides))+'''</nav></dialog>'''+SPRITE+f'<script>{js}</script></body></html>'
import board
(root/'dist/index.html').write_text(board.inject(html,'#deck'),encoding='utf-8')
md=[f"# {cover['title']}\n\n{lesson_label} · Возраст 7–9 лет · 45 минут\n"]
for i,s in enumerate(slides):
    md.append(f'\n## Слайд {i+1}. {s["title"]}\n')
    if s.get('goal'):md.append('**Цель урока:** '+s['goal']+'\n\n**К концу урока вы:**\n')
    for t in s.get('outcomes',[]):md.append('- '+t)
    for k in ['text','extra']:
        if s.get(k):md.append(s[k]+'\n')
    for c in s.get('cards',[]):md.append(f'- **{c[0]}**{"" if c[0][-1] in "?!" else "."} {c[1]}')
    for k in ['items','options','fields']:
        for t in s.get(k,[]):md.append('- '+t)
    if s.get('answer'):md.append('\nОтвет: '+s['answer'])
    if s.get('prompt'):md.append('\nЗапрос для отправки:\n\n'+s['prompt'])
    for key in ['action','secondary']:
        if s.get(key):md.append(f'\n{s[key]["label"]}: {s[key]["href"]}')
    md.append('\n**Преподавателю:** '+s['notes']+'\n')
(root/'Текст урока.md').write_text('\n'.join(md),encoding='utf-8')
print(f'Built {len(slides)} slides')
