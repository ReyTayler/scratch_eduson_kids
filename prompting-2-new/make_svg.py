"""Рисует схемы урока в папку svg. Нажимаемые группы: tap-N, показ по нажатию: show-N, метка «Нажмите»: hide-N."""
from html import escape as e
from pathlib import Path

R = Path(__file__).resolve().parent
OUT = R/'svg'
OUT.mkdir(exist_ok=True)
INK, V, VB, G, GB, RED, RB, GRAY, LINE, LIGHT, MUTE = '#17171C', '#6F61E8', '#F0EEFE', '#0FBF6E', '#E7FDF2', '#E04848', '#FFECEC', '#5F5F6B', '#E3E3EA', '#EFEFF2', '#8F8F98'
FONT = 'Inter Tight, Inter, Arial, Helvetica, sans-serif'
WHITE, LAVENDER, MINT, GOLD, PEACH = '#FFFFFF', '#DCD7FF', '#BFF4D9', '#FFDE8A', '#FFD7C3'
DARK_V, DARK_G = '#4938AE', '#126248'


def t(x, y, s, size=24, w=600, fill=INK, a='start'):
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{a}">{e(s)}</text>'


def rect(x, y, w, h, fill='#F5F5F9', stroke='none', r=16, sw=3, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def path(d, fill='none', stroke='none', sw=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'


def circle(x, y, r, fill, stroke='none', sw=2):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def ellipse(x, y, rx, ry, fill):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}"/>'


def place(x, y, body, scale=1):
    return f'<g transform="translate({x} {y}) scale({scale})">{body}</g>'


def panel(x, y, w, h, fill=WHITE, edge=LINE, r=16):
    return rect(x, y + 4, w, h, edge, r=r, sw=0) + rect(x, y, w, h, fill, edge, r, 2)


def bars(x, y, widths, color=GRAY, gap=8, thickness=3):
    return ''.join(path(f'M{x} {y + i*gap}h{w}', stroke=color, sw=thickness) for i, w in enumerate(widths))


def tick(x, y, color=DARK_G, scale=1):
    return place(x, y, path('M-7 0l5 5 9-10', stroke=color, sw=3), scale)


def mini(kind, x, y, scale=1):
    """Учебные пиктограммы в общей сетке 48 × 48."""
    if kind == 'chat':
        b = path('M-20-14h40v26H-5l-9 7v-7h-6z', LAVENDER, DARK_V)
        b += bars(-11, -5, [21, 14], DARK_V)
    elif kind == 'edit':
        b = rect(-20, -17, 31, 35, WHITE, DARK_V, 5, 2) + bars(-13, -8, [14, 10], DARK_V)
        b += path('M-2 15l4-11 15-15 7 7-15 15z M13-7l7 7', GOLD, DARK_V)
    elif kind == 'book':
        b = path('M0-12c-9-6-15-6-21-4v30c7-2 13-1 21 4 8-5 14-6 21-4v-30c-6-2-12-2-21 4z', MINT, DARK_G)
        b += path('M0-12v30', stroke=DARK_G) + bars(-15, -6, [9, 9], DARK_G) + tick(11, 1, scale=.75)
    elif kind == 'list':
        b = rect(-18, -19, 36, 38, WHITE, DARK_V, 6, 2) + bars(-2, -9, [12, 12, 9], DARK_V, 9)
        b += ''.join(circle(-9, cy, 2, DARK_V) for cy in (-9, 0, 9))
    elif kind == 'planet':
        b = circle(0, 0, 14, GOLD, '#885026')
        b += path('M-14-1c6 4 22 4 28-2 M-11 7c7 2 15 2 21-1', stroke='#A66A38', sw=3)
        b += path('M-13-11c-9 3-14 8-10 12 4 5 22 7 37 3 10-3 12-8-1-13', stroke=DARK_V)
    else:
        b = rect(-16, -17, 32, 34, WHITE, DARK_V, 6, 2)
        b += path('M-8-7h16 M-8 0h7 M-8 7h7', stroke=DARK_V, sw=3) + tick(8, 7, scale=.65)
    return place(x, y, b, scale)


def num(x, y, n, fill, r=18):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>' + t(x, y + 8, str(n), 23, 700, '#FFFFFF', 'middle')


def person(x, y, fill='#FFFFFF', r=18):
    """Значок роли: голова и плечи в круге."""
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}"/><circle cx="{x}" cy="{y-5}" r="5.5" fill="{fill}"/><path d="M{x-9} {y+11} C{x-9} {y+1},{x+9} {y+1},{x+9} {y+11} Z" fill="{fill}"/>'


def arrow(x1, y1, x2, y2, color=MUTE, w=4):
    import math
    ang = math.atan2(y2 - y1, x2 - x1); c, s = math.cos(ang), math.sin(ang)
    p1 = (x2 - 14*c + 7*s, y2 - 14*s - 7*c); p2 = (x2 - 14*c - 7*s, y2 - 14*s + 7*c)
    return f'<line x1="{x1}" y1="{y1}" x2="{x2-6*c:.1f}" y2="{y2-6*s:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/><path d="M{x2} {y2} L{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f} Z" fill="{color}"/>'


def chip(x, y, n):
    """Метка «Нажмите», исчезает после нажатия."""
    return f'<g id="hide-{n}"><rect x="{x}" y="{y}" width="132" height="34" rx="17" fill="{V}"/><path d="M0 0 L0 15 L4.2 11.2 L7 17.4 L9.6 16.2 L6.8 10.2 L12.6 10.2 Z" fill="#FFFFFF" transform="translate({x+12} {y+8})"/>' + t(x + 32, y + 24, 'Нажмите', 20, 800, '#FFFFFF') + '</g>'


def raised(x, y, w, h, n, r=14):
    """Фиолетовый нижний край нажимаемого элемента: виден, пока элемент не открыт."""
    return f'<g id="hide-{n}">{rect(x, y + 6, w, h, V, r=r, sw=0)}</g>'


def svg(name, w, h, label, body):
    (OUT/f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}"><title>{e(label)}</title>{body}</svg>', encoding='utf-8')


# ---------- слайд 5: роли ----------
def icon(kind, cx, cy):
    if kind == 'board':
        b = path('M-23 17l-8 20 M23 17l8 20', stroke=INK, sw=4)
        b += rect(-40, -30, 80, 52, '#28675E', INK, 7, 3)
        b += path('M-26 5l8-15 9 15z M5-11h22 M5 0h16', stroke=MINT, sw=3)
        b += path('M-39 20h78 M17 17h10', stroke=GOLD, sw=4)
    elif kind == 'pencil':
        b = rect(-32, -34, 54, 69, WHITE, INK, 7, 3) + bars(-21, -20, [29, 24, 29, 16], V, 11)
        b += path('M-6 29l4-16 31-36q5-6 11-1l4 4q4 4 0 9L13 25z', GOLD, INK, 3)
        b += path('M-6 29l4-16 15 12z', PEACH, INK, 3) + path('M26-19l13 12 M4 17l29-32', stroke='#935C29', sw=2)
    elif kind == 'lens':
        b = rect(-30, -33, 53, 66, WHITE, INK, 6, 3) + bars(-21, -19, [27, 27, 22, 13], '#9984C2', 10)
        b += path('M16 13l23 22', stroke=INK, sw=13) + path('M16 13l23 22', stroke='#8B74E1', sw=7)
        b += circle(5, 1, 22, '#EEE7FF', INK, 3) + path('M-7 0a12 12 0 0 1 9-11', stroke=WHITE, sw=4)
        b += path('M2-7h6l-1 11H3z M5 10h.1', DARK_V, DARK_V, 3)
    else:
        b = path('M-16 9l-12 27 15-5 7 11 10-24 M14 9l12 27-15-5-7 11-9-24', MINT, '#385948', 3)
        b += circle(0, -7, 27, GOLD, '#8D5C32', 3) + circle(0, -7, 21, '#FFF0AE', '#C78B49', 2)
        b += path('M0-23l5 10 11 2-8 8 2 11L0 3l-10 5 2-11-8-8 11-2z', '#E99940', '#8D5C32')
    return place(cx, cy, b)


def net(cx, cy):
    pts = [(cx-38, cy-26), (cx-38, cy+26), (cx, cy-34), (cx, cy), (cx, cy+34), (cx+38, cy)]
    lines = ''.join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{V}" stroke-width="3"/>' for a in pts[:2] for b in pts[2:5]) + ''.join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{pts[5][0]}" y2="{pts[5][1]}" stroke="{V}" stroke-width="3"/>' for a in pts[2:5])
    plate = rect(cx - 59, cy - 52, 118, 104, '#DDD6FF', '#C7BCFD', 22, 2)
    pins = ''.join(path(f'M{cx+dx} {cy-58}v6 M{cx+dx} {cy+52}v6', stroke=V, sw=3) for dx in (-32, 0, 32))
    nodes = ''.join(circle(x, y, 9, WHITE, DARK_V, 3) + circle(x, y, 3, V) for x, y in pts)
    return pins + plate + lines + nodes


b = panel(15, 30, 200, 190, VB, '#C9BEFB') + net(115, 102) + t(115, 196, 'Нейросеть', 24, 800, INK, 'middle')
b += t(280, 104, 'выступает', 24, 600, GRAY, 'middle') + t(280, 132, 'в роли', 24, 600, GRAY, 'middle') + arrow(232, 150, 330, 150, V)
role_colors = [('#F0F9F5', '#D3EDE1', '#C8E9DA'), ('#FFF8EE', '#F2DEC1', '#FFE8BD'),
               ('#F7F1FF', '#E8D9FB', '#E6D7FF'), ('#F2F8FF', '#D8E6F7', '#DBEDFC')]
for i, (name, ic) in enumerate([('Учитель', 'board'), ('Редактор', 'pencil'), ('Критик', 'lens'), ('Эксперт', 'medal')]):
    x = 345 + i*162
    fill, edge, spot = role_colors[i]
    b += panel(x, 30, 148, 190, fill, edge) + circle(x + 74, 105, 53, spot)
    b += icon(ic, x + 74, 105) + t(x + 74, 196, name, 23, 800, INK, 'middle')
svg('s05-roles', 1000, 240, 'Одна нейросеть может выступить в разных ролях: учитель, редактор, критик, эксперт', b)

# ---------- слайд 6: промт с ролью, строки открываются нажатием ----------
rows = [('Выступи в роли ведущего викторины.', 'Роль', INK, LIGHT, 'role'),
        ('Придумай 3 вопроса про планеты Солнечной системы.', 'Цель', V, VB, 1),
        ('Это для детей 8 лет.', 'Контекст', G, GB, 2),
        ('У каждого вопроса 3 варианта ответа.', 'Формат', RED, RB, 3)]
b = ''
for i, (txt, lab, col, bg, n) in enumerate(rows, 1):
    y = 8 + (i-1)*88; cy = y + 36
    b += f'<g id="tap-{i}">' + raised(15, y, 740, 72, i) + rect(15, y, 740, 72, WHITE, V, 14)
    b += f'<g id="show-{i}">{rect(15, y, 740, 72, bg, col, 14)}{rect(28, y + 16, 5, 40, col, r=3, sw=0)}</g>'
    b += t(47, cy + 8, txt, 23, 700) + chip(613, y + 54, i) + '</g>'
    badge = person(836, cy) if n == 'role' else num(836, cy, n, col, 19)
    b += f'<g id="show-{i}">' + arrow(806, cy, 765, cy, col, 3)
    b += rect(808, cy - 25, 177, 50, bg, col, 25, 1.5) + badge + t(864, cy + 9, lab, 25, 700) + '</g>'
svg('s06-prompt-role', 1000, 368, 'Промт с ролью разобран на части: роль, цель, контекст, формат', b)

# ---------- слайд 7: образец и новый вопрос ----------
def qcard(x, y, w, h, head, q, opts, fill, stroke, topic):
    b = panel(x, y, w, h, fill, stroke) + rect(x + 6, y + 48, w - 12, h - 54, WHITE, r=11, sw=0)
    b += t(x + 20, y + 34, head, 21, 800, INK) + t(x + 20, y + 84, q, 23, 800)
    if topic == 'planet':
        b += mini('planet', x + w - 34, y + 24, .68)
    else:
        spider = path('M-4-5l-9-5-8 3 M-5-1l-9-3-8 6 M-5 4l-9 2-7 5 M-3 8l-7 6-5 6 M4-5l9-5 8 3 M5-1l9-3 8 6 M5 4l9 2 7 5 M3 8l7 6 5 6', stroke=DARK_V, sw=2.6)
        spider += ellipse(0, 3, 8, 9, DARK_V) + circle(0, -6, 5, DARK_V)
        b += place(x + w - 35, y + 24, spider, .8)
    for j, (letter, option) in enumerate(zip('АБВ', opts)):
        xx = x + 20 + j * ((w - 40) / 3)
        b += rect(xx, y + 101, (w - 40)/3 - 5, 37, '#F4F1FC', '#E7E0F6', 8, 1)
        b += circle(xx + 16, y + 119, 12, LAVENDER)
        b += t(xx + 16, y + 126, letter, 19, 800, DARK_V, 'middle') + t(xx + 31, y + 126, option, 19, 650)
    b += rect(x + 20, y + 151, 130, 31, GB, r=10, sw=0)
    return b + tick(x + 36, y + 166, scale=.8) + t(x + 50, y + 173, 'Ответ: Б', 21, 800, DARK_G)


b = qcard(15, 20, 390, 196, 'Образец в промте', 'Сколько ног у паука?', ['6', '8', '10'], VB, '#BFB1F0', 'spider')
b += t(482, 92, 'Вопрос', 21, 700, DARK_V, 'middle') + t(482, 118, 'про планеты', 20, 650, DARK_V, 'middle')
b += arrow(420, 140, 547, 140, V)
b += '<g id="tap-1">' + raised(560, 20, 425, 196, 1, 16) + rect(560, 20, 425, 196, '#FAF8FF', V)
b += '<g id="hide-1">' + circle(772, 74, 29, LAVENDER) + mini('chat', 772, 73, .9)
b += t(772, 131, 'Что напишет нейросеть?', 25, 800, INK, 'middle') + '</g>' + chip(706, 160, 1)
b += '<g id="show-1">' + qcard(560, 20, 425, 196, 'Ответ нейросети', 'Какая планета самая большая?', ['Марс', 'Юпитер', 'Земля'], GB, '#90D8B6', 'planet') + '</g></g>'
b += t(500, 252, 'Ответ нейросети нарисован для примера', 19, 600, GRAY, 'middle')
svg('s07-sample', 1000, 262, 'Образец вопроса про паука и вопрос про планеты, который напишет нейросеть', b)

# ---------- слайд 8: разминка по образцу ----------
def fig(x, y, pose):
    skin, hair, shorts = '#FFC69E', '#563749', '#353260'
    shirt = {'clap': '#8768DC', 'stomp': '#E17653', 'jump': '#497CC9', 'up': '#309C79'}[pose]
    b = ellipse(0, 87, 27 if pose != 'jump' else 17, 4, '#DBD9E8')
    legs = 'M-7 46l-5 18-8 13 M7 46l4 18 8 13'
    shoes = 'M-21 78h-6 M19 78h7'
    if pose == 'clap':
        arms = 'M-13 22l-12 10 20-8 M13 22l12 10-20-8'
        motion = 'M-2 16l-4-5 M4 15l4-5 M-2 33v5 M5 32l4 5'
    elif pose == 'up':
        arms = 'M-13 22l-11-16-5-20 M13 22l11-16 5-20'
        motion = 'M-39-9l2-8 4 2 M39-9l-2-8-4 2'
    elif pose == 'stomp':
        arms = 'M-12 22l-11 17 M12 22l16 3 6-10'
        legs = 'M-6 45l-4 18-5 14 M6 46l16 2-2 16'
        shoes = 'M-16 78h-8 M20 65h8'
        motion = 'M-31 79l-7-4 M-21 69l-5-5 M-30 86h-7'
    else:
        arms = 'M-11 20l-14-6-7-14 M11 20l14-6 7-14'
        legs = 'M-6 46l-10 9 10 9 M6 46l10 9-9 9'
        shoes = 'M-5 66l-5 5 M6 66l5 5'
        motion = 'M-31 69v-15l-4 4 M31 69v-15l4 4'
    b += path(legs, stroke=shorts, sw=8) + path(shoes, stroke='#F7AF43', sw=7)
    b += path(arms, stroke=skin, sw=7)
    b += path('M-14 19q14-9 28 0l-3 24q-11 4-22 0z', shirt, shorts, 2)
    b += path('M-6 17q6 7 12 0 M-7 34h14', stroke=WHITE, sw=2)
    b += circle(0, 0, 13, skin, hair, 2)
    b += path('M-13-1q-1-16 12-16 12 0 15 12-7 2-15-5-3 8-12 9z', hair)
    b += circle(-4, 2, 1.2, hair) + circle(4, 2, 1.2, hair)
    b += path('M-3 7q3 3 6 0', stroke=hair, sw=1.5)
    if pose == 'clap':
        b += path(arms, stroke=skin, sw=5)
    b += path(motion, stroke=shirt, sw=2.6)
    return place(x, y, b)


def slots(x0, y, poses, caps):
    out = ''
    for j, (p, c) in enumerate(zip(poses, caps)):
        cx = x0 + 52 + j*104
        out += rect(cx - 45, y - 16, 90, 146, '#F9F7FE' if p else '#F1EBFF', r=13, sw=0)
        if p:
            out += fig(cx, y + 9, p) + t(cx, y + 122, c, 19, 700, INK, 'middle')
    return out


b = ''
for i, (head, poses, caps) in enumerate([('Образец 1', ['clap', 'clap', 'up'], ['хлопок', 'хлопок', 'вверх']), ('Образец 2', ['stomp', 'stomp', 'up'], ['топ', 'топ', 'вверх'])]):
    x = 15 + i*330
    b += panel(x, 16, 315, 214, WHITE, '#DCD3F1') + t(x + 20, 47, head, 21, 800, DARK_V) + slots(x + 2, 72, poses, caps)
x = 675
b += '<g id="tap-1">' + raised(x, 16, 310, 214, 1, 16) + rect(x, 16, 310, 214, '#FFFFFF', V) + t(x + 20, 50, 'Новое', 21, 700, GRAY) + slots(x, 72, ['jump', 'jump', None], ['прыжок', 'прыжок', ''])
b += f'<g id="hide-1">{t(x + 260, 150, "?", 54, 800, V, "middle")}</g>' + chip(x + 166, 26, 1)
b += f'<g id="show-1">{rect(x + 215, 56, 90, 146, GB, r=13, sw=0)}{fig(x + 260, 81, "up")}{t(x + 260, 194, "вверх", 19, 700, DARK_G, "middle")}</g></g>'
b += f'<g id="show-1">{rect(15, 246, 970, 50, GB, G, 14)}{t(500, 279, "Два одинаковых движения, потом руки вверх", 23, 700, "#0B5B39", "middle")}</g>'
svg('s08-pattern', 1000, 300, 'Два образца движений и новое задание: что идёт после двух прыжков', b)

# ---------- слайд 9: два чата ----------
def bubble(x, y, w, lines, me=True):
    h = 15 + 28*len(lines)
    fill, edge = ('#E9E1FF', '#C8B9F2') if me else (WHITE, '#DCD7EB')
    out = rect(x, y, w, h, fill, edge, 13, 1.5)
    if me:
        out += path(f'M{x+w-13} {y+h-1}h18l-6-10', fill)
    else:
        out += path(f'M{x+13} {y+h-1}h-18l6-10', fill)
    for k, s in enumerate(lines):
        out += t(x + 12, y + 29 + 28*k, s, 21, 650)
    return out


b = ''
for i, title in enumerate(['Чат 1', 'Чат 2']):
    x = 15 + i*500
    b += panel(x, 6, 470, 244, '#F7F4FF', '#DCD3F1')
    b += rect(x + 1, 7, 468, 39, DARK_V, r=15, sw=0) + rect(x + 1, 29, 468, 17, DARK_V, r=0, sw=0)
    b += mini('chat', x + 28, 26, .53) + t(x + 51, 34, title, 23, 800, WHITE)
    b += ''.join(circle(x + dx, 26, 2.8, '#DCD7FF') for dx in (425, 436, 447))
b += path('M461 103c17 13 14 75-1 100', stroke='#A38DE4', sw=3)
b += bubble(60, 54, 400, ['Выступи в роли ведущего викторины.', 'Придумай 3 вопроса про планеты…'])
b += mini('chat', 51, 155, .56) + bubble(72, 133, 315, ['1. Какая планета…  2. …  3. …'], me=False)
b += bubble(245, 193, 215, ['Ещё один вопрос.'])
b += circle(750, 101, 30, '#EEE8FC') + mini('chat', 750, 101, .85)
b += t(750, 160, 'Других сообщений нет', 23, 650, GRAY, 'middle') + bubble(745, 193, 215, ['Ещё один вопрос.'])
svg('s09-chats', 1000, 258, 'Одна и та же просьба «Ещё один вопрос» в чате с разговором о викторине и в пустом чате', b)

# ---------- слайды 11 и 16: источник ----------
planets = [
    ('Меркурий', 13, '#B8AAA4', '#6D5362', 'самая', 'маленькая'),
    ('Венера', 19, '#F2BC64', '#AC663D', '', ''),
    ('Земля', 20, '#498FD5', '#3549A7', '', ''),
    ('Марс', 15, '#E69065', '#9F423E', '', ''),
    ('Юпитер', 44, '#F2C89D', '#AA6951', 'самая', 'большая'),
    ('Сатурн', 34, '#F7D798', '#AC824F', 'вторая', 'по размеру'),
    ('Уран', 27, '#98DFE1', '#3C9DB6', '', ''),
    ('Нептун', 26, '#6488EA', '#3546A5', '', ''),
]


def globe(cx, cy, r, fill, shade, name):
    # Поверхность строится в пределах круга радиусом 40. Кольца проходят за диском и перед ним.
    b = ''
    if name == 'Сатурн':
        b += '<g transform="rotate(-15)">' + ellipse(0, 0, 63, 14, '#D4A963') + ellipse(0, 0, 53, 8, '#9A7049') + '</g>'
    b += circle(0, 0, 40, fill, shade, 1.6)
    if name == 'Меркурий':
        for x, y, size in [(-16, -12, 8), (10, -21, 5), (19, 4, 9), (-8, 17, 6), (-22, 9, 4), (6, 27, 5)]:
            b += circle(x, y, size, '#8C797C', '#DACAC3', 2)
    elif name == 'Венера':
        b += path('M-29-22Q-1-10 27-21 M-36-10Q-5 7 34-10 M-36 5Q-8 20 36 5 M-29 22Q-2 37 26 22', stroke='#FFDEA4', sw=6)
        b += path('M-21-27q15 7 32 2 M-26 11q22 7 41 2', stroke='#D58D51', sw=3)
    elif name == 'Земля':
        b += path('M-31-20l9-9 12 1 6 6-7 8 3 6-9 6-11-6z M-13 0l12 5 6 9-8 12-4 8-6-15z M9-23l13-5 10 10-2 12-11-4-7 7-6-5z M12 1l10 2 6 10-11 12-5-9z M25 24l9-4-4 9-9 4z', '#79CA91')
        b += path('M-33-13q8 6 18 3 M4-15q11-3 23 3 M-30 12q10 6 18 3 M1 29q9 5 19 2', stroke='#EAF8F4', sw=3)
    elif name == 'Марс':
        b += path('M-34-14l10-10 11 11 11 1 5 10-13 10-12-6-12 4z M4 17l12-10 16 3-5 12-13 8z', '#B75244')
        b += path('M-14-35q16-7 30 2l-8 5-19-1z', '#FFE6D3')
        b += circle(18, -11, 7, '#D67353', '#A75346', 2)
    elif name == 'Юпитер':
        b += path('M-32-21q33 10 64 0 M-37-10q41 11 74 0 M-37 9q33 10 74-1 M-27 25q27 6 54-1', stroke='#BD8062', sw=6)
        b += path('M-23-28q26 6 45-1 M-38 0q35 9 76-1 M-31 19q32 7 63-3', stroke='#FFDFB5', sw=4)
        b += '<g transform="rotate(-9)">' + ellipse(16, 12, 12, 7, '#B75B49') + ellipse(17, 12, 7, 3, '#F29871') + '</g>'
    elif name == 'Сатурн':
        b += path('M-28-22q26 9 56 0 M-36-10q38 10 72 0 M-37 3q37 10 74 0 M-27 24q29 5 54-2', stroke='#E7B976', sw=5)
    elif name == 'Уран':
        b += path('M-29-22q28 7 59 0 M-37-8q38 7 74-1 M-34 13q38 7 68-1', stroke='#BDF1EC', sw=4)
    else:
        b += path('M-30-20q26 7 61-1 M-37-1q36 11 74 0 M-29 22q25 6 58-2', stroke='#83A9F7', sw=4)
        b += ellipse(-6, 11, 10, 5, '#4157B7') + path('M13 12q9-2 16-4', stroke='#CEDFFF', sw=3)
    b += f'<g opacity=".22">{path("M19-35A40 40 0 0 1-29 28C13 42 48 0 19-35Z", shade)}</g>'
    b += f'<g opacity=".48">{path("M-31-11q4-15 18-20", stroke=WHITE, sw=2.5)}</g>'
    if name == 'Сатурн':
        front = path('M-63 0C-63 18 63 18 63 0C59 10 -59 10 -63 0Z', '#E8C17E', '#A8804A', 1.2)
        front += path('M-58 5c25 12 91 12 116 0', stroke='#FFF0BE', sw=2)
        b += f'<g transform="rotate(-15)">{front}</g>'
    return place(cx, cy, b, r / 40)


def source():
    out = rect(6, 3, 988, 226, '#F8F7FE', '#E3DDF4', 22, 2)
    out += path('M77 98H959', stroke='#DDD5EE', sw=2)
    for x, y, size in [(94, 66, 2), (198, 126, 2), (302, 63, 2), (477, 128, 2), (513, 58, 3),
                        (640, 135, 2), (744, 63, 2), (848, 130, 3), (954, 58, 2)]:
        out += circle(x, y, size, '#C8BDE8')
    out += circle(52, 98, 40, '#FFEBC2') + circle(52, 98, 32, '#FFD16A', '#EA9C3A', 2)
    out += path('M28 102q15-13 38-5 M35 80q17-7 32 1 M43 117q19 6 26-7', stroke='#F6AB40', sw=3)
    out += path('M52 50v-6 M52 146v6 M11 98h5 M88 98h5 M22 68l-4-4 M82 128l4 4 M82 68l4-4 M22 128l-4 4', stroke='#E9A13F', sw=2.5)
    out += t(52, 171, 'Солнце', 21, 750, '#82491C', 'middle')
    for k, (name, r, color, shade, n1, n2) in enumerate(planets):
        cx = 153 + k*113
        out += circle(cx, 29, 16, LAVENDER) + t(cx, 36, str(k + 1), 22, 800, DARK_V, 'middle')
        out += globe(cx, 98, r, color, shade, name)
        out += t(cx, 171, name, 22, 800, INK, 'middle')
        if n1:
            badge_w = {'Меркурий': 116, 'Юпитер': 98, 'Сатурн': 120}[name]
            out += rect(cx - badge_w/2, 178, badge_w, 46, GB, '#C3EBDC', 10, 1)
            out += t(cx, 197, n1, 21, 700, DARK_G, 'middle') + t(cx, 218, n2, 21, 700, DARK_G, 'middle')
    return out


svg('s11-source', 1000, 258, 'Восемь планет по порядку от Солнца: Меркурий самая маленькая, Юпитер самая большая, Сатурн вторая по размеру', source())
svg('s16-source', 1000, 258, 'Источник для проверки: восемь планет по порядку от Солнца и их размер', source())

# ---------- слайд 13: начать практику ----------
b = ''
for k, title in enumerate(['Сайт', 'Новый чат', 'Поле для промта']):
    x = 15 + k*335
    b += panel(x, 8, 300, 146, '#F9F6FE', '#DCD3F1')
    b += num(x + 30, 38, k + 1, DARK_V, 18) + t(x + 58, 47, title, 25, 800)
    if k == 0:
        b += rect(x + 16, 66, 268, 72, WHITE, '#D4C9F0', 10, 2)
        b += ''.join(circle(x + dx, 79, 2.5, V) for dx in (29, 39, 49))
        b += rect(x + 25, 90, 250, 36, VB, r=8, sw=0)
        b += circle(x + 45, 108, 9, WHITE, DARK_V)
        b += path(f'M{x+37} 108h16 M{x+45} 100q-7 8 0 16q7-8 0-16', stroke=DARK_V, sw=1.4)
        b += t(x + 65, 116, 'alice.yandex.ru', 23, 700, DARK_V)
    elif k == 1:
        b += circle(x + 59, 102, 32, LAVENDER) + mini('chat', x + 54, 98, .85)
        b += circle(x + 76, 109, 13, MINT, DARK_G) + path(f'M{x+70} 109h12 M{x+76} 103v12', stroke=DARK_G, sw=2.8)
        b += t(x + 106, 98, 'Кнопка. Значок', 20, 650, GRAY) + t(x + 106, 124, 'может отличаться', 20, 650, GRAY)
    else:
        b += rect(x + 16, 74, 268, 58, WHITE, V, 13, 2)
        b += path(f'M{x+36} 89v28 M{x+32} 89h8 M{x+32} 117h8', stroke=DARK_V, sw=2.4)
        b += circle(x + 251, 103, 18, LAVENDER) + place(x + 251, 103, path('M-7 5l15-6-15-6 3 6z', DARK_V))
    if k < 2:
        b += arrow(x + 305, 104, x + 329, 104, V, 3)
svg('s13-start', 1000, 166, 'Три шага: открыть сайт, начать новый чат, найти поле для промта', b)

# ---------- слайд 14: промт с ролью по частям ----------
parts = [(['Выступи в роли ведущего викторины.'], INK, LIGHT, 'role'),
         (['Придумай 3 вопроса про планеты Солнечной системы: какая', 'планета по счёту от Солнца, какая самая большая или самая маленькая.'], V, VB, 1),
         (['Это для [кого].'], G, GB, 2),
         (['У каждого вопроса 3 варианта ответа. Напиши все вопросы сразу.'], RED, RB, 3)]
b = ''; y = 6
for lines, col, bg, n in parts:
    h = 22 + 34*len(lines)
    b += rect(15, y, 1090, h, bg, col, 14, 2)
    b += rect(26, y + 9, 50, h - 18, WHITE, r=9, sw=0)
    b += (person(51, y + h/2) if n == 'role' else num(51, y + h/2, n, col, 17))
    for k, s in enumerate(lines):
        baseline = y + 38 + 34*k
        if n == 2:
            b += rect(194, baseline - 28, 82, 37, WHITE, r=7, sw=0)
            b += t(91, baseline, s, 27, 700).replace('[кого]', f'<tspan fill="{DARK_G}" font-weight="800">[кого]</tspan>')
        else:
            b += t(91, baseline, s, 27, 700)
    y += h + 6
svg('s14-template', 1120, y, 'Образец промта: роль, цель, контекст и формат', b)

# ---------- слайд 15: проверка после образца ----------
b = ''
for k, s in enumerate(['Форма как в образце: вопрос, 3 варианта, ответ?', 'Вопросы всё ещё про планеты?', 'У каждого вопроса есть строка «Ответ»?']):
    y = 10 + k*70
    b += panel(15, y, 970, 57, '#FAF8FF', '#E1D8F3', 13)
    b += num(44, y + 29, k + 1, DARK_V, 17) + mini(['list', 'planet', 'answer'][k], 94, y + 29, .9)
    b += t(129, y + 37, s, 24, 700)
svg('s15-check', 1000, 222, 'Три вопроса для проверки ответа после образца', b)

# ---------- слайд 17: пауза для глаз ----------
desk = path('M0 149h270v13H0z M22 162h13v23H22z M235 162h13v23h-13z', '#E5BE98', '#956C58')
desk += rect(32, 16, 169, 103, '#40365B', '#524367', 10, 3) + rect(41, 25, 151, 85, '#EDE7FF', r=6, sw=0)
desk += rect(49, 33, 135, 12, '#CABAF7', r=4, sw=0) + bars(58, 60, [99, 80, 91], '#B7A7E2', 14, 4)
desk += path('M101 118h29l3 23h-35z M84 143h64', '#40365B', '#40365B', 5)
desk += path('M222 151l-7-29h32l-7 29z', PEACH, '#925750')
desk += path('M230 122q-6-17-23-18 0 14 23 18 M230 122q-1-22 19-29 3 16-19 29', '#67AD8C', DARK_G)
desk += t(116, 94, 'Экран', 31, 800, '#3D306F', 'middle')
window = rect(0, 0, 258, 155, '#A8DDF5', '#294F63', 9, 4)
window += circle(65, 41, 17, '#FFDE84')
window += path('M16 61q4-10 13-6 7-13 20-1 11-3 18 7z M163 38q8-13 20-4 8-5 18 4z', '#EFFAFF')
window += path('M3 119l48-34 29 14 54-52 38 40 17-13 66 49v29H3z', '#8FB8CE')
window += path('M107 74l27-27 26 27-14-7-11 6-10-6z', '#EDF8FC')
window += path('M3 128q61-30 113-10t139-8v42H3z', '#8CC5A3')
window += path('M3 142q59-22 120-4t132-9v23H3z', '#5C9C7D')
window += path('M129 3v149 M3 80h252', stroke='#345A62', sw=5)
window += path('M-8 155h274', stroke='#345A62', sw=7)
b = panel(15, 13, 321, 196, '#FAF4FE', '#DCCFEF', 18) + place(42, 24, desk)
b += t(500, 92, 'Смотрим вдаль', 30, 800, DARK_G, 'middle') + arrow(355, 126, 646, 126, '#2C9A77', 5)
b += panel(665, 13, 320, 196, '#EDF9F3', '#BDE7D5', 18) + place(696, 34, window)
svg('s17-pause', 1000, 230, 'Отводим взгляд от экрана и смотрим вдаль, например в окно', b)

# ---------- слайд 18: замена и новая проверка ----------
b = ''
steps = [('Замена', 'в том же чате'), ('Новый вопрос', 'остальные как были'), ('Проверка', 'по источнику')]
for k, (a1, a2) in enumerate(steps):
    x = 15 + k*335
    fill, edge = ('#F5F0FE', '#DED1F6') if k < 2 else ('#F0FAF5', '#C8EADA')
    b += panel(x, 10, 300, 88, fill, edge)
    b += num(x + 25, 54, k + 1, DARK_V if k < 2 else DARK_G, 16)
    b += circle(x + 71, 54, 24, LAVENDER if k < 2 else MINT) + mini(['edit', 'chat', 'book'][k], x + 71, 54, .8)
    b += t(x + 106, 49, a1, 23, 800) + t(x + 106, 77, a2, 20, 650, GRAY)
    if k < 2:
        b += arrow(x + 305, 54, x + 330, 54, V, 3)
svg('s18-flow', 1000, 112, 'Замена вопроса в том же чате, новый вопрос и его проверка по источнику', b)

# ---------- слайд 19: свой промт ----------
b = ''
for k, (a1, a2) in enumerate([('Сколько вопросов', 'нужно?'), ('Про что вопрос:', 'порядок или размер?'), ('Форма та же,', 'что в образце?')]):
    x = 15 + k*330
    b += panel(x, 12, 310, 150, '#FAF7FF', '#DCD2F2')
    b += circle(x + 155, 57, 32, ['#E1D8FA', '#FFEDC9', '#D8F4E7'][k])
    b += mini(['list', 'planet', 'answer'][k], x + 155, 57, 1.12)
    b += t(x + 155, 115, a1, 23, 800, INK, 'middle') + t(x + 155, 141, a2, 23, 700, INK, 'middle')
svg('s19-own', 1000, 174, 'Три подсказки для своего промта', b)

# ---------- слайд 20: сохранить квиз ----------
b = ''
cards = [
    (['Нажмите в Алисе', 'значок из двух', 'квадратов'], 'Он копирует ответ'),
    (['Покажите текст', 'взрослому'], 'Личных сведений нет?'),
    (['Вставьте', 'в чат урока'], 'Ваш квиз'),
]
for k, (title, cap) in enumerate(cards):
    x = 15 + k*335
    fill, edge = ('#F7F3FE', '#DED3F5') if k != 1 else ('#F1FBF6', '#CBEBDD')
    b += panel(x, 15, 300, 220, fill, edge, 18)
    b += num(x + 32, 52, k + 1, DARK_V if k != 1 else DARK_G, 18)
    first_line = 41 if k == 0 else 49
    b += t(x + 61, first_line, title[0], 22, 800)
    for j, line in enumerate(title[1:], 1):
        b += t(x + 61, first_line + j*23, line, 21, 700)
    if k == 0:
        b += rect(x + 62, 94, 176, 91, WHITE, '#D4C6F1', 13, 2)
        b += bars(x + 78, 116, [66, 79, 65], '#B9AAD9', 15, 4)
        b += circle(x + 204, 141, 27, LAVENDER)
        b += rect(x + 190, 137, 20, 22, '#F1EAFF', DARK_V, 4, 2) + rect(x + 199, 128, 20, 22, WHITE, DARK_V, 4, 2)
    if k == 1:
        adult = path('M-31 39v-8q0-21 31-21t31 21v8z', '#7BC6AD', DARK_G)
        adult += circle(0, -6, 20, '#F7C5A6', '#5C4650', 2)
        adult += path('M-20-6q-5-24 18-24 20 0 23 21-16-2-23-13-5 12-18 16z', '#60414C')
        adult += circle(-7, -3, 1.6, '#5C4650') + circle(7, -3, 1.6, '#5C4650')
        adult += path('M-5 4q5 5 10 0', stroke='#5C4650')
        b += circle(x + 120, 139, 46, '#D8F4E7') + place(x + 120, 131, adult)
        b += mini('answer', x + 173, 145, 1.35)
    if k == 2:
        b += rect(x + 28, 94, 244, 91, WHITE, '#D4C6F1', 13, 2)
        b += rect(x + 40, 105, 181, 62, '#EAE1FC', r=8, sw=0)
        b += t(x + 49, 131, '1. Какая планета…', 19, 750) + t(x + 49, 154, 'А) Б) В) Ответ: …', 19, 650)
        b += circle(x + 243, 155, 17, LAVENDER) + place(x + 243, 155, path('M-7 5l15-6-15-6 3 6z', DARK_V))
    b += t(x + 150, 215, cap, 20, 650, GRAY, 'middle')
    if k < 2:
        b += arrow(x + 305, 138, x + 330, 138, V, 3)
svg('s20-save', 1000, 250, 'В Алисе нажать значок копирования, показать текст взрослому и вставить квиз в чат урока', b)

print('SVG:', sorted(p.name for p in OUT.glob('*.svg')))
