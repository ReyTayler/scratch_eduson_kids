"""Собирает презентацию и HTML-сценарий: речь берётся из «Сценарий урока.md», экран описан здесь."""
import json, re
from html import escape as e
from pathlib import Path
import board

R = Path(__file__).resolve().parent
D = R/'dist'
D.mkdir(exist_ok=True)
md = (R/'Сценарий урока.md').read_text(encoding='utf-8')
N = 25

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
parsed[13]['prompt'] = 'https://alice.yandex.ru'

Q1 = '1. Какая планета ближе всех к Солнцу? Варианты: Венера, Меркурий, Марс.\n2. Какая планета самая большая? Варианты: Сатурн, Юпитер, Нептун.\n3. Какая планета третья по счёту от Солнца? Варианты: Земля, Марс, Венера.'
Q2 = '1. Какая планета ближе всех к Солнцу? А) Венера Б) Меркурий В) Марс. Ответ: Б.\n2. Какая планета самая большая? А) Сатурн Б) Юпитер В) Нептун. Ответ: А.\n3. Какая планета третья по счёту от Солнца? А) Земля Б) Марс В) Венера. Ответ: А.'
Q3 = '1. Какая планета ближе всех к Солнцу? А) Венера Б) Меркурий В) Марс. Ответ: Б.\n2. Какая планета пятая по счёту от Солнца? А) Юпитер Б) Сатурн В) Марс. Ответ: А.\n3. Какая планета третья по счёту от Солнца? А) Земля Б) Марс В) Венера. Ответ: А.'
fallback = {
    14: 'Учебный пример ответа без образца:\n\n' + Q1,
    15: 'Ответ после образца. Во втором вопросе специально ошибка:\n\n' + Q2,
    16: Q2 + '\n\nПроверка по источнику: 1 ✓, 2 ✗ (самая большая — Юпитер), 3 ✓.',
    18: 'Уточнение для этого случая: «Замени вопрос 2 на другой вопрос о том, какая планета по счёту от Солнца, которого ещё нет в квизе. Остальные вопросы оставь как есть. Напиши весь квиз целиком».\n\n' + Q3 + '\n\nПроверка: новый вопрос 2 ✓, Юпитер пятый от Солнца.',
    21: 'Учебный квиз для игры:\n\n' + Q3,
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

def hints(items):
    return '<div class="hints">' + ''.join(f'<span>{e(x)}</span>' for x in items) + '</div>'

def question(t):
    return f'<div class="lesson-question ek-note"><p>{e(t)}</p></div>'

def opt(label, ok):
    return f'<button type="button" class="qz-opt"{" data-ok=1" if ok else ""}>{e(label)}</button>'

def quiz(q, opts, fb):
    """Вопрос с вариантами: учитель нажимает ответ, вариант показывает результат."""
    wide = ' qz-wide' if sum(len(x) for x, _ in opts) > 30 else ''
    return f'<div class="qz qz-line{wide} ek-note"><div class="qz-text"><p class="qz-q">{e(q)}</p><p class="qz-fb">{e(fb)}</p></div><div class="qz-opts">' + ''.join(opt(a, b) for a, b in opts) + '</div></div>'

def qrow(text, opts, mark):
    return f'<div class="qz qz-row"><span class="qz-mark">{mark}</span><p>{e(text)}</p><div class="qz-opts">' + ''.join(opt(a, b) for a, b in opts) + '</div></div>'

def cards_quiz(items, fb):
    cards = ''.join(f'<button type="button" class="qz-opt qz-card"{" data-ok=1" if ok else ""}><b>{e(a)}</b></button>' for a, ok in items)
    return f'<div class="qz qz-big"><div class="qz-opts">{cards}</div><div class="strip qz-fb">{e(fb)}</div></div>'

def prompt_card(tag, text):
    return f'<div class="prompt-card"><span class="pc-tag">{e(tag)}</span><p class="pc-text">{e(text)}</p></div>'

def hw_card(tag, body, cls):
    return f'<div class="prompt-card hw-card hw-{cls}"><span class="pc-tag">{e(tag)}</span>{body}</div>'

def hw_steps(items):
    return '<ol class="hw-steps">' + ''.join(f'<li>{e(x)}</li>' for x in items) + '</ol>'

def card_list(title, items):
    return f'<div class="info-card"><h3>{e(title)}</h3><ul class="clean">' + ''.join(f'<li>{e(x)}</li>' for x in items) + '</ul></div>'

def agenda(rows):
    return '<div class="agenda">' + ''.join(f'<div class="agenda-row"><span class="t">{a}</span><div><div class="tt">{e(b)}</div><div class="dd">{e(c)}</div></div></div>' for a, b, c in rows) + '</div>'

def from_md(label):
    """Список пунктов карточки из сценария, чтобы цель и итоги не расходились со сценарием."""
    block = md.split(f'Карточка **{label}:**')[1].split('\n\n', 2)[1]
    return [x[2:].strip() for x in block.splitlines() if x.startswith('- ')]

GOAL = re.search(r'Формулировка цели: \*(.+?)\*', md)[1]
RESULT = re.search(r'Формулировка: \*(Цель достигнута.+?)\*', md)[1]
KNOW, DO, KNEW, DONE = from_md('Узнаете'), from_md('Сделаете'), from_md('Узнали'), from_md('Сделали')
assert KNOW == KNEW and len(DO) == len(DONE)

P14 = parsed[14]['prompt']; P15 = parsed[15]['prompt']; P18 = parsed[18]['prompt']
assert P14 and P15 and P18
MARKS = hints(['✓ да: совпало', '✗ нет: не совпало', '? нет в источнике'])

# Экран каждого слайда: блок, подводка, содержимое, вопрос.
S = {
 2: dict(block='agenda', body=agenda([('0–5', 'Начало', 'План и цель урока.'), ('5–10', 'Повторение', 'Домашнее задание и прошлый урок.'), ('10–27', 'Новая тема', 'Роль, образец, разговор в чате, проверка фактов, разминка.'), ('27–55', 'Практика', 'AI-квиз в Алисе AI.'), ('55–60', 'Итоги', 'Что получилось и домашнее задание.')])),
 3: dict(block='goals', body=f'<div class="ek-note">{e(GOAL)}</div><div class="grid-2">{card_list("Узнаете", KNOW)}{card_list("Сделаете", DO)}</div>'),
 4: dict(block='Повторение', body=''.join(qrow(t, [('Верно', ok), ('Неверно', not ok)], i) for i, (t, ok) in enumerate([('Токен — это всегда целое слово.', False), ('«Это для детей 8 лет» — это контекст промта.', True), ('В новом чате Алиса продолжает разговор из прошлого чата.', False), ('Если ответ не подошёл, его можно уточнить в том же чате.', True)], 1)), q=question('Какой промт вы чинили дома? Что изменилось в ответе?')),
 5: dict(block='Новая тема', lead='Роль — это то, кем нейросеть выступит в ответе. Например: учитель, редактор, критик или эксперт.', body=svg('s05-roles'), q=quiz('Какая просьба задаёт роль?', [('«Выступи в роли гида»', True), ('«Напиши 3 предложения»', False), ('«Это для младшего брата»', False)], 'Роль задаёт просьба «Выступи в роли гида». Две другие — это формат и контекст.')),
 6: dict(block='Новая тема', lead='Найдите в промте роль, цель, контекст и формат.', body=svg('s06-prompt-role'), q=question('Почему ведущий викторины, а не сказочник? Что изменится в ответе?')),
 7: dict(block='Новая тема', lead='Образец — это пример того, какой ответ вам нужен.', body=svg('s07-sample'), q=quiz('Что нейросеть возьмёт из образца?', [('Вопрос про паука', False), ('Форму: вопрос, 3 варианта, ответ', True)], 'Нейросеть возьмёт из образца форму: вопрос, три варианта и ответ. А тему задаёт промт: планеты.')),
 8: dict(block='Новая тема', lead='Найдите, что повторяется в образцах, и продолжите.', body=svg('s08-pattern')),
 9: dict(block='Новая тема', lead='В одном чате Алиса учитывает то, что было раньше в этом чате. Разные чаты не смешиваются.', body=svg('s09-chats'), q=quiz('Где Алиса поймёт просьбу «Ещё один вопрос»?', [('Чат 1', True), ('Чат 2', False)], 'В чате 1: там уже был разговор о викторине про планеты.') + strip('Имена, адреса и телефоны не пишем ни в одном чате')),
 10: dict(block='Новая тема', lead='Галлюцинация — это когда нейросеть пишет неправду так, будто это факт.', body=prompt_card('Ответ нейросети · пример написан для урока', 'Какая планета самая большая? Ответ: Сатурн.'), q=quiz('Как узнать, верен ли ответ?', [('Звучит уверенно — значит, верно', False), ('Спросить нейросеть ещё раз', False), ('Найти в надёжном источнике', True)], 'Нужно найти этот факт в надёжном источнике. Если спросить нейросеть ещё раз, это не проверка: ответ может быть другим.')),
 11: dict(block='Новая тема', lead='Надёжный источник — это энциклопедия, учебник или страница, которую проверил взрослый.', body=svg('s11-source') + ''.join(qrow(t, [('Совпало', i == 0), ('Не совпало', i == 1), ('Нет в источнике', i == 2)], l) for l, t, i in [('А', '«Самая большая планета — Сатурн.»', 1), ('Б', '«На Марсе есть вулканы.»', 2), ('В', '«Ближе всех к Солнцу — Меркурий.»', 0)])),
 12: dict(block='Новая тема', lead='В квизе вопрос 2 не прошёл проверку. Какая просьба заменит только его?', body=cards_quiz([('«Сделай вопросы лучше.»', False), ('«Замени вопрос 2 на вопрос о самой маленькой планете. Остальные оставь как есть.»', True)], 'Вторая: в ней сказано, какой вопрос заменить и на какой. Слово «лучше» каждый понимает по‑своему.') + strip('Свой неудачный вопрос к нейросети тоже можно заменить: напишите его другими словами')),
 13: dict(block='Практика', lead='AI-квиз — вопросы с вариантами ответов. Каждый ответ проверим по источнику.', body=svg('s13-start') + hints(['Ссылка в чате урока. Пока ничего не отправляем', 'Просят войти или ввести личные сведения? Позовите взрослого', 'Ответ странный или неприятный? Покажите взрослому', 'В ответе есть ссылка? Без взрослого не переходим'])),
 14: dict(block='Практика', lead='Скопируйте промт из чата урока. Замените слова в скобках, сотрите скобки и отправьте.', body=svg('s14-template') + hints(['Например: «Это для моих друзей». Настоящие имена не пишем']), q=question('Как Алиса оформила вопросы? Есть ли правильные ответы?')),
 15: dict(block='Практика', body=prompt_card('Промт в чате урока. Отправьте в тот же чат', P15) + svg('s15-check')),
 16: dict(block='Практика', lead='Найдите ответ каждого вопроса в источнике.', body=svg('s16-source') + MARKS + strip('Напишите в чат урока номер вопроса и результат: да, нет или нет в источнике')),
 18: dict(block='Практика', body=prompt_card('Промт в чате урока. Отправьте в тот же чат', P18) + svg('s18-flow') + strip('Вопрос не прошёл проверку? Замените его. Все вопросы совпали с источником? Можно заменить тот, что нравится меньше: это тоже тренировка')),
 19: dict(block='Практика', lead='Попросите ещё один вопрос для квиза. Промт напишите сами.', body=svg('s19-own') + strip('В тот же чат. Новый вопрос проверьте по источнику') + hints(['Алиса поняла не так? Напишите просьбу другими словами'])),
 20: dict(block='Практика', lead='Скопируйте квиз и вставьте его в чат урока.', body=svg('s20-save')),
 21: dict(block='Практика', lead='Автор читает вопрос и варианты. Остальные называют букву. Потом автор показывает ответ в источнике.', body=svg('s16-source'), q=question('Кто готов первым?')),
}
accents = {2: '60 минут', 3: 'урока', 4: '«Верно или неверно»', 5: 'в промте', 6: 'с ролью', 7: 'в промте', 8: '«Повторите по образцу»', 9: 'в одном чате', 10: 'но неверно', 11: 'по источнику', 12: 'неудачный вопрос', 13: 'практику', 14: 'с ролью', 15: 'в том же чате', 16: 'по источнику', 18: 'неудачный вопрос', 19: 'в том же чате', 20: 'квиз', 21: 'в квиз', 22: 'себя', 23: 'урока', 24: 'по образцу', 25: 'выглядеть'}
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
        row = ''.join(f'<span class="part part-{c}">{w}</span>' for c, w in [('role', 'Роль'), ('sample', 'Образец'), ('chat', 'Разговор в чате'), ('source', 'Проверка по источнику')])
        body = orbit() + f'<div class="cover-center"><div class="cover-card"><div class="badge">Урок №3</div>{chrome}<h1>{title}</h1><p class="cover-sub">Роль, образец и проверка фактов</p><div class="cover-parts">{row}</div></div></div>'
    elif n == 17:
        kind, cls = 'break', 'slide--green'
        body = orbit() + f'<div class="cover-center"><div class="bubble"><h1>{title}</h1>{svg("s17-pause")}{ol(["Посмотрите вдаль.", "Поднимите и опустите плечи.", "Потянитесь."])}</div></div>'
    elif n == 22:
        kind = 'exit'
        items = [('Зачем в промте роль и образец?', 'Роль говорит, кем нейросеть выступит в ответе. Образец показывает, каким должен быть ответ.'), ('Почему в том же чате можно написать коротко: «Ещё один вопрос»?', 'В одном чате Алиса учитывает то, что было раньше в этом чате.'), ('Нейросеть уверенно написала факт. Как узнать, верен ли он?', 'Найти его в надёжном источнике. Нет в источнике — значит, не проверен.')]
        lis = ''.join(f'<li class="tap" data-tap="{i}" role="button" tabindex="0"><div>{e(q)}<em class="reply" data-show="{i}">{e(a)}</em></div><span class="tap-chip" data-hide="{i}">{CHIP}</span></li>' for i, (q, a) in enumerate(items, 1))
        body = f'<div class="sl-waves" aria-hidden="true">{waves}</div><div class="sl-body wave-layout"><div class="q-label">Итоги · {p["minutes"]} мин</div><h2>{title}</h2><div class="visual"><ol class="steps">{lis}</ol></div></div>'
    elif n == 23:
        kind = 'results'
        v = f'<div class="ek-note ek-note--green">{e(RESULT)}</div>' + f'<div class="grid-2">{card_list("Узнали", KNEW)}{card_list("Сделали", DONE)}</div>' + question('Какой пункт вы хотели попробовать первым? Получилось?')
        body = f'<div class="corner-decor" aria-hidden="true"><svg viewBox="0 0 100 100"><use href="#ek-i-star"/></svg></div><div class="sl-body"><div class="q-label">{labels["results"]}</div><h2>{title}</h2><div class="visual">{v}</div></div>'
    elif n == 24:
        kind = 'home'
        hw = re.search(r'Промт: \*(Выступи в роли \[кого\].+?)\*', md)[1]
        v = prompt_card('Промт. Слова в скобках замените своими', hw) + '<p class="hw-note">Вместо [ваш пример] напишите короткий факт на другую тему, например: «У паука 8 ног».</p>' + hw_steps(['Откройте новый чат и отправьте промт со своей ролью и своим образцом.', 'Найдите каждый факт из ответа в статье и поставьте знак: ✓, ✗ или ?.', 'Факт со знаком ✗ или ? замените один раз в том же чате и проверьте новый.', 'Взрослый присылает преподавателю промт, три факта со знаками и название книги.'])
        body = f'<div class="corner-decor" aria-hidden="true"><svg viewBox="0 0 100 100"><use href="#ek-i-star"/></svg></div><div class="sl-body"><div class="q-label">{labels["home"]}</div><h2>{title}</h2><p class="lead">Возьмите дома детскую энциклопедию или книгу и выберите в ней статью.</p><div class="visual">{v}</div></div>'
    elif n == 25:
        kind = 'home-example'
        left = hw_card('Промт и ответ', '<p class="pc-text">Выступи в роли учёного. Расскажи 3 факта про кометы и астероиды для ученика 2 класса. Каждый факт — одно предложение, как в образце: У паука 8 ног.</p><p class="hw-reply"><b>Ответ:</b> 1. Комета — ледяной ком из замёрзших газов, камня и пыли, который летит вокруг Солнца.<br>2. Астероид — это звезда, которая упала с неба.<br>3. Хвост кометы всегда синий.</p>', 'no')
        right = hw_card('Проверка', '<ul class="hw-checks"><li><b>✓</b> 1: совпало с источником.</li><li><b>✗</b> 2: в источнике астероиды — каменные остатки с рождения Солнечной системы, а не звёзды.</li><li><b>?</b> 3: в тексте источника этого нет.</li></ul><p class="hw-reply"><b>Замена:</b> «Замени факты 2 и 3 на другие факты про кометы и астероиды. Остальные факты оставь как есть. Напиши все три факта целиком.»</p>', 'ok')
        v = '<p class="hw-note">Ответ в примере подготовлен для урока. У вас он будет другим. Источник примера: страницы NASA о кометах и астероидах.</p><div class="hw-example">' + left + '<span class="hw-go" aria-hidden="true">→</span>' + right + '</div>' + strip('Сегодня вы писали текстовые промты. На следующем уроке Алиса будет рисовать картинки по вашему описанию')
        body = f'<div class="corner-decor" aria-hidden="true"><svg viewBox="0 0 100 100"><use href="#ek-i-star"/></svg></div><div class="sl-body"><div class="q-label">{labels["home-example"]}</div><h2>{title}</h2><div class="visual">{v}</div></div>'
    else:
        d = S[n]; block = d['block']
        kind = block if block in labels else 'quiz' if 'qz-row' in d['body'] or 'qz-big' in d['body'] else 'fig' if 'fig' in d['body'] else 'cards'
        if n in (15, 18): kind = 'fig kind-revision'
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
TITLE = 'Текстовый промтинг. Часть 2'
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
data = [dict(title=parsed[n]['title'], kind=parsed[n]['kind'], prompt=parsed[n]['prompt'], fallback=fallback.get(n, '')) for n in range(1, N+1)]
data_json = json.dumps(data, ensure_ascii=False).replace('</', '<' + chr(92) + '/')
html = f'''{head(TITLE + " · Eduson Kids")}<body class="audience lesson-deck"><main class="stage" id="stage">{"".join(sections)}</main><div class="deck-toolbar"><button id="notesBtn" aria-expanded="false" aria-controls="notesPanel">Преподавателю</button><button id="fullBtn" aria-label="Весь экран">⛶</button></div><nav class="deck-controls" aria-label="Управление слайдами"><button id="prev" aria-label="Предыдущий слайд">←</button><span id="counter" aria-live="polite"></span><button id="next" aria-label="Следующий слайд">→</button></nav><aside id="notesPanel" class="speaker-panel" aria-label="Заметки преподавателя" hidden><header class="speaker-toolbar"><span>Преподавателю</span><div><button id="contentsBtn">Слайды</button><button id="fontDown" aria-label="Уменьшить шрифт заметок">А−</button><button id="fontUp" aria-label="Увеличить шрифт заметок">А+</button><button id="closeNotes" aria-label="Закрыть заметки">Закрыть ×</button></div></header><div id="notesScroll">{notes}</div><footer class="speaker-actions"><button id="copyPrompt" hidden>Скопировать для чата урока</button><button id="showFallback" hidden>Запасной учебный ответ</button><span id="copyStatus" role="status"></span></footer></aside><dialog id="contents"><div class="dialog-top"><h2>План урока · 60 минут</h2><button id="closeContents">Закрыть</button></div><nav>{nav}</nav></dialog><dialog id="fallback"><div class="dialog-top"><h2>Запасной учебный ответ</h2><button id="closeFallback">Закрыть</button></div><p class="fallback-text"></p><p>Это подготовленный текст, а не ответ сервиса. Скажите об этом детям.</p></dialog>{sprite}<script>const lessonData={data_json};</script><script>{js}</script></body></html>'''
(D/'index.html').write_text(board.inject(html, '#stage'), encoding='utf-8')

# ---------- сценарий для преподавателя в HTML: схемы вставлены после «На экране» ----------
SLIDE_SVG = {5: ['s05-roles'], 6: ['s06-prompt-role'], 7: ['s07-sample'], 8: ['s08-pattern'], 9: ['s09-chats'], 11: ['s11-source'], 13: ['s13-start'], 14: ['s14-template'], 15: ['s15-check'], 16: ['s16-source'], 17: ['s17-pause'], 18: ['s18-flow'], 19: ['s19-own'], 20: ['s20-save'], 21: ['s16-source']}
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
(R/'Сценарий урока.html').write_text(f'<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Сценарий: текстовый промтинг, часть 2</title><style>{style}</style></head><body><main>{md_html(md)}</main></body></html>', encoding='utf-8')
print(f'Собрано: {N} слайдов, минут:', sum(parsed[n]['minutes'] for n in parsed))
