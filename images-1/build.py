"""Собирает презентацию и HTML-сценарий: речь берётся из «Сценарий урока.md», экран описан здесь."""
import json, re
from html import escape as e
from pathlib import Path
import board

R = Path(__file__).resolve().parent
D = R/'dist'
D.mkdir(exist_ok=True)
md = (R/'Сценарий урока.md').read_text(encoding='utf-8')
N = 24

# ---------- сценарий ----------
parsed = {}
for sec in re.split(r'(?=^### Слайд \d+\.)', md, flags=re.M)[1:]:
    sec = re.split(r'^(?:---|## )', sec, flags=re.M)[0]
    n, title = re.match(r'### Слайд (\d+)\. (.*)', sec).groups()
    a, b = re.search(r'\*\*Время:\*\* (\d+)–(\d+)', sec).groups()
    speech = sec.split('**Текст для учителя:**')[1].split('**Действие:**')[0].strip()
    action = sec.split('**Действие:**')[1].strip()
    prompt = re.search(r'Промт для чата урока: `([^`]+)`', action)
    action = re.sub(r'\s*Промт для чата урока: `[^`]+`', '', action).strip()
    parsed[int(n)] = dict(title=title, start=int(a), end=int(b), minutes=int(b)-int(a), speech=speech,
                          action=action, prompt=prompt[1] if prompt else '')
assert sorted(parsed) == list(range(1, N+1)), sorted(parsed)
assert sum(p['minutes'] for p in parsed.values()) == 60
parsed[12]['prompt'] = 'https://alice.yandex.ru'

fallback = {
    14: ('fb-robot1', 'Нарисуй синего робота с гаечным ключом возле ракеты на красной планете. Стиль: мультфильм.'),
    15: ('fb-robot2', 'Оставь всё как есть, но сделай робота синим.'),
    18: ('fb-place', 'Нарисуй красную планету с камнями и ракетой. Стиль: мультфильм.'),
}

# ---------- рисунки ----------
def svg(name):
    s = (R/'svg'/f'{name}.svg').read_text(encoding='utf-8')
    s = re.sub(r'<g id="tap-(\w+)">', r'<g class="tap" data-tap="\1" role="button" tabindex="0">', s)
    s = re.sub(r'<g id="show-(\w+)">', r'<g data-show="\1">', s)
    s = re.sub(r'<g id="hide-(\w+)">', r'<g data-hide="\1">', s)
    return f'<div class="fig">{s}</div>'

def ol(items):
    return '<ol class="steps">' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>'

def strip(t, cls=''):
    return f'<div class="strip {cls}">{e(t)}</div>'

def question(t):
    return f'<div class="lesson-question ek-note"><p>{e(t)}</p></div>'

def opt(label, ok):
    return f'<button type="button" class="qz-opt"{" data-ok=1" if ok else ""}>{e(label)}</button>'

def quiz(q, opts, fb):
    """Вопрос с вариантами: учитель нажимает ответ, вариант показывает результат."""
    wide = ' qz-wide' if sum(len(x) for x, _ in opts) > 30 else ''
    buttons = ''.join(opt(a, b) for a, b in opts)
    return f'<div class="qz qz-line{wide} ek-note"><p class="qz-q">{e(q)}</p><div class="qz-opts">{buttons}</div><p class="qz-fb">{e(fb)}</p></div>'

def qrow(text, opts, mark, feedback):
    return f'<div class="qz qz-row"><span class="qz-mark">{mark}</span><div class="row-prompt"><p>{e(text)}</p><p class="qz-fb">{e(feedback)}</p></div><div class="qz-opts">' + ''.join(opt(a, b) for a, b in opts) + '</div></div>'

def cards_quiz(items, fb):
    cards = ''.join(f'<button type="button" class="qz-opt qz-card"{" data-ok=1" if ok else ""}><b>{e(a)}</b></button>' for a, ok in items)
    return f'<div class="qz qz-big"><div class="qz-opts">{cards}</div><div class="strip qz-fb">{e(fb)}</div></div>'

def prompt_card(tag, text):
    return f'<div class="prompt-card"><span class="pc-tag">{e(tag)}</span><p class="pc-text">{e(text)}</p></div>'

def card_list(title, items):
    return f'<div class="info-card"><h3>{e(title)}</h3><ul class="clean">' + ''.join(f'<li>{e(x)}</li>' for x in items) + '</ul></div>'

def agenda(rows):
    return '<div class="agenda">' + ''.join(f'<div class="agenda-row"><span class="t">{a}</span><div><div class="tt">{e(b)}</div><div class="dd">{e(c)}</div></div></div>' for a, b, c in rows) + '</div>'

def from_md(label):
    """Список пунктов карточки из сценария, чтобы цель и итоги не расходились со сценарием."""
    block = md.split(f'Карточка **{label}:**')[1].split('\n\n', 2)[1]
    return [x[2:].strip() for x in block.splitlines() if x.startswith('- ')]

GOAL = re.search(r'Формулировка цели: \*(.+?)\*', md)[1]
RESULT = re.search(r'Формулировка: \*(.+?)\*', md)[1]
KNOW, DO, KNEW, DONE = from_md('Узнаете'), from_md('Сделаете'), from_md('Узнали'), from_md('Сделали')
assert len(KNOW) == len(KNEW) and len(DO) == len(DONE)

assert parsed[13]['prompt'] and parsed[15]['prompt']
MARKS = '✓ совпало · ✗ не совпало'

# Экран каждого слайда: блок, подводка, содержимое, вопрос.
S = {
 2: dict(block='agenda', body=agenda([('0–5', 'Начало', 'План и цель урока.'), ('5–10', 'Повторение', 'Домашнее задание и прошлый урок.'), ('10–27', 'Новая тема', 'Как нейросеть рисует, промт, проверка и уточнение.'), ('27–54', 'Практика', 'Картинки к своей игре в Алисе AI.'), ('54–60', 'Итоги', 'Что получилось и домашнее задание.')])),
 3: dict(block='goals', body=f'<div class="ek-note">{e(GOAL)}</div><div class="grid-2">{card_list("Узнаете", KNOW)}{card_list("Сделаете", DO)}</div>'),
 4: dict(block='Повторение', lead='Какую роль и какой образец вы дали дома? Какой факт проверили и где его нашли?', body=''.join(qrow(t, [('Верно', ok), ('Неверно', not ok)], i, fb) for i, (t, ok, fb) in enumerate([
     ('Образец подсказывает, на какую тему писать.', False, 'Образец показывает форму ответа.'),
     ('В одном чате Алиса учитывает предыдущие сообщения.', True, 'Уточнение продолжает разговор в этом чате.'),
     ('Галлюцинация может звучать как достоверный факт.', True, 'Ответ может звучать убедительно и содержать ошибку.'),
     ('Если факта нет в источнике, он неверный.', False, 'Факт пока не проверен.')], 1))),
 5: dict(block='Новая тема', lead='YandexART училась на парах «картинка и описание».', body=svg('s05-pairs'), q=quiz('Может ли модель нарисовать кота на Луне, если такой пары ей не показывали?', [('Да', True), ('Нет', False)], 'Да. Из знакомых деталей может получиться новая картинка.')),
 6: dict(block='Новая тема', lead='Диффузионная модель шаг за шагом превращает шум в картинку.', body=svg('s06-noise'), q=question('Что меняется от первого кадра к последнему?')),
 7: dict(block='Новая тема', lead='Предмет — кто или что. Фон — где. Стиль — как нарисовано.', body=svg('s07-prompt'), q=question('Какие слова в промте описывают каждую часть?')),
 8: dict(block='Новая тема', body=svg('s08-compare'), q=quiz('«Нарисуй кота-космонавта». Что ещё нужно описать?', [('Где он и как нарисован', True), ('Кто на картинке', False)], 'Кто — уже сказано. Добавьте место и стиль.')),
 9: dict(block='Новая тема', body=prompt_card('Промт', 'Нарисуй трёх рыжих котов на Луне. Стиль — мультфильм.') +
     '<div class="picture-check">' + svg('s10-cats') + '<div class="checks">' +
     ''.join(qrow(t, [('Да', ok), ('Нет', not ok)], mark, fb) for mark, t, ok, fb in [
       ('1', 'Предмет: три рыжих кота?', False, 'Рыжих котов два.'),
       ('2', 'Фон: Луна?', True, 'Видна поверхность Луны.'),
       ('3', 'Стиль: мультфильм?', True, 'Коты нарисованы как в мультфильме.')]) +
     '</div></div>' + '<p class="picture-caption">Учебная картинка, нарисована для урока.</p>'),
 10: dict(block='Новая тема', body='<div class="dog-example">' +
     prompt_card('Промт', 'Нарисуй жёлтую собаку с табличкой «ПРИВЕТ» в лесу. Стиль — мультфильм.') + svg('s11-dog') +
     '</div><p class="picture-caption">Учебная картинка, нарисована для урока.</p>',
     q=quiz('Что не совпало с промтом?', [('Цвет собаки', False), ('Надпись на табличке', True), ('Место', False)], 'На табличке «ПРИВКТ». В промте просили «ПРИВЕТ».')),
 11: dict(block='Новая тема', lead='Просили трёх рыжих котов на Луне. Получилось два. Что написать в том же чате?', body=cards_quiz([
     ('«Сделай картинку лучше».', False), ('«Добавь третьего рыжего кота. Остальное оставь как есть».', True)], 'Здесь точно сказано, что изменить и что сохранить.') + strip('Сравните новую картинку с промтом ещё раз.')),
 12: dict(block='Практика', lead='Нарисуйте две картинки к игре — главного персонажа и место действия.', body=svg('s13-start') + '<ul class="safety-list"><li>Сценарий в чате урока. Нет сценария? Придумайте персонажа и место.</li><li>Взрослый рядом. Если нужен вход, он войдёт в аккаунт.</li><li>Имена и адреса не пишем. Фото людей не загружаем. Реальных людей не рисуем.</li><li>Странную картинку покажите взрослому. По ссылкам переходите вместе с ним.</li></ul>'),
 13: dict(block='Практика', lead='Скопируйте промт. Замените скобки и текст внутри своими словами. Отправьте.', body=svg('s14-template') + prompt_card('Пример', 'Нарисуй синего робота с ключом возле ракеты на красной планете. Стиль — мультфильм.')),
 14: dict(block='Практика', lead='Сравните картинку с промтом. В чат урока напишите, что не совпало.', body=svg('s15-check') + strip(MARKS) + '<ul class="safety-list"><li>Ответ текстом? Включите «Нарисовать картинку».</li><li>Картинка не появилась? Позовите преподавателя.</li><li>Алиса отказалась? Покажите промт взрослому.</li></ul>'),
 15: dict(block='Практика', body=prompt_card('Промт для уточнения', parsed[15]['prompt']) + svg('s16-flow') + strip('Всё совпало? Попробуйте добавить одну деталь.')),
 17: dict(block='Практика', lead='Вместе со взрослым сохраните картинку с персонажем.', body=svg('s18-save') + strip('Без Алисы Плюс картинки в чате хранятся 14 дней.')),
 18: dict(block='Практика', lead='В новом чате напишите свой промт для места действия.', body=svg('s19-own') + strip('Нарисуйте место без персонажа. Сверьте картинку с промтом.')),
 19: dict(block='Практика', lead='Сохраните место действия так же, как персонажа.', body=svg('s20-send') + strip('После урока взрослый отправит файлы и промты преподавателю.')),
 20: dict(block='Практика', lead='Закончите и сохраните свои картинки. Готовы? Покажите одну.', body=svg('s21-show'), q=question('Какая деталь совпала с вашим промтом?')),
}
accents = {2: '60 минут', 3: 'урока', 5: 'учится рисовать', 6: 'из шума', 8: 'для картинки', 11: 'уточнением', 21: 'себя', 22: 'урока', 23: 'два стиля'}
labels = {'agenda': 'Agenda · план занятия', 'goals': 'Цель · что будет в конце', 'results': 'Итоги · что получилось', 'home': 'Домашнее задание · около 15 минут', 'home-example': 'Домашнее задание · пример'}

sprite = (R/'designbook-sprite.svg').read_text(encoding='utf-8')
waves = (R/'designbook-waves.svg').read_text(encoding='utf-8')
chrome = '<div class="card-top"><span class="win-dots"><i></i><i></i><i></i></span><span class="win-close" aria-hidden="true"></span></div>'
def orbit(full=True):
    if not full:
        return '<div class="sl-orbit orbit-sparse" aria-hidden="true"><svg class="sl-ico" viewBox="0 0 100 100" style="left:-35px;top:450px;width:220px;height:220px"><use href="#ek-i-heart"/></svg><svg class="sl-ico" viewBox="0 0 100 100" style="left:1140px;top:28px;width:180px;height:180px"><use href="#ek-i-gem"/></svg></div>'
    return '''<div class="sl-orbit" aria-hidden="true"><i class="sl-ring"></i>
    <svg class="sl-ico" viewBox="0 0 100 100" style="left:75px;top:20px;width:150px;height:150px;transform:rotate(-10deg)"><use href="#ek-i-trophy"/></svg>
    <i class="sl-letter" style="left:466px;top:13px;width:78px;height:78px;--fs:36px">P</i>
    <svg class="sl-ico" viewBox="0 0 100 100" style="left:1040px;top:15px;width:130px;height:130px;transform:rotate(12deg)"><use href="#ek-i-heart"/></svg>
    <i class="sl-letter" style="left:68px;top:268px;width:100px;height:100px;--fs:46px">A</i>
    <i class="sl-letter" style="left:1137px;top:327px;width:95px;height:95px;--fs:44px">I</i>
    <svg class="sl-ico" viewBox="0 0 100 100" style="left:102px;top:532px;width:125px;height:125px;transform:rotate(-15deg)"><use href="#ek-i-star"/></svg>
    <i class="sl-letter" style="left:726px;top:613px;width:78px;height:78px;--fs:36px">T</i>
    <svg class="sl-ico" viewBox="0 0 100 100" style="left:1045px;top:540px;width:110px;height:110px;transform:rotate(8deg)"><use href="#ek-i-gem"/></svg></div>'''

def titled(n, t):
    t = e(t)
    return t.replace(e(accents[n]), f'<span class="acc">{e(accents[n])}</span>') if n in accents else t

CHIP = '<svg viewBox="0 0 14 18" aria-hidden="true"><path d="M0 0 L0 15 L4.2 11.2 L7 17.4 L9.6 16.2 L6.8 10.2 L12.6 10.2 Z" fill="#fff"/></svg>Нажмите'
sections = []
for n in range(1, N+1):
    p = parsed[n]; title = titled(n, p['title']); cls = 'slide--content'; kind = 'cards'
    if n == 1:
        kind, cls = 'cover', 'slide--violet'
        row = ''.join(f'<span class="part part-{c}">{w}</span>' for c, w in [('role', 'Предмет'), ('role', 'Фон'), ('role', 'Стиль'), ('role', 'Проверка по промту')])
        body = orbit() + f'<div class="cover-center"><div class="cover-card"><div class="badge">Урок №4</div>{chrome}<h1>{title}</h1><p class="cover-sub">Как описать картинку словами и проверить, что нарисовала нейросеть</p><div class="cover-parts">{row}</div></div></div>'
    elif n == 16:
        kind, cls = 'break', 'slide--green'
        body = orbit() + f'<div class="cover-center"><div class="bubble"><h1>{title}</h1>{svg("s17-pause")}{ol(["Посмотрите вдаль.", "Поднимите и опустите плечи.", "Потянитесь."])}</div></div>'
    elif n == 21:
        kind = 'exit'
        items = [('Чем промт для картинки отличается от промта для текста?', 'Он описывает, что будет видно на картинке.'), ('Что можно указать в промте для картинки?', 'Предмет, фон и стиль.'), ('Нашли несовпадение. Что делать?', 'Уточнить в том же чате и проверить новый результат.')]
        lis = ''.join(f'<li class="tap" data-tap="{i}" role="button" tabindex="0"><div>{e(q)}<em class="reply" data-show="{i}">{e(a)}</em></div><span class="tap-chip" data-hide="{i}">{CHIP}</span></li>' for i, (q, a) in enumerate(items, 1))
        body = f'<div class="sl-waves" aria-hidden="true">{waves}</div><div class="sl-body wave-layout"><div class="q-label">Итоги · {p["minutes"]} мин</div><h2>{title}</h2><div class="visual"><ol class="steps">{lis}</ol></div></div>'
    elif n == 22:
        kind = 'results'
        v = f'<div class="ek-note ek-note--green">{e(RESULT)}</div>' + f'<div class="grid-2">{card_list("Узнали", KNEW)}{card_list("Сделали", DONE)}</div>' + question('Какой шаг у вас получился? Какой ещё нужно потренировать?')
        body = f'<div class="corner-decor" aria-hidden="true"><svg viewBox="0 0 100 100"><use href="#ek-i-star"/></svg></div><div class="sl-body"><div class="q-label">{labels["results"]}</div><h2>{title}</h2><div class="visual">{v}</div></div>'
    elif n == 23:
        kind = 'home'
        hw = re.search(r'Промт: \*(Нарисуй \[кого или что.+?)\*', md)[1]
        v = prompt_card('Промт для первой картинки', hw) + ol([
            'Вместе со взрослым нарисуйте предмет в новом чате.',
            'Попросите нарисовать то же самое в другом стиле.',
            'Сравните картинки. Если пропала деталь, уточните.',
            'Взрослый отправит две картинки, промты и одну фразу о различии.'])
        body = f'<div class="sl-body"><div class="q-label">{labels["home"]}</div><h2>{title}</h2><p class="lead">Выберите животное, вещь или место. Рисуйте в Алисе AI вместе со взрослым.</p><div class="visual">{v}</div></div>'
    elif n == 24:
        kind = 'home-example'
        v = prompt_card('Что просили в обеих картинках', 'Зелёная черепаха с красным рюкзаком на берегу реки.') + svg('hw-pair')
        body = f'<div class="sl-body"><div class="q-label">{labels["home-example"]}</div><h2>{title}</h2><div class="visual">{v}</div>{question("Что изменилось, кроме стиля?")}{strip("Следующий урок — постер к игре.")}</div>'
    else:
        d = S[n]; block = d['block']
        kind = block if block in labels else 'quiz' if 'qz-row' in d['body'] or 'qz-big' in d['body'] else 'fig' if 'fig' in d['body'] else 'cards'
        if n in (9, 10, 14, 17): kind = 'fig'
        lead = f'<p class="lead">{e(d["lead"])}</p>' if d.get('lead') else ''
        q = d.get('q', '')
        window = block == 'Практика'
        label = labels.get(block) or f'{block} · {p["minutes"]} мин'
        label = f'<span class="badge badge--sm badge--violet">{e(label)}</span>' if window else f'<div class="q-label">{e(label)}</div>'
        content = f'{label}<h2>{title}</h2>{lead}<div class="visual">{d["body"]}</div>{q}'
        if window:
            cls = 'slide--violet slide--window'
            body = orbit(False) + f'<div class="lesson-window">{chrome}<div class="sl-body">{content}</div></div><span class="sl-pagenum">{n}</span>'
        else:
            body = f'<div class="corner-decor" aria-hidden="true"><svg viewBox="0 0 100 100"><use href="#ek-i-star"/></svg></div><div class="sl-body">{content}</div>'
    p['kind'] = kind
    sections.append(f'<section class="slide {cls} kind-{kind} sl-{n}" data-index="{n-1}" data-page="{n}" aria-label="Слайд {n}: {e(p["title"])}" hidden>{body}</section>')

NB = re.compile(r'(?<![\w-])(в|и|с|к|о|у|а|на|не|по|за|из|для|от|до|что)\s(?=[\w«\[])', re.I)
def typo(html):
    return re.sub(r'>([^<]+)<', lambda m: '>' + NB.sub(lambda x: x[1] + chr(160), m[1]) + '<', html)
sections = [typo(x) for x in sections]
css = '\n'.join((R/f).read_text(encoding='utf-8') for f in ['designbook-fonts.css', 'designbook-base.css', 'web-60.css', 'designbook-slides.css', 'lesson.css'])
js = (R/'web.js').read_text(encoding='utf-8')
TITLE = 'Генерация изображений. Часть 1'
head = lambda t: f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{t}</title><style>{css}</style></head>'
audience = f'{head(TITLE + " · Экран показа")}<body class="audience"><main class="stage" id="stage">{"".join(sections)}</main>{sprite}<script>{js}</script></body></html>'
(D/'audience.html').write_text(board.inject(audience, '#stage'), encoding='utf-8')

def inline(x):
    x = e(x, quote=False)
    x = re.sub(r'`([^`]+)`', r'<code>\1</code>', x)
    x = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', x)
    x = re.sub(r'(?<!\*)\*(?!\*)(.+?)\*', r'<em>\1</em>', x)
    x = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', x)
    return x

def formatted(t):
    return ''.join(f'<p>{inline(x)}</p>' for x in t.split('\n\n'))
notes = ''.join(f'<article class="speaker" data-index="{n-1}" hidden><h2>{e(parsed[n]["title"])}</h2><div class="note-meta">{parsed[n]["start"]:02}–{parsed[n]["end"]:02} мин · {parsed[n]["minutes"]} мин на слайд</div>{formatted(parsed[n]["speech"])}<details open><summary>Действие детей</summary><p>{e(parsed[n]["action"])}</p></details></article>' for n in range(1, N+1))
nav = ''.join(f'<button class="jump" data-to="{n-1}"><span>{n:02}</span><span>{e(parsed[n]["title"])}</span><small>{parsed[n]["start"]:02}–{parsed[n]["end"]:02}</small></button>' for n in range(1, N+1))
data = [dict(title=parsed[n]['title'], kind=parsed[n]['kind'], prompt=parsed[n]['prompt'], fallback=fallback.get(n)) for n in range(1, N+1)]
data_json = json.dumps(data, ensure_ascii=False).replace('</', '<' + chr(92) + '/')
html = f'''{head(TITLE + " · Eduson Kids")}<body class="audience lesson-deck"><main class="stage" id="stage">{"".join(sections)}</main><div class="deck-toolbar"><button id="notesBtn" aria-expanded="false" aria-controls="notesPanel">Преподавателю</button><button id="fullBtn" aria-label="Весь экран">⛶</button></div><nav class="deck-controls" aria-label="Управление слайдами"><button id="prev" aria-label="Предыдущий слайд">←</button><span id="counter" aria-live="polite"></span><button id="next" aria-label="Следующий слайд">→</button></nav><aside id="notesPanel" class="speaker-panel" aria-label="Заметки преподавателя" hidden><header class="speaker-toolbar"><span>Преподавателю</span><div><button id="contentsBtn">Слайды</button><button id="fontDown" aria-label="Уменьшить шрифт заметок">А−</button><button id="fontUp" aria-label="Увеличить шрифт заметок">А+</button><button id="closeNotes" aria-label="Закрыть заметки">Закрыть ×</button></div></header><div id="notesScroll">{notes}</div><footer class="speaker-actions"><button id="copyPrompt" hidden>Скопировать для чата урока</button><button id="showFallback" hidden>Запасной учебный ответ</button><span id="copyStatus" role="status"></span></footer></aside><dialog id="contents"><div class="dialog-top"><h2>План урока · 60 минут</h2><button id="closeContents">Закрыть</button></div><nav>{nav}</nav></dialog><dialog id="fallback"><div class="dialog-top"><h2>Запасной учебный ответ</h2><button id="closeFallback">Закрыть</button></div><p class="fallback-text"></p><img class="fallback-image" alt="Учебная картинка"><p>Картинка нарисована для урока.</p><a class="fallback-open" target="_blank" rel="noopener">Открыть только учебную картинку</a></dialog>{sprite}<script>const lessonData={data_json};</script><script>{js}</script></body></html>'''
(D/'index.html').write_text(board.inject(html, '#stage'), encoding='utf-8')

# ---------- сценарий для преподавателя в HTML: схемы вставлены после «На экране» ----------
SLIDE_SVG = {5: ['s05-pairs'], 6: ['s06-noise'], 7: ['s07-prompt'], 8: ['s08-compare'], 9: ['s10-cats'], 10: ['s11-dog'], 12: ['s13-start'], 13: ['s14-template'], 14: ['s15-check'], 15: ['s16-flow'], 16: ['s17-pause'], 17: ['s18-save'], 18: ['s19-own'], 19: ['s20-send'], 20: ['s21-show'], 24: ['hw-pair']}
def md_html(src):
    out, lines, i, cur = [], src.split('\n'), 0, None
    while i < len(lines):
        L = lines[i]
        if L.startswith('### Слайд'):
            cur = int(re.match(r'### Слайд (\d+)', L)[1]); out.append(f'<h3>{inline(L[4:])}</h3>')
        elif L.startswith('#'):
            lvl = len(L) - len(L.lstrip('#')); out.append(f'<h{lvl}>{inline(L[lvl+1:])}</h{lvl}>'); cur = None
        elif L.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip('|').split('|')]); i += 1
            out.append('<table><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in rows[0]) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in rows[2:]) + '</table>'); continue
        elif re.match(r'^(- |\d+\. )', L):
            tag = 'ul' if L.startswith('- ') else 'ol'; items = []
            while i < len(lines) and re.match(r'^(- |\d+\. )', lines[i]):
                items.append(re.sub(r'^(- |\d+\. )', '', lines[i])); i += 1
            out.append(f'<{tag}>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + f'</{tag}>'); continue
        elif L.strip() == '---' or not L.strip():
            pass
        else:
            out.append(f'<p>{inline(L)}</p>')
            if L.startswith('**На экране:**') and cur in SLIDE_SVG:
                out += [f'<figure>{(R/"svg"/(s + ".svg")).read_text(encoding="utf-8")}</figure>' for s in SLIDE_SVG[cur]]
        i += 1
    return ''.join(out)
style = ''':root{--ink:#17171C;--v:#6F61E8;--vb:#F0EEFE;--line:#E3E3EA}html{color-scheme:light}*{box-sizing:border-box}h1,h2,h3{text-wrap:balance}figure{overflow-x:auto}body{margin:0;background:#fff;color:var(--ink);font:17px/1.55 Inter,'Segoe UI',Arial,sans-serif}main{max-width:900px;margin:0 auto;padding:32px 20px 80px}h1{font-size:36px;line-height:1.15;margin:0 0 12px}h2{font-size:25px;margin:44px 0 12px;color:var(--v)}h3{font-size:21px;margin:30px 0 8px;padding-top:18px;border-top:2px solid var(--line)}figure{margin:14px 0;padding:12px;border:1px solid var(--line);border-radius:14px}figure svg{display:block;width:100%;height:auto}table{border-collapse:collapse;width:100%;margin:12px 0}th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}th{background:var(--vb)}code{font:14px/1.5 Consolas,monospace;background:#EFEFF2;padding:2px 5px;border-radius:5px;word-break:break-word}a{color:var(--v)}li{margin:3px 0}p{margin:9px 0}'''
style += 'figure svg [id^="hide-"]{visibility:hidden}'
(R/'Сценарий урока.html').write_text(f'<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Генерация изображений. Часть 1 · Сценарий урока</title><style>{style}</style></head><body><main>{md_html(md)}</main></body></html>', encoding='utf-8')
print(f'Собрано: {N} слайдов, минут:', sum(parsed[n]['minutes'] for n in parsed))
