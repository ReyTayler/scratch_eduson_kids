"""Собирает презентацию из сценария: речь берётся из «Сценарий урока.md», экран описан здесь."""
import json, re
from html import escape as e
from pathlib import Path
import board

R = Path(__file__).resolve().parent
D = R/'dist'
D.mkdir(exist_ok=True)
md = (R/'Сценарий урока.md').read_text(encoding='utf-8')

# ---------- сценарий ----------
parsed = {}
for sec in re.split(r'(?=^### Слайд \d+\.)', md, flags=re.M)[1:]:
    sec = re.split(r'^(?:---|## )', sec, flags=re.M)[0]
    n, title = re.match(r'### Слайд (\d+)\. (.*)', sec).groups()
    a, b = re.search(r'\*\*Время:\*\* (\d+)–(\d+)', sec).groups()
    screen = sec.split('**На экране:**')[1].split('**Текст для учителя:**')[0]
    speech = sec.split('**Текст для учителя:**')[1].split('**Действие:**')[0].strip()
    action = sec.split('**Действие:**')[1].strip()
    prompt = re.search(r'Промт для чата урока: `([^`]+)`', action)
    action = re.sub(r'\s*Промт для чата урока: `[^`]+`', '', action).strip()
    parsed[int(n)] = dict(title=title, start=int(a), end=int(b), minutes=int(b)-int(a), speech=speech,
                          action=action, prompt=prompt[1] if prompt else '',
                          screen=re.sub(r'!\[[^\]]*\]\([^)]*\)', '', screen).strip())
assert sorted(parsed) == list(range(1, 27))
parsed[13]['prompt'] = 'https://alice.yandex.ru'
parsed[14]['prompt'] = 'Придумай игру.'

BOLT3 = '1. Начало: робот Болт находит сломанную ракету.\n2. Что мешает: детали разбросаны по всей планете.\n3. Конец: ракета взлетает, и Болт машет всем рукой.'
BOLT4 = '1. Начало: робот Болт находит сломанную ракету.\n2. Что мешает: детали разбросаны по всей планете.\n3. Как справляется: Болт собирает детали с помощью магнита.\n4. Конец: ракета взлетает, и Болт машет всем рукой.'
fallback = {
    14: 'Игра «Собери яблоки». Игрок ходит по саду и собирает яблоки. За каждое яблоко он получает очко. Игра заканчивается, когда яблоки кончатся.',
    15: BOLT3, 16: BOLT3, 17: BOLT3,
    18: 'Уточнение для этого случая: «Добавь пункт: как герой справляется. Остальные пункты оставь как есть. Напиши весь сценарий целиком».\n\n' + BOLT4,
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
    return f'<div class="strip {cls}">{t}</div>'

def hints(items):
    return '<div class="hints">' + ''.join(f'<span>{e(x)}</span>' for x in items) + '</div>'

def question(t):
    return f'<div class="lesson-question ek-note"><p>{e(t)}</p></div>'

def opt(label, ok):
    return f'<button type="button" class="qz-opt"{" data-ok=1" if ok else ""}>{e(label)}</button>'

def quiz(q, opts, fb):
    """Вопрос с вариантами: учитель нажимает ответ, вариант показывает результат."""
    return f'<div class="qz qz-line ek-note"><div class="qz-text"><p class="qz-q">{e(q)}</p><p class="qz-fb">{e(fb)}</p></div><div class="qz-opts">' + ''.join(opt(a, b) for a, b in opts) + '</div></div>'

def qrow(text, opts, mark):
    return f'<div class="qz qz-row"><span class="qz-mark">{mark}</span><p>{e(text)}</p><div class="qz-opts">' + ''.join(opt(a, b) for a, b in opts) + '</div></div>'

def cards_quiz(items, fb):
    cards = ''.join(f'<button type="button" class="qz-opt qz-card"{" data-ok=1" if ok else ""}><b>{e(a)}</b><i>{e(c)}</i></button>' for a, c, ok in items)
    return f'<div class="qz qz-big"><div class="qz-opts">{cards}</div><div class="strip qz-fb">{e(fb)}</div></div>'

def hw_card(tag, prompt, reply, check, cls):
    return f'<div class="prompt-card hw-card hw-{cls}"><span class="pc-tag">{e(tag)}</span><p class="pc-text">{e(prompt)}</p><p class="hw-reply"><b>Ответ:</b> {e(reply)}</p><p class="hw-check"><b>Проверка:</b> {e(check)}</p></div>'

def card_list(title, items):
    return f'<div class="info-card"><h3>{e(title)}</h3><ul class="clean">' + ''.join(f'<li>{e(x)}</li>' for x in items) + '</ul></div>'

def agenda(rows):
    return '<div class="agenda">' + ''.join(f'<div class="agenda-row"><span class="t">{a}</span><div><div class="tt">{e(b)}</div><div class="dd">{e(c)}</div></div></div>' for a, b, c in rows) + '</div>'

GOAL = 'Составлять промт из трёх частей: цель, контекст, формат. Проверять ответ нейросети по этим частям и уточнять его в том же чате.'
KNOW = ['Что такое промт и токен', 'Как нейросеть выбирает следующий кусочек текста', 'Что такое цель, контекст и формат промта', 'Зачем промт уточняют несколько раз']
DO = ['Найти недостающую часть промта', 'Сравнить ответы на короткий и подробный промт', 'Составить сценарий игры в Алисе AI', 'Проверить ответ по частям промта', 'Уточнить ответ в том же чате', 'Написать промт без образца']
DONE = ['Найдена недостающая часть промта', 'Сравнены ответы на короткий и подробный промт', 'Составлен сценарий игры в Алисе AI', 'Ответ проверен по частям промта', 'Ответ уточнён в том же чате', 'Написан промт без образца']

# Экран каждого слайда: блок, подводка, содержимое, вопрос, ответ по пробелу.
S = {
 2: dict(block='agenda', body=agenda([('0–5', 'Начало', 'План и цель урока.'), ('5–10', 'Повторение', 'Домашнее задание и прошлый урок.'), ('10–27', 'Новая тема', 'Промт, токен, цель, контекст и формат, разминка.'), ('27–55', 'Практика', 'Сценарий игры в Алисе AI.'), ('55–60', 'Итоги', 'Что получилось и домашнее задание.')])),
 3: dict(block='goals', body=f'<div class="ek-note">{e(GOAL)}</div><div class="grid-2">{card_list("Узнаете", KNOW)}{card_list("Сделаете", DO)}</div>'),
 4: dict(block='Повторение', body=''.join(qrow(t, [('Верно', ok), ('Неверно', not ok)], i) for i, (t, ok) in enumerate([('Нейросеть обучают на примерах.', True), ('Нейросеть всегда знает ответ наверняка.', False), ('Если в примерах все семёрки зелёные, нейросеть может принять зелёную единицу за семёрку.', True), ('Если написать в чате «сделай короче», нейросеть обучается заново.', False), ('В чат можно писать свой домашний адрес.', False)], 1)), q=question('Что вы создали дома с Алисой? Что попросили изменить?')),
 5: dict(block='Новая тема', lead='Промт — текстовый запрос, по которому нейросеть составляет ответ.', body=svg('s05-flow'), q=question('Что вы просили у Алисы на прошлом уроке?')),
 6: dict(block='Новая тема', lead='Токен — кусочек текста: слово, часть слова или даже одна буква.', body=svg('s06-token'), q=quiz('В какой фразе больше подсказок?', [('Фраза 1', False), ('Фраза 2', True)], 'Во второй: рюкзак и учебники подсказывают. Это и есть контекст.')),
 7: dict(block='Новая тема', lead='Создатели нейросети Claude советуют представить её как умного, но нового сотрудника.', body=svg('s07-cakes'), q=quiz('Кондитер ошибся?', [('Да', False), ('Нет', True)], 'Нет: заказ он выполнил, а чего хотел заказчик, не знал.')),
 8: dict(block='Новая тема', lead='Проверка промта: поймёт ли его тот, кто не знает задумку?', body=svg('s08-live-prompt'), q=quiz('В каком промте вы точно знали, что показать?', [('Первый', False), ('Второй', True)], 'Во втором: в нём сказано, что именно нужно сделать.')),
 9: dict(block='Новая тема', body=svg('s09-three-parts'), q=quiz('«Торт на день рождения». Какая часть здесь «на день рождения»?', [('Цель', False), ('Контекст', True), ('Формат', False)], 'Контекст: это ситуация.')),
 10: dict(block='Новая тема', body=svg('s10-prompt-parts'), q=question('Что может измениться в ответе, если вместо брата написать «для взрослых на празднике»?')),
 11: dict(block='Новая тема', body=''.join(qrow(t, [('Цель', i == 0), ('Контекст', i == 1), ('Формат', i == 2)], l) for l, t, i in [('А', '«Придумай стихотворение про осень. Это для школьного праздника.»', 2), ('Б', '«Придумай стихотворение про осень. Напиши 4 строки.»', 1), ('В', '«Это для школьного праздника. Напиши 4 строки.»', 0)]), q=question('Как дополнить промт Б?')),
 12: dict(block='Новая тема', lead='Какое условие легко проверить?', body=cards_quiz([('«Напиши хорошо.»', '? ? ?', False), ('«Напиши 3 предложения.»', '1 · 2 · 3', True)], 'Второе: предложения можно посчитать, а слово «хорошо» каждый понимает по\u2011своему.')),
 13: dict(block='Практика', lead='Сценарий — это рассказ о том, что происходит в игре: начало, трудности, конец.', body=svg('s13-start') + hints(['Ссылка в чате урока. Пока ничего не отправляем', 'Просят войти или ввести личные сведения? Позовите взрослого', 'Ответ странный или неприятный? Покажите взрослому'])),
 14: dict(block='Практика', lead='Напишите в новом чате два слова. Отправьте. Дождитесь ответа.', body=svg('s14-short'), q=question('Что Алиса решила за вас?')),
 15: dict(block='Практика', lead='Начните новый чат. Скопируйте образец из чата урока, замените слова в скобках и сотрите скобки. Отправьте.', body=svg('s15-template') + hints(['Герой выдуманный. Настоящие имена не пишем'])),
 16: dict(block='Практика', body=svg('s16-compare'), q=question('В каком ответе больше вашей задумки: в первом или во втором?')),
 17: dict(block='Практика', body=svg('s17-check'), q=question('Всё совпало? Какой пункт сценария хочется изменить?')),
 18: dict(block='Практика', body='<div class="prompt-card"><span class="pc-tag">Образец в чате урока. Отправьте в тот же чат</span><p class="pc-text">Измени пункт [номер]: [что должно быть в нём]. Остальные пункты оставь как есть. Напиши весь сценарий целиком.</p></div>' + svg('s18-loop') + strip('Промт иногда приходится улучшать за несколько попыток')),
 19: dict(block='Практика', lead='Скопируйте последний ответ со сценарием и вставьте его в чат урока.', body=svg('s19-save')),
 21: dict(block='Практика', lead='У игры должно быть название. Напишите промт сами.', body=svg('s21-own') + strip('Новый чат. Отправьте. Выберите название и напишите его в чат урока. Личные сведения не пишем')),
 22: dict(block='Практика', body=svg('s22-show'), q=question('Какая это часть? 1 цель, 2 контекст, 3 формат')),
 26: dict(block='home-example', body='<p class="hw-note">Ответы в примере подготовлены для урока. У вас они будут другими.</p><div class="hw-example">' + hw_card('Как есть', 'Придумай имя для робота. Напиши 3 варианта.', 'Робик, Ботя, Винтик.', 'Непонятно, где и зачем этот робот: контекста нет.', 'no') + '<span class="hw-go" aria-hidden="true">→</span>' + hw_card('Починили', 'Придумай имя для робота. Он будет жить у нас дома и поливать цветы. Напиши 3 варианта.', 'Капелька, Поливайка, Росток.', 'Три варианта, имена про воду и цветы: подходят домашнему роботу-садовнику.', 'ok') + '</div>' + strip('Следующий урок: текстовый промтинг, часть 2. Роль и образец в промте, проверка фактов')),
}
accents = {2: '60 минут', 3: 'урока', 4: '«Верно или неверно»', 5: 'промт', 6: 'дальше?', 7: 'новичок', 8: '«Живой промт»', 9: 'промта', 10: 'промт', 11: 'не хватает?', 12: 'говорим точно', 13: 'практику', 14: 'промт', 15: 'из трёх частей', 16: 'два ответа', 17: 'ответ', 18: 'в том же чате', 19: 'сценарий', 21: 'без образца', 22: 'результат', 23: 'себя', 24: 'урока', 25: 'промт', 26: 'выглядеть'}
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

sections = []
for n in range(1, 27):
    p = parsed[n]; title = titled(n, p['title']); cls = 'slide--content'; kind = 'cards'
    if n == 1:
        kind, cls = 'cover', 'slide--violet'
        row = ''.join(f'<span class="part part-{i}"><b>{i}</b>{w}</span>' for i, w in enumerate(['Цель', 'Контекст', 'Формат'], 1))
        body = orbit() + f'<div class="cover-center"><div class="cover-card"><div class="badge">Урок №2</div>{chrome}<h1>{title}</h1><p class="cover-sub">Как написать хороший запрос к нейросети</p><div class="cover-parts">{row}<i>→</i><span class="part part-answer">Ответ</span></div></div></div>'
    elif n == 20:
        kind, cls = 'break', 'slide--green'
        body = orbit() + f'<div class="cover-center"><div class="bubble"><h1>{title}</h1>{svg("s20-pause")}{ol(["Посмотрите вдаль.", "Поднимите и опустите плечи.", "Потянитесь."])}</div></div>'
    elif n == 23:
        kind = 'exit'
        items = [('Какие три части промта мы сегодня разобрали?', 'Цель, контекст, формат.'), ('Зачем нейросети контекст?', 'Без него она не знает ситуацию. Контекст помогает ей подобрать ответ.'), ('«Придумай игру про кота. Напиши 3 пункта». Какой части не хватает?', 'Контекста: неизвестно, для кого и зачем игра.')]
        CHIP = '<svg viewBox="0 0 14 18" aria-hidden="true"><path d="M0 0 L0 15 L4.2 11.2 L7 17.4 L9.6 16.2 L6.8 10.2 L12.6 10.2 Z" fill="#fff"/></svg>Нажмите'
        lis = ''.join(f'<li class="tap" data-tap="{i}" role="button" tabindex="0"><div>{e(q)}<em class="reply" data-show="{i}">{e(a)}</em></div><span class="tap-chip" data-hide="{i}">{CHIP}</span></li>' for i, (q, a) in enumerate(items, 1))
        body = f'<div class="sl-waves" aria-hidden="true">{waves}</div><div class="sl-body wave-layout"><div class="q-label">Итоги · {p["minutes"]} мин</div><h2>{title}</h2><div class="visual"><ol class="steps">{lis}</ol></div></div>'
    elif n == 24:
        kind = 'results'
        v = '<div class="ek-note ek-note--green">Цель достигнута. Промт составлен из трёх частей: цель, контекст, формат. Ответ нейросети проверен по этим частям и уточнён в том же чате.</div>' + f'<div class="grid-2">{card_list("Узнали", KNOW)}{card_list("Сделали", DONE)}</div>' + question('Какой пункт вы хотели попробовать первым? Получилось?')
        body = f'<div class="corner-decor" aria-hidden="true"><svg viewBox="0 0 100 100"><use href="#ek-i-star"/></svg></div><div class="sl-body"><div class="q-label">{labels["results"]}</div><h2>{title}</h2><div class="visual">{v}</div></div>'
    elif n == 25:
        kind = 'home'
        prompts = [('А', '«Придумай считалку про котов. В неё будут играть малыши в детском саду.»'), ('Б', '«Придумай кличку для щенка. Напиши 5 вариантов.»'), ('В', '«Это для плаката в нашем классе. Напиши 2 предложения.»')]
        rows = ''.join(f'<div class="hw-row"><span class="qz-mark">{a}</span><p>{e(p)}</p></div>' for a, p in prompts)
        v = rows + strip('Отправьте промт как есть → в новом чате допишите недостающую часть → проверьте ответ по трём частям и уточните → сравните два ответа')
        body = f'<div class="corner-decor" aria-hidden="true"><svg viewBox="0 0 100 100"><use href="#ek-i-star"/></svg></div><div class="sl-body"><div class="q-label">{labels["home"]}</div><h2>{title}</h2><p class="lead">В каждом промте не хватает одной части. Выберите один.</p><div class="visual">{v}</div></div>'
    else:
        d = S[n]; block = d['block']
        kind = block if block in labels else 'quiz' if 'qz-row' in d['body'] or 'qz-big' in d['body'] else 'fig' if 'fig' in d['body'] else 'cards'
        if n == 18: kind = 'fig kind-revision'
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
    sections.append(f'<section class="slide {cls} kind-{kind}" data-index="{n-1}" data-page="{n}" aria-label="Слайд {n}: {e(p["title"])}" hidden>{body}</section>')

NB = re.compile(r'(?<![\w-])(в|и|с|к|о|у|а|на|не|по|за|из|для|от|до|что)\s(?=[\w«\[])', re.I)
def typo(html):
    return re.sub(r'>([^<]+)<', lambda m: '>' + NB.sub(lambda x: x[1] + chr(160), m[1]) + '<', html)
sections = [typo(x) for x in sections]
css = '\n'.join((R/f).read_text(encoding='utf-8') for f in ['designbook-fonts.css', 'designbook-base.css', 'web-60.css', 'designbook-slides.css', 'lesson.css'])
js = (R/'web.js').read_text(encoding='utf-8')
TITLE = 'Текстовый промтинг. Часть 1'
head = lambda t: f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{t}</title><style>{css}</style></head>'
audience = f'{head(TITLE + " · Экран показа")}<body class="audience"><main class="stage" id="stage">{"".join(sections)}</main>{sprite}<script>{js}</script></body></html>'
(D/'audience.html').write_text(board.inject(audience, '#stage'), encoding='utf-8')

def formatted(t):
    out = []
    for x in t.split('\n\n'):
        x = e(x, quote=False)
        x = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', x)
        x = re.sub(r'(?<!\*)\*(?!\*)(.+?)\*', r'<em>\1</em>', x)
        out.append(f'<p>{x}</p>')
    return ''.join(out)
notes = ''.join(f'<article class="speaker" data-index="{n-1}" hidden><h2>{e(parsed[n]["title"])}</h2><div class="note-meta">{parsed[n]["start"]:02}–{parsed[n]["end"]:02} мин · {parsed[n]["minutes"]} мин на слайд</div>{formatted(parsed[n]["speech"])}<details open><summary>Действие детей</summary><p>{e(parsed[n]["action"])}</p></details></article>' for n in range(1, 27))
nav = ''.join(f'<button class="jump" data-to="{n-1}"><span>{n:02}</span><span>{e(parsed[n]["title"])}</span><small>{parsed[n]["start"]:02}–{parsed[n]["end"]:02}</small></button>' for n in range(1, 27))
data = [dict(title=parsed[n]['title'], kind=parsed[n]['kind'], prompt=parsed[n]['prompt'], fallback=fallback.get(n, '')) for n in range(1, 27)]
data_json = json.dumps(data, ensure_ascii=False).replace('</', '<' + chr(92) + '/')
html = f'''{head(TITLE + " · Eduson Kids")}<body class="audience lesson-deck"><main class="stage" id="stage">{"".join(sections)}</main><div class="deck-toolbar"><button id="notesBtn" aria-expanded="false" aria-controls="notesPanel">Преподавателю</button><button id="fullBtn" aria-label="Весь экран">⛶</button></div><nav class="deck-controls" aria-label="Управление слайдами"><button id="prev" aria-label="Предыдущий слайд">←</button><span id="counter" aria-live="polite"></span><button id="next" aria-label="Следующий слайд">→</button></nav><aside id="notesPanel" class="speaker-panel" aria-label="Заметки преподавателя" hidden><header class="speaker-toolbar"><span>Преподавателю</span><div><button id="contentsBtn">Слайды</button><button id="fontDown" aria-label="Уменьшить шрифт заметок">А−</button><button id="fontUp" aria-label="Увеличить шрифт заметок">А+</button><button id="closeNotes" aria-label="Закрыть заметки">Закрыть ×</button></div></header><div id="notesScroll">{notes}</div><footer class="speaker-actions"><button id="copyPrompt" hidden>Скопировать для чата урока</button><button id="showFallback" hidden>Запасной учебный ответ</button><span id="copyStatus" role="status"></span></footer></aside><dialog id="contents"><div class="dialog-top"><h2>План урока · 60 минут</h2><button id="closeContents">Закрыть</button></div><nav>{nav}</nav></dialog><dialog id="fallback"><div class="dialog-top"><h2>Запасной учебный ответ</h2><button id="closeFallback">Закрыть</button></div><p class="fallback-text"></p><p>Это подготовленный текст, а не ответ сервиса. Скажите об этом детям.</p></dialog>{sprite}<script>const lessonData={data_json};</script><script>{js}</script></body></html>'''
(D/'index.html').write_text(board.inject(html, '#stage'), encoding='utf-8')
print('Собрано: 26 слайдов, минут:', sum(parsed[n]['minutes'] for n in parsed))
