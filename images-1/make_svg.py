"""Рисует схемы урока в папку svg. Нажимаемые группы: tap-N, показ по нажатию: show-N, метка «Нажмите»: hide-N."""
import math
import random
from html import escape as e
from pathlib import Path

R = Path(__file__).resolve().parent
OUT = R/'svg'
OUT.mkdir(exist_ok=True)
INK, V, VB, G, GB, RED, RB, GRAY, LINE, LIGHT, MUTE = '#17171C', '#6F61E8', '#F0EEFE', '#0FBF6E', '#E7FDF2', '#E04848', '#FFECEC', '#5F5F6B', '#E3E3EA', '#EFEFF2', '#8F8F98'
AM, AMB = '#D9822B', '#FFF1E0'          # стиль
ORANGE, SKY = '#F08A24', '#1E2440'
FONT = 'Inter Tight, Inter, Arial, Helvetica, sans-serif'
PARTS = {'subj': (V, VB, 'Предмет'), 'bg': (G, GB, 'Фон'), 'style': (AM, AMB, 'Стиль')}


def t(x, y, s, size=24, w=600, fill=INK, a='start'):
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{a}">{e(s)}</text>'


def rect(x, y, w, h, fill='#F5F5F9', stroke='none', r=16, sw=3, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def num(x, y, n, fill, r=18):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>' + t(x, y + 8, str(n), 23, 700, '#FFFFFF', 'middle')


def arrow(x1, y1, x2, y2, color=MUTE, w=4):
    ang = math.atan2(y2 - y1, x2 - x1); c, s = math.cos(ang), math.sin(ang)
    p1 = (x2 - 14*c + 7*s, y2 - 14*s - 7*c); p2 = (x2 - 14*c - 7*s, y2 - 14*s + 7*c)
    return f'<line x1="{x1}" y1="{y1}" x2="{x2-6*c:.1f}" y2="{y2-6*s:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/><path d="M{x2} {y2} L{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f} Z" fill="{color}"/>'


def chip(x, y, n):
    """Метка «Нажмите», исчезает после нажатия."""
    return f'<g id="hide-{n}"><rect x="{x}" y="{y}" width="132" height="34" rx="17" fill="{V}"/><path d="M0 0 L0 15 L4.2 11.2 L7 17.4 L9.6 16.2 L6.8 10.2 L12.6 10.2 Z" fill="#FFFFFF" transform="translate({x+12} {y+8})"/>' + t(x + 32, y + 24, 'Нажмите', 20, 800, '#FFFFFF') + '</g>'


def raised(x, y, w, h, n, r=14):
    """Фиолетовый нижний край нажимаемого элемента: виден, пока элемент не открыт."""
    return f'<g id="hide-{n}">{rect(x, y + 6, w, h, V, r=r, sw=0)}</g>'


def svg(name, w, h, label, body, defs=''):
    (OUT/f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}"><title>{e(label)}</title>{defs}{body}</svg>', encoding='utf-8')


def clip(cid, x, y, w, h, r=14):
    return f'<defs><clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath></defs>'


# ---------- маленькие рисунки ----------
def cat(x, y, k=1.0, color=ORANGE, detail=True, turned_left=False):
    """Мультяшный кот сидя: (x, y) — середина низа."""
    direction = -k if turned_left else k
    outline = '#753E29' if detail else color
    tail = 'M21-12C52-6 69-28 61-49Q58-59 49-63'
    out = f'<g transform="translate({x} {y}) scale({direction} {k})">'
    out += f'<path d="{tail}" stroke="{outline}" stroke-width="17" fill="none" stroke-linecap="round"/>'
    out += f'<path d="{tail}" stroke="{color}" stroke-width="11" fill="none" stroke-linecap="round"/>'
    out += f'<path d="M-30-5C-40-18-30-48-21-64Q0-82 23-62C32-48 40-16 29-5Q0 3-30-5Z" fill="{color}" stroke="{outline}" stroke-width="3.5"/>'
    out += f'<path d="M-29-95L-29-132Q-28-136-24-131L-9-115Q0-118 10-115L25-132Q29-137 30-130L30-96Q39-80 25-70Q0-56-25-70Q-39-81-29-95Z" fill="{color}" stroke="{outline}" stroke-width="3.5" stroke-linejoin="round"/>'
    if detail:
        out += '<path d="M-24-123l9 10-10 8zM25-123l-9 10 10 8z" fill="#FFBA80"/>'
        out += '<path d="M-10-113l4 10m6-11v10m10-9-4 10M-28-40l9 5m49-5-9 5" fill="none" stroke="#A45129" stroke-width="3.5" stroke-linecap="round"/>'
        out += '<ellipse cx="0" cy="-33" rx="13" ry="18" fill="#FFD18F"/><ellipse cx="0" cy="-80" rx="15" ry="10" fill="#FFE1B4"/>'
        out += f'<circle cx="-13" cy="-94" r="4.9" fill="{INK}"/><circle cx="13" cy="-94" r="4.9" fill="{INK}"/><circle cx="-14" cy="-96" r="1.4" fill="#FFFFFF"/><circle cx="12" cy="-96" r="1.4" fill="#FFFFFF"/>'
        out += '<path d="M-5-86Q0-88 5-86L0-80Z" fill="#A44536"/><path d="M0-81v4m0 0q-4 6-8 1m8-1q4 6 8 1" fill="none" stroke="#753E29" stroke-width="1.8" stroke-linecap="round"/>'
        out += '<path d="M-13-83l-25-6m24 12-26-1m53-5 25-6M14-77l26-1" fill="none" stroke="#753E29" stroke-width="2.2" stroke-linecap="round"/>'
        out += f'<ellipse cx="-14" cy="-5" rx="12" ry="8" fill="#FFC373" stroke="{outline}" stroke-width="2.5"/><ellipse cx="14" cy="-5" rx="12" ry="8" fill="#FFC373" stroke="{outline}" stroke-width="2.5"/>'
    return out + '</g>'


def sleeping_cat(x, y):
    return f'''<g transform="translate({x} {y})">
    <ellipse cx="8" cy="-7" rx="34" ry="19" fill="{ORANGE}"/>
    <path d="M34-11 C57-6 48 13 21 12 L-5 12" fill="none" stroke="#C05E26" stroke-width="7" stroke-linecap="round"/>
    <path d="M-40-10 L-43-34 L-27-24 L-18-24 L-7-35 L-6-8" fill="{ORANGE}"/>
    <ellipse cx="-23" cy="-10" rx="21" ry="16" fill="{ORANGE}"/>
    <path d="M-37-10q4 5 8 0m9 0q4 5 8 0" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>
    <path d="M-27-3h7l-3.5 3z" fill="#B0402A"/>
    <ellipse cx="-26" cy="8" rx="15" ry="5" fill="#FFC16D"/></g>'''


def rocket(x, y, k=1.0):
    s = lambda v: v*k
    return (f'<path d="M{x} {y-s(110)} C{x+s(30)} {y-s(80)},{x+s(26)} {y-s(30)},{x+s(22)} {y} L{x-s(22)} {y} C{x-s(26)} {y-s(30)},{x-s(30)} {y-s(80)},{x} {y-s(110)} Z" fill="#FFFFFF" stroke="{INK}" stroke-width="{s(4)}"/>'
            f'<path d="M{x-s(22)} {y-s(30)} L{x-s(42)} {y+s(4)} L{x-s(22)} {y} Z M{x+s(22)} {y-s(30)} L{x+s(42)} {y+s(4)} L{x+s(22)} {y} Z" fill="{RED}" stroke="{INK}" stroke-width="{s(3)}"/>'
            f'<circle cx="{x}" cy="{y-s(62)}" r="{s(11)}" fill="#7FD3DC" stroke="{INK}" stroke-width="{s(3)}"/>')


def house_sea(x, y, w, h):
    out = rect(x, y, w, h, '#FFD9B3', 'none', 10, 0)
    out += f'<circle cx="{x+w*0.72}" cy="{y+h*0.55}" r="{h*0.22}" fill="#F7A23B"/>'
    out += f'<rect x="{x}" y="{y+h*0.58}" width="{w}" height="{h*0.42}" fill="#3D8BE0"/>'
    out += f'<path d="M{x} {y+h*0.66}Q{x+w*0.22} {y+h*0.58} {x+w*0.54} {y+h*0.67}L{x+w*0.5} {y+h*0.74}Q{x+w*0.24} {y+h*0.69} {x} {y+h*0.76}Z" fill="#F1B67C"/>'
    for a, b, c in [(0.48, 0.81, 0.21), (0.66, 0.73, 0.23), (0.16, 0.87, 0.19)]:
        out += f'<path d="M{x+w*a} {y+h*b}q{w*c/2} 3 {w*c} 0" fill="none" stroke="#B9E6EF" stroke-width="2.5" stroke-linecap="round"/>'
    out += f'<path d="M{x+w*0.12} {y+h*0.66} L{x+w*0.12} {y+h*0.38} L{x+w*0.26} {y+h*0.24} L{x+w*0.4} {y+h*0.38} L{x+w*0.4} {y+h*0.66} Z" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/>'
    out += f'<path d="M{x+w*0.09} {y+h*0.4} L{x+w*0.26} {y+h*0.22} L{x+w*0.43} {y+h*0.4}" fill="none" stroke="{RED}" stroke-width="6" stroke-linejoin="round"/>'
    out += rect(x + w*0.16, y + h*0.45, w*0.08, h*0.10, '#7FD3DC', INK, r=2, sw=1.5)
    out += rect(x + w*0.28, y + h*0.48, w*0.07, h*0.17, '#AC6846', INK, r=2, sw=1.5)
    return out


def net(cx, cy, col=V):
    pts = [(cx-38, cy-26), (cx-38, cy+26), (cx, cy-34), (cx, cy), (cx, cy+34), (cx+38, cy)]
    lines = ''.join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{col}" stroke-width="3"/>' for a in pts[:2] for b in pts[2:5]) + ''.join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{pts[5][0]}" y2="{pts[5][1]}" stroke="{col}" stroke-width="3"/>' for a in pts[2:5])
    return lines + ''.join(f'<circle cx="{x}" cy="{y}" r="10" fill="{col}"/>' for x, y in pts)


def moon_land(x, y, w, h, detail=True):
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{SKY}"/>'
    if detail:
        rnd = random.Random(7)
        for _ in range(26):
            sx, sy = x + w*rnd.uniform(.04, .96), y + h*rnd.uniform(.05, .58)
            out += f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{h*rnd.choice([.003, .0045, .006]):.1f}" fill="#F6EDDA"/>'
    ex, ey, scale = x + w*.80, y + h*.20, h*.11/36
    out += f'<g transform="translate({ex} {ey}) scale({scale})"><circle r="36" fill="#4F9BE4"/>'
    if detail:
        out += '<path d="M-25-24l12-6 13 2 5 6-10 5-4 7-10 4-1 6-7-5-5-11zM-14 2l10 2 5 6-3 9-5 8-5-5-2-10-6-5zM8-16l10-8 11 7 3 11-7 3-3 8-10 2-4-6 3-7-5-3z" fill="#65C795"/><path d="M20 18l8-3 5 3-5 7-8 2-5-5z" fill="#65C795"/><circle r="36" fill="none" stroke="#A9D8F4" stroke-width="2"/>'
    out += '</g>'
    out += f'<path d="M{x} {y+h*.66}Q{x+w*.32} {y+h*.57} {x+w*.61} {y+h*.65}T{x+w} {y+h*.63}V{y+h}H{x}Z" fill="#BCC2D0"/>'
    if detail:
        out += f'<path d="M{x} {y+h*.79}Q{x+w*.26} {y+h*.73} {x+w*.52} {y+h*.82}T{x+w} {y+h*.8}V{y+h}H{x}Z" fill="#A8AFBF"/>'
        for cx, cy, rw in [(0.13, 0.83, 0.075), (0.48, 0.93, 0.07), (0.86, 0.79, 0.066), (0.59, 0.71, 0.04)]:
            cx, cy, rx, ry = x + w*cx, y + h*cy, w*rw, w*rw*.32
            out += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#DCE1E8"/><ellipse cx="{cx}" cy="{cy-ry*.16}" rx="{rx*.77}" ry="{ry*.60}" fill="#778193"/><ellipse cx="{cx+rx*.09}" cy="{cy+ry*.11}" rx="{rx*.48}" ry="{ry*.23}" fill="#929BAB"/>'
    return out


def moon_scene(x, y, w, h, cid, cats):
    out = clip(cid, x, y, w, h) + f'<g clip-path="url(#{cid})">' + moon_land(x, y, w, h)
    for position, scale, turned_left in cats:
        out += f'<ellipse cx="{x+w*position}" cy="{y+h*.9}" rx="{32*scale}" ry="{6*scale}" fill="#667285" opacity=".33"/>'
        out += cat(x + w*position, y + h*.9, scale, turned_left=turned_left)
    return out + '</g>'


# ---------- слайд 5: пары «картинка — описание» ----------
b = ''
pairs = [('Рыжий кот', 'спит на диване'), ('Ракета летит', 'в космосе'), ('Дом у моря', 'на закате')]
for i, (a1, a2) in enumerate(pairs):
    x = 15 + i*225
    b += rect(x, 10, 210, 250, '#FFFFFF', INK, 16, 3)
    px, py, pw, ph = x + 12, 22, 186, 140
    if i == 0:
        b += rect(px, py, pw, ph, '#FFF6E8', r=10)
        b += rect(px + 26, py + 49, 134, 61, '#8378F0', r=13) + rect(px + 18, py + 94, 150, 31, V, r=10)
        b += rect(px + 10, py + 78, 23, 47, '#5A4ED0', r=8) + rect(px + 153, py + 78, 23, 47, '#5A4ED0', r=8)
        b += sleeping_cat(px + 90, py + 96)
    elif i == 1:
        rnd = random.Random(3)
        b += rect(px, py, pw, ph, SKY, r=10)
        b += ''.join(f'<circle cx="{px+8+rnd.random()*(pw-16):.0f}" cy="{py+8+rnd.random()*(ph-16):.0f}" r="2" fill="#FFFFFF"/>' for _ in range(16))
        rx, ry = px + 93, py + 113
        b += f'<g transform="rotate(30 {px+93} {py+75})"><path d="M{rx-10} {ry-2}q-8 13 10 25q18-12 10-25z" fill="#F29236"/><path d="M{rx-4} {ry-2}q-4 10 4 16q8-6 4-16z" fill="#FFD47E"/>{rocket(rx, ry, 0.86)}</g>'
    else:
        b += house_sea(px, py, pw, ph)
    b += t(x + 105, 198, a1, 22, 700, INK, 'middle') + t(x + 105, 228, a2, 22, 700, INK, 'middle')
b += arrow(700, 135, 790, 135) + t(745, 100, 'учится', 20, 600, GRAY, 'middle')
b += rect(800, 40, 185, 190, VB) + net(892, 120) + t(892, 210, 'Нейросеть', 23, 700, INK, 'middle')
b += t(15, 296, 'Описание — под каждой картинкой. Рисунки нарисованы для урока', 20, 600, GRAY)
svg('s05-pairs', 1000, 306, 'Нейросеть учится на парах: картинка и описание к ней', b)

# ---------- слайд 6: из шума в картинку ----------
FW, FH = 205, 170


def noise(x, y, seed=11):
    rnd = random.Random(seed); out = ''
    pal = ['#9C9AA6', '#F08A24', '#3D8BE0', '#1E2440', '#B9B9C3', '#E8B04B', '#6F61E8', '#FFFFFF']
    for i in range(0, FW, 15):
        for j in range(0, FH, 15):
            out += f'<rect x="{x+i}" y="{y+j}" width="15" height="15" fill="{rnd.choice(pal)}"/>'
    return out


defs = '<defs><filter id="blur6" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter><filter id="blur2"><feGaussianBlur stdDeviation="3"/></filter></defs>'
b = ''
xs = [15 + k*248 for k in range(4)]
labels = ['Шум', 'Цветовое пятно', 'Формы', 'Готово']
Y = 46
for k, x in enumerate(xs):
    b += num(x + 18, 20, k + 1, INK, 16)
    if k < 3:
        b += arrow(x + FW + 6, Y + FH/2, x + 242, Y + FH/2)
b += clip('f1', xs[0], Y, FW, FH) + f'<g clip-path="url(#f1)">{noise(xs[0], Y)}</g>' + t(xs[0] + 42, 28, labels[0], 22, 700)
# кадр 2: пятно
x = xs[1]
blob = clip('f2', x, Y, FW, FH)
blob += f'<g clip-path="url(#f2)"><rect x="{x}" y="{Y}" width="{FW}" height="{FH}" fill="{SKY}"/><g filter="url(#blur6)">{moon_land(x, Y, FW, FH, detail=False)}<ellipse cx="{x+FW*.48}" cy="{Y+104}" rx="27" ry="43" fill="{ORANGE}"/></g></g>'
# кадр 3: формы без деталей
x3 = xs[2]
shapes = clip('f3', x3, Y, FW, FH)
shapes += f'<g clip-path="url(#f3)"><rect x="{x3}" y="{Y}" width="{FW}" height="{FH}" fill="{SKY}"/><g filter="url(#blur2)">{moon_land(x3, Y, FW, FH, detail=False)}{cat(x3+FW*.48, Y+FH*.9, 0.62, detail=False)}</g></g>'
for xx, content, lab in [(xs[1], blob, labels[1]), (xs[2], shapes, labels[2])]:
    b += content + t(xx + 42, 28, lab, 22, 700)
b += moon_scene(xs[3], Y, FW, FH, 'f4', cats=[(0.48, 0.62, False)]) + t(xs[3] + 42, 28, labels[3], 22, 700)
b += t(500, 250, 'Кадры нарисованы для урока', 20, 600, GRAY, 'middle')
svg('s06-noise', 1000, 260, 'Картинка из шума шаг за шагом: шум, цветовое пятно, формы, готовая картинка', b, defs)

# ---------- слайд 7: промт для картинки, строки открываются нажатием ----------
rows = [('Нарисуй рыжего кота', 'subj'), ('на Луне', 'bg'), ('цветными карандашами.', 'style')]
b = ''
for i, (txt, part) in enumerate(rows, 1):
    col, bg, lab = PARTS[part]
    y = 8 + (i-1)*92; cy = y + 37
    b += f'<g id="tap-{i}">' + raised(15, y, 740, 74, i) + rect(15, y, 740, 74, '#FFFFFF', V, 14) + f'<g id="show-{i}">{rect(15, y, 740, 74, bg, col, 14)}</g>' + t(36, cy + 9, txt, 25, 700) + chip(613, y + 56, i) + '</g>'
    b += f'<g id="show-{i}">' + arrow(808, cy, 765, cy, col) + num(836, cy, i, col, 19) + t(864, cy + 9, lab, 26, 700) + '</g>'
svg('s07-prompt', 1000, 286, 'Промт для картинки разобран на части: предмет, фон, стиль', b)

# ---------- слайд 8: промт для текста и для картинки ----------
def pill(x, y, s, bg):
    w = 26 + 13*len(s)
    return rect(x, y, w, 44, bg, r=10) + t(x + w/2, y + 30, s, 22, 700, INK, 'middle'), w


b = ''
for k, (title, parts, ans) in enumerate([('Промт для текста', [('цель', LIGHT), ('контекст', LIGHT), ('формат', LIGHT)], 'text'),
                                         ('Промт для картинки', [('предмет', VB), ('фон', GB), ('стиль', AMB)], 'pic')]):
    x = 15 + k*495
    b += rect(x, 8, 475, 236, '#FFFFFF', INK, 18, 3) + t(x + 24, 48, title, 25, 800)
    if k == 1:
        b += t(x + 24, 86, 'Начинается со слова «Нарисуй»', 21, 600, GRAY)
    px = x + 24
    for s, bg in parts:
        p, w = pill(px, 104, s, bg); b += p; px += w + 10
    b += arrow(x + 40, 178, x + 120, 178) + t(x + 140, 186, 'Ответ:', 22, 700)
    if ans == 'text':
        b += ''.join(f'<line x1="{x+240}" y1="{170+j*16}" x2="{x+240+w_}" y2="{170+j*16}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>' for j, w_ in enumerate([170, 130, 150])) + t(x + 240, 230, 'текст', 21, 700, GRAY)
    else:
        b += rect(x + 240, 152, 110, 64, '#DDEBFF', INK, 8, 3) + f'<path d="M{x+244} {212} L{x+280} {176} L{x+305} {200} L{x+322} {186} L{x+346} {212} Z" fill="{G}"/><circle cx="{x+326}" cy="{168}" r="8" fill="#F7A23B"/>' + t(x + 364, 194, 'картинка', 21, 700, GRAY)
svg('s08-compare', 1000, 252, 'Промт для текста: цель, контекст, формат. Промт для картинки: предмет, фон, стиль', b)

# ---------- слайд 10: три рыжих кота на Луне (нарисовано два) ----------
b = moon_scene(0, 0, 600, 380, 'm10', cats=[(0.31, 1.28, True), (0.65, 1.12, False)])
svg('s10-cats', 600, 380, 'Учебная картинка: коты на Луне', b)

# ---------- слайд 11: собака с табличкой ----------
def tree(x, y, k, shades):
    return f'''<g transform="translate({x} {y}) scale({k})">
    <path d="M-9 1v-47H7V1z" fill="#8B6443"/>
    <path d="M0-97L-26-59-20-62-52-20Q0-11 52-20L20-62 26-59Z" fill="{shades[0]}"/>
    <path d="M0-135L-20-98-16-101-40-60Q0-51 40-60L16-101 20-98Z" fill="{shades[1]}"/>
    <path d="M0-177L-31-103Q0-96 31-103Z" fill="{shades[2]}"/></g>'''


def dog(x, y, k=1.0, color='#F2C230', sign='ПРИВКТ'):
    s = lambda v: v*k
    out = f'<ellipse cx="{x+s(4)}" cy="{y+s(5)}" rx="{s(76)}" ry="{s(10)}" fill="#397447" opacity=".24"/>'
    out += f'<path d="M{x+s(54)} {y-s(61)} Q{x+s(81)} {y-s(64)} {x+s(90)} {y-s(98)}" stroke="#A87421" stroke-width="{s(13)}" fill="none" stroke-linecap="round"/>'
    out += f'<path d="M{x+s(54)} {y-s(61)} Q{x+s(81)} {y-s(64)} {x+s(90)} {y-s(98)}" stroke="{color}" stroke-width="{s(9)}" fill="none" stroke-linecap="round"/>'
    for d in (-48, 13, 40):
        out += rect(x + s(d), y - s(35), s(17), s(37), color, '#A87421', r=s(6), sw=s(2))
    out += f'<ellipse cx="{x}" cy="{y-s(50)}" rx="{s(62)}" ry="{s(41)}" fill="{color}" stroke="#A87421" stroke-width="{s(2.5)}"/>'
    out += f'<path d="M{x+s(7)} {y-s(86)}q{s(27)} {s(1)} {s(39)} {s(17)}" stroke="#FFD95B" stroke-width="{s(6)}" fill="none" stroke-linecap="round"/>'
    hx, hy = x - s(62), y - s(100)
    out += f'<circle cx="{hx}" cy="{hy}" r="{s(34)}" fill="{color}" stroke="#A87421" stroke-width="{s(2.5)}"/><ellipse cx="{hx-s(27)}" cy="{hy-s(5)}" rx="{s(12)}" ry="{s(26)}" fill="#BF801A"/><ellipse cx="{hx+s(27)}" cy="{hy-s(5)}" rx="{s(12)}" ry="{s(26)}" fill="#BF801A"/>'
    out += f'<ellipse cx="{hx}" cy="{hy+s(14)}" rx="{s(16)}" ry="{s(13)}" fill="#FFE49A"/>'
    out += f'<circle cx="{hx-s(11)}" cy="{hy-s(7)}" r="{s(5)}" fill="{INK}"/><circle cx="{hx+s(11)}" cy="{hy-s(7)}" r="{s(5)}" fill="{INK}"/><ellipse cx="{hx}" cy="{hy+s(8)}" rx="{s(8)}" ry="{s(6)}" fill="{INK}"/>'
    out += f'<path d="M{hx-s(7)} {hy+s(17)}q{s(7)} {s(8)} {s(14)} 0" fill="none" stroke="#753E29" stroke-width="{s(2)}" stroke-linecap="round"/>'
    sx, sy = x - s(155), y - s(240)
    post = sx + s(116)
    out += f'<path d="M{post} {sy+s(72)} V{y-s(34)}" stroke="#8A5A2B" stroke-width="{s(9)}" stroke-linecap="round"/>'
    out += f'<path d="M{x-s(12)} {y-s(47)} Q{x-s(21)} {y-s(64)} {post} {y-s(55)}" stroke="{color}" stroke-width="{s(18)}" stroke-linecap="round" fill="none"/>'
    out += rect(sx, sy, s(232), s(78), '#FFFFFF', '#8A5A2B', 10, s(5)) + t(sx + s(116), sy + s(56), sign, 42*k, 800, INK, 'middle')
    return out


b = clip('d11', 0, 0, 600, 380) + '<g clip-path="url(#d11)"><rect x="0" y="0" width="600" height="380" fill="#DFF3FF"/>'
b += '<path d="M0 256Q108 174 231 233T430 222Q537 193 600 238V380H0Z" fill="#BDDEAE"/>'
back_fir = ('#91B98A', '#9AC695', '#A1CCA2')
for x, y, scale in [(33, 267, .75), (144, 252, .70), (214, 277, .60), (429, 260, .75), (571, 266, .70)]:
    b += tree(x, y, scale, back_fir)
b += '<path d="M0 283Q105 257 215 280T446 277Q551 257 600 277V380H0Z" fill="#95CD76"/>'
front_fir = ('#26764E', '#318757', '#3D9863')
b += tree(94, 289, 1.1, front_fir) + tree(517, 289, 1.2, front_fir)
for x, y in [(53, 332), (149, 311), (193, 353), (429, 349), (470, 311), (550, 352)]:
    b += f'<path d="M{x-5} {y}q-2-7-5-9m10 9v-12m4 12q4-6 7-7" stroke="#528B4E" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
b += dog(330, 345, 1.15) + '</g>'
svg('s11-dog', 600, 380, 'Учебная картинка: собака в лесу с табличкой', b)

# ---------- слайды практики: две картинки и файл с промтом ----------
def game_picture(x, y, character=False, scale=1):
    if character:
        art = rect(0, 0, 130, 70, '#DDEBFF', r=8)
        art += f'<path d="M65 14v9" stroke="{INK}" stroke-width="4"/><circle cx="65" cy="11" r="4" fill="{RED}"/>'
        art += rect(44, 21, 42, 26, '#5B8DEF', INK, r=6, sw=2)
        art += f'<circle cx="57" cy="33" r="3" fill="{INK}"/><circle cx="73" cy="33" r="3" fill="{INK}"/>'
        art += rect(51, 48, 28, 15, '#5B8DEF', INK, r=4, sw=2)
    else:
        art = rect(0, 0, 130, 70, '#283451', r=8)
        art += '<path d="M6 56Q44 33 80 52T124 52V64H6Z" fill="#D9583B"/><circle cx="98" cy="20" r="9" fill="#F3AD48"/>'
        art += '<path d="M15 55l7-8 10 2 5 6zM92 60l5-8 8-2 10 10z" fill="#F5A16D"/>'
        art += rocket(62, 57, 0.39)
    return f'<g transform="translate({x} {y}) scale({scale})">{art}</g>'


def text_file(x, y):
    return (f'<g transform="translate({x} {y})"><path d="M0 0H45L61 17V73H0Z M45 0V17H61" fill="#FFFFFF" stroke="{INK}"'
            f' stroke-width="3" stroke-linejoin="round"/><path d="M12 29h36M12 42h30M12 55h34" fill="none" stroke="{GRAY}"'
            ' stroke-width="3" stroke-linecap="round"/></g>')


# ---------- слайд 13: две картинки и начало работы ----------
b = rect(10, 8, 360, 124, LIGHT, r=14)
b += game_picture(35, 22, character=True) + game_picture(213, 22)
b += t(100, 119, 'Персонаж', 24, 800, a='middle') + t(278, 119, 'Место игры', 24, 800, a='middle')
for i, (first, second) in enumerate([('Откройте', 'alice.yandex.ru'), ('Начните', 'новый чат'), ('Найдите поле', 'для промта')], 1):
    x = 385 + (i - 1)*205
    b += rect(x, 8, 200, 124, '#F5F5F9', r=14) + num(x + 24, 28, i, INK, 15)
    b += t(x + 100, 71, first, 24, 800, a='middle') + t(x + 100, 103, second, 24, 600, a='middle')
svg('s13-start', 1000, 140, 'Две картинки для игры, персонаж и место. Откройте сайт, начните новый чат и найдите поле для промта', b)

# ---------- слайд 14: промт для персонажа по частям ----------
parts = [(['Нарисуй [кого: персонаж игры, какого он цвета, что у него есть]'], 'subj'),
         (['[где: место из игры].'], 'bg'),
         (['Стиль: [мультфильм, рисунок цветными карандашами,', 'акварель или пластилин].'], 'style')]
b = ''; y = 6
for lines, part in parts:
    _, bg, lab = PARTS[part]
    h = 22 + 36*len(lines)
    b += rect(15, y, 1090, h, bg, r=14) + t(95, y + h/2 + 8, lab, 22, 800, INK, 'middle')
    for k, s in enumerate(lines):
        b += t(178, y + 40 + 36*k, s, 27, 700)
    y += h + 6
svg('s14-template', 1120, y, 'Промт для персонажа: предмет, фон, стиль', b)

# ---------- слайд 15: проверка по промту ----------
b = ''
checks = [('subj', 'Тот персонаж? Цвет, детали, количество?'), ('bg', 'То место, что в промте?'), ('style', 'Тот стиль, что в промте?')]
for k, (part, s) in enumerate(checks):
    _, bg, lab = PARTS[part]
    y = 8 + k*66
    b += rect(15, y, 970, 56, bg, r=14) + t(93, y + 35, lab, 22, 800, INK, 'middle') + t(176, y + 37, s, 24, 600)
svg('s15-check', 1000, 208, 'Проверка картинки по промту: предмет, фон, стиль', b)

# ---------- слайд 16: от уточнения к сравнению ----------
def flag_picture(x, y, flag):
    return f'''<g transform="translate({x} {y})">
    {rect(0, 0, 74, 53, '#DDEBFF', r=6)}
    <path d="M4 47H70V42Q44 30 4 42Z" fill="#77C683"/>
    <path d="M25 43V27H48V43Z" fill="#F7D497" stroke="{INK}" stroke-width="1.7"/>
    <path d="M21 29L37 17L52 29Z" fill="#A75537" stroke="{INK}" stroke-width="1.7"/>
    <path d="M37 43V34H43V43" fill="#A75537"/>
    <path d="M56 37V9" fill="none" stroke="{INK}" stroke-width="2"/>
    <path d="M56 9h13l-3 4 3 4H56z" fill="{flag}"/></g>'''


def chat_bubbles(x, y):
    return f'''<g transform="translate({x} {y})">
    <path d="M12 4h59a10 10 0 0 1 10 10v6a10 10 0 0 1-10 10H26l-13 8v-8h-1A10 10 0 0 1 2 20v-6A10 10 0 0 1 12 4z" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/>
    <path d="M51 27h60a10 10 0 0 1 10 10v6a10 10 0 0 1-10 10h-1v8l-13-8H51a10 10 0 0 1-10-10v-6a10 10 0 0 1 10-10z" fill="{VB}" stroke="{INK}" stroke-width="3"/>
    <path d="M18 17h43M56 40h47" fill="none" stroke="{GRAY}" stroke-width="3" stroke-linecap="round"/>
    </g>'''


first_flag, new_flag = '#D74743', '#3275C7'
icons = [
    chat_bubbles(103, 21),
    flag_picture(411, 25, first_flag) + arrow(491, 51, 513, 51, GRAY, 3) + flag_picture(519, 25, new_flag),
    text_file(774, 22) + flag_picture(862, 32, new_flag) + '<path d="M840 56l6 7l10-12" fill="none" stroke="#087D46" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',
]
b = ''
for k, (a1, a2) in enumerate([('Уточнение', 'в том же чате'), ('Новая картинка', 'что изменилось?'), ('Проверка', 'что сохранилось?')]):
    x = 15 + k*335
    b += rect(x, 8, 300, 158, LIGHT, r=16) + num(x + 30, 31, k + 1, INK, 16) + icons[k]
    b += t(x + 150, 122, a1, 24, 800, a='middle') + t(x + 150, 151, a2, 22, 600, GRAY, 'middle')
    if k < 2:
        b += arrow(x + 305, 82, x + 330, 82)
b += t(500, 192, 'Картинки с домом нарисованы для урока', 22, 600, GRAY, 'middle')
svg('s16-flow', 1000, 202, 'Уточнение в том же чате. Сравните учебные картинки и проверьте, что изменилось и что сохранилось', b)


# ---------- слайд 21: три действия при показе ----------
b = ''
for k, (a1, a2) in enumerate([('Выберите', 'одну картинку'), ('Прочитайте', 'свой промт'), ('Назовите деталь,', 'которая совпала')]):
    x = 15 + k*335
    b += rect(x, 10, 300, 92, LIGHT) + num(x + 34, 56, k + 1, INK)
    b += t(x + 64, 50, a1, 23, 700) + t(x + 64, 80, a2, 21, 600, GRAY)
    if k < 2:
        b += arrow(x + 304, 56, x + 331, 56)
svg('s21-show', 1000, 112, 'Покажите одну картинку, прочитайте промт и назовите совпавшую деталь', b)

# ---------- слайд 17: переводим взгляд вдаль ----------
b = rect(15, 20, 300, 190, LIGHT, r=18) + rect(60, 50, 210, 120, '#FFFFFF', MUTE, r=10, sw=4)
b += rect(145, 170, 40, 22, MUTE, r=0) + t(165, 123, 'Экран', 31, 700, GRAY, 'middle')
b += arrow(330, 115, 650, 115, G, 6) + t(490, 89, 'Смотрим вдаль', 31, 700, '#087D46', 'middle')
b += rect(665, 20, 320, 190, GB, r=18) + rect(710, 50, 230, 130, '#BFE8FF', INK, r=0, sw=5)
b += '<path d="M835 176L883 131L934 176Z" fill="#0FBF6E"/><circle cx="763" cy="84" r="18" fill="#FFD84D"/>'
b += '<path d="M825 50v130M710 115h230" stroke="#17171C" stroke-width="5"/>'
svg('s17-pause', 1000, 230, 'Отводим взгляд от экрана и смотрим вдаль, например в окно', b)

# ---------- слайд 18: сохранить картинку ----------
b = ''
cards = [('Откройте', 'картинку'), ('Скачайте', 'файл'), ('Взрослый кладёт', 'в папку «Постер»')]
for k, (a1, a2) in enumerate(cards):
    x = 15 + k*330
    b += rect(x, 12, 290, 228, LIGHT, 'none', 18) + num(x + 34, 48, k + 1, INK, 18) + t(x + 64, 46, a1, 22, 700) + t(x + 64, 74, a2, 22, 700)
    cx = x + 145
    if k == 0:
        b += rect(cx - 70, 97, 140, 91, '#FFFFFF', INK, 10, 3)
        b += game_picture(cx - 65, 108, character=True)
    if k == 1:
        b += f'<line x1="{cx}" y1="100" x2="{cx}" y2="160" stroke="{INK}" stroke-width="8" stroke-linecap="round"/><path d="M{cx-26} 140 L{cx} 168 L{cx+26} 140" stroke="{INK}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/><line x1="{cx-40}" y1="184" x2="{cx+40}" y2="184" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>' + t(cx, 224, 'Значок может отличаться', 19, 600, GRAY, 'middle')
    if k == 2:
        b += f'<path d="M{cx-66} 110H{cx-23}L{cx-10} 123H{cx+66}V195H{cx-66}Z" fill="#F0AB38" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
        b += game_picture(cx - 48, 103, character=True, scale=.74)
        b += f'<path d="M{cx-66} 140H{cx+66}V195H{cx-66}Z" fill="#F7C64B" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>' + t(cx, 177, 'Постер', 22, 800, INK, 'middle')
    if k < 2:
        b += arrow(x + 296, 126, x + 324, 126)
svg('s18-save', 1000, 250, 'Открыть картинку, скачать на компьютер, взрослый кладёт файл в папку «Постер»', b)

# ---------- слайд 19: свой промт места действия ----------
place = rect(103, 29, 134, 79, SKY, r=12)
place += '<circle cx="169" cy="70" r="25" fill="#D9583B"/><path d="M147 60q22-9 38 7m-37 16q16-9 35-1" fill="none" stroke="#F5A16D" stroke-width="3" stroke-linecap="round"/>'
place += '<circle cx="121" cy="46" r="2.8" fill="#FFFFFF"/><circle cx="218" cy="68" r="2.8" fill="#FFFFFF"/>'

details = '<path d="M475 94l12-17 15-1 10 16-10 5h-20zM452 104l8-11 13 3 3 8z" fill="#D9583B" stroke="#943E2A" stroke-width="2" stroke-linejoin="round"/>'
details += rocket(545, 104, 0.55)

style = '<path d="M774 83q13-32 29-17t28-12v37q-27 25-57-8z" fill="#DB7456" opacity=".7"/><path d="M769 89q21-18 42-5t21-28m-57 36q29 10 52-5" fill="none" stroke="#DF916A" stroke-width="7" stroke-linecap="round" opacity=".72"/>'
style += '<path d="M865 79l29-29q4-4 8 0q4 4 0 8l-29 30z" fill="#9C603F" stroke="#633D21" stroke-width="2.5" stroke-linejoin="round"/><path d="M860 83l5-5 10 10-5 5z" fill="#CED7E0" stroke="#495565" stroke-width="2"/><path d="M860 83q-8 2-13 17q13 2 23-7z" fill="#CC5236" stroke="#8E3D29" stroke-width="2"/>'

b = ''
questions = [('Где идёт игра?', 'красная планета', GB, place),
             ('Что там есть?', 'камни и ракета', GB, details),
             ('Какой стиль?', 'например, акварель', AMB, style)]
for k, (question, example, bg, art) in enumerate(questions):
    x = 15 + k*330
    b += rect(x, 12, 310, 166, bg) + art
    b += t(x + 155, 137, question, 24, 800, a='middle') + t(x + 155, 164, example, 22, 600, GRAY, 'middle')
svg('s19-own', 1000, 190, 'Из чего собрать промт для места. Пример: красная планета, камни и ракета, акварель', b)

# ---------- слайд 20: отправить картинки ----------
def person(x, y, r=34):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}"/><circle cx="{x}" cy="{y-9}" r="{r*0.3}" fill="#FFFFFF"/><path d="M{x-r*0.52} {y+r*0.62} C{x-r*0.52} {y+r*0.05},{x+r*0.52} {y+r*0.05},{x+r*0.52} {y+r*0.62} Z" fill="#FFFFFF"/>'


b = ''
for k, (a1, a2) in enumerate([('Персонаж', 'и его промт'), ('Место действия', 'и его промт')]):
    x = 15 + k*265
    b += rect(x, 12, 245, 210, LIGHT, r=18)
    b += game_picture(x + 19, 54, character=(k == 0), scale=0.9) + text_file(x + 158, 50)
    b += t(x + 122, 166, a1, 23, 800, INK, 'middle') + t(x + 122, 196, a2, 22, 600, GRAY, 'middle')
b += arrow(545, 117, 680, 117) + t(612, 92, 'Взрослый', 22, 700, GRAY, 'middle') + t(612, 152, 'отправляет', 22, 600, GRAY, 'middle')
b += rect(700, 12, 285, 210, LIGHT, 'none', 18) + person(842, 92) + t(842, 178, 'Преподаватель', 23, 700, INK, 'middle')
svg('s20-send', 1000, 232, 'Взрослый отправляет преподавателю две картинки и их промты', b)

# ---------- запасной план: учебные картинки ----------
def robot(x, y, color, k=1.0):
    s = lambda v: v*k
    out = f'<line x1="{x}" y1="{y-s(170)}" x2="{x}" y2="{y-s(196)}" stroke="{INK}" stroke-width="{s(5)}"/><circle cx="{x}" cy="{y-s(200)}" r="{s(8)}" fill="{RED}"/>'
    out += rect(x - s(44), y - s(170), s(88), s(66), color, INK, s(14), s(4)) + f'<circle cx="{x-s(18)}" cy="{y-s(140)}" r="{s(9)}" fill="#FFFFFF"/><circle cx="{x+s(18)}" cy="{y-s(140)}" r="{s(9)}" fill="#FFFFFF"/><circle cx="{x-s(18)}" cy="{y-s(140)}" r="{s(4)}" fill="{INK}"/><circle cx="{x+s(18)}" cy="{y-s(140)}" r="{s(4)}" fill="{INK}"/><rect x="{x-s(20)}" y="{y-s(120)}" width="{s(40)}" height="{s(6)}" rx="3" fill="{INK}"/>'
    out += rect(x - s(52), y - s(98), s(104), s(80), color, INK, s(14), s(4)) + rect(x - s(22), y - s(80), s(44), s(30), '#FFFFFF', INK, s(6), s(3))
    out += f'<rect x="{x-s(40)}" y="{y-s(18)}" width="{s(22)}" height="{s(20)}" rx="4" fill="{INK}"/><rect x="{x+s(18)}" y="{y-s(18)}" width="{s(22)}" height="{s(20)}" rx="4" fill="{INK}"/>'
    out += f'<line x1="{x-s(52)}" y1="{y-s(80)}" x2="{x-s(84)}" y2="{y-s(46)}" stroke="{INK}" stroke-width="{s(8)}" stroke-linecap="round"/><line x1="{x+s(52)}" y1="{y-s(80)}" x2="{x+s(86)}" y2="{y-s(110)}" stroke="{INK}" stroke-width="{s(8)}" stroke-linecap="round"/>'
    wx, wy = x + s(92), y - s(118)
    out += f'<g transform="rotate(-30 {wx} {wy})"><rect x="{wx-s(6)}" y="{wy-s(30)}" width="{s(12)}" height="{s(54)}" rx="4" fill="#9C9AA6" stroke="{INK}" stroke-width="{s(3)}"/><path d="M{wx-s(16)} {wy-s(30)} a{s(16)} {s(16)} 0 1 1 {s(32)} 0 l-{s(10)} 0 l0 {s(10)} l-{s(12)} 0 l0 -{s(10)} Z" fill="#9C9AA6" stroke="{INK}" stroke-width="{s(3)}"/></g>'
    return out


def planet(cid, with_robot=None):
    out = clip(cid, 0, 0, 600, 380) + f'<g clip-path="url(#{cid})"><rect x="0" y="0" width="600" height="380" fill="{SKY}"/>'
    rnd = random.Random(5)
    out += ''.join(f'<circle cx="{rnd.random()*600:.0f}" cy="{rnd.random()*200:.0f}" r="{rnd.choice([1.5,2,2.5])}" fill="#FFFFFF"/>' for _ in range(30))
    out += '<path d="M0 270 Q150 240 300 262 T600 250 L600 380 L0 380 Z" fill="#D9583B"/>'
    for x, y, scale in [(80, 320, 0.9), (148, 353, 0.5), (524, 332, 1.15), (380, 320, 0.45)]:
        out += f'<g transform="translate({x} {y}) scale({scale})"><path d="M-26 0 L-17 -16 L5 -21 L23 -10 L28 1 L10 7 L-17 7 Z" fill="#8F392B" stroke="#6A2E25" stroke-width="2"/><path d="M-26 0 L-17 -16 L5 -21 L23 -10 L4 0 Z" fill="#F5A16D"/></g>'
    out += rocket(428, 300, 1.6)
    if with_robot:
        out += robot(230, 330, with_robot)
    return out + '</g>' + t(300, 411, 'Учебная картинка, нарисована для урока', 22, 700, GRAY, 'middle')


svg('fb-robot1', 600, 424, 'Учебная картинка 1, нарисована для урока: зелёный робот с гаечным ключом возле ракеты на красной планете', planet('r1', '#5CCB7A'))
svg('fb-robot2', 600, 424, 'Учебная картинка 2, нарисована для урока: синий робот с гаечным ключом возле ракеты на красной планете', planet('r2', '#5B8DEF'))
svg('fb-place', 600, 424, 'Учебная картинка 3, нарисована для урока: красная планета с камнями и ракетой', planet('r3'))


# ---------- домашнее задание: два рисунка для сравнения ----------
def turtle_river(name, watercolor=False, backpack=None):
    width, height = 480, 240
    sky, far_bank, river, near_bank = (
        ('#F5EBD8', '#CDDDB7', '#A6CED6', '#E8D9AC') if watercolor
        else ('#CDEDFB', '#BCE295', '#64CBE7', '#F7E1A4')
    )
    out = clip(name, 0, 0, width, height) + f'<g clip-path="url(#{name})">'
    out += rect(0, 0, width, height, sky, r=0)
    out += f'<path d="M0 104 Q85 58 171 103 Q254 145 343 97 Q420 57 480 91 V180 H0Z" fill="{far_bank}"/>'
    out += f'<path d="M0 126 Q100 102 191 123 Q264 148 339 123 Q416 101 480 120 V240 H0Z" fill="{river}"/>'
    out += f'<path d="M0 184 Q123 205 213 176 Q325 143 480 184 V240 H0Z" fill="{near_bank}"/>'
    for x, y, length in [(22, 151, 67), (94, 172, 37), (300, 145, 51), (391, 161, 65), (5, 168, 27)]:
        out += f'<path d="M{x} {y} q{length/2} 3 {length} 0" fill="none" stroke="#FFFFFF" stroke-opacity=".6" stroke-linecap="round" stroke-width="3"/>'
    for x, y in [(41, 214), (146, 221), (384, 202), (448, 218)]:
        out += f'<path d="M{x-10} {y} q-3 -9 -8 -13 M{x} {y} q0 -13 -4 -21 M{x+8} {y} q5 -10 11 -11" fill="none" stroke="#738C52" stroke-width="3" stroke-linecap="round"/>'
    if watercolor:
        out += '<path d="M-12 97 Q91 58 176 101 T347 93 T486 82" fill="none" stroke="#B2CA91" stroke-opacity=".64" stroke-width="22" filter="url(#wash)"/>'
        out += '<path d="M-10 151 Q85 131 166 150 T320 148 T490 134" fill="none" stroke="#62A9C0" stroke-opacity=".38" stroke-width="20" filter="url(#wash)"/>'
    out += '<g transform="translate(108 45)">'
    if watercolor:
        out += '<g fill="#759953" opacity=".86" filter="url(#pigment)"><path d="M51 130 Q30 120 13 134 Q31 148 61 145Z"/><path d="M81 137 Q66 146 66 161 Q75 174 101 156 L105 143Z"/><path d="M163 138 Q173 149 176 163 Q190 170 198 155 L185 132Z"/><path d="M173 113 Q180 101 191 100 Q195 78 220 79 Q245 81 247 101 Q242 118 220 117 Q209 134 183 137Z"/></g>'
        out += '<path d="M44 136 Q44 70 103 70 Q162 64 186 112 Q193 141 156 149 Q102 159 48 144Z" fill="#6D8C45" opacity=".86" filter="url(#pigment)"/>'
        out += '<path d="M51 130 Q58 82 96 80 Q143 72 171 102 Q147 101 135 125 Q115 115 92 132 Q66 119 51 130Z" fill="#ADBC65" opacity=".6" filter="url(#wash)"/>'
        out += '<path d="M91 78 Q111 98 108 137 M130 77 Q142 96 141 139 M61 108 Q116 96 167 109" fill="none" stroke="#526E43" stroke-width="2.4" stroke-opacity=".54"/>'
        out += '<circle cx="231" cy="96" r="3.4" fill="#33492C"/><path d="M232 108 q7 2 10 -2" fill="none" stroke="#48623C" stroke-width="2"/>'
        if backpack:
            out += '<g filter="url(#pigment)" opacity=".92"><path d="M85 77 Q108 46 138 70 Q155 84 148 113 L88 126 Q72 115 77 96Z" fill="#577CB8"/><path d="M94 70 Q101 49 116 53 Q127 56 130 67 M143 75 Q159 82 165 101" fill="none" stroke="#405F86" stroke-width="4"/><path d="M87 96 Q111 88 140 91 L141 107 Q119 113 91 114Z" fill="#8EB7D7"/></g>'
    else:
        out += '<g stroke="#304927" stroke-width="4" stroke-linejoin="round"><path d="M51 130 Q30 120 13 134 Q31 148 61 145Z" fill="#9DD560"/><path d="M81 137 Q66 146 66 161 Q75 174 101 156 L105 143Z M163 138 Q173 149 176 163 Q190 170 198 155 L185 132Z" fill="#9DD560"/><path d="M173 113 Q180 101 191 100 Q195 78 220 79 Q245 81 247 101 Q242 118 220 117 Q209 134 183 137Z" fill="#9DD560"/>'
        out += '<path d="M44 136 Q44 70 103 70 Q162 64 186 112 Q193 141 156 149 Q102 159 48 144Z" fill="#6FAE47"/></g>'
        out += '<path d="M81 87 Q67 101 64 120 M159 88 Q172 103 177 122 M57 130 Q115 142 178 128" fill="none" stroke="#426E35" stroke-width="3"/>'
        out += '<path d="M85 77 Q108 46 138 70 Q155 84 148 113 L88 126 Q72 115 77 96Z" fill="#D84343" stroke="#712D35" stroke-width="4" stroke-linejoin="round"/><path d="M94 70 Q101 49 116 53 Q127 56 130 67" fill="none" stroke="#712D35" stroke-width="5" stroke-linecap="round"/><path d="M87 96 Q111 88 140 91 L141 107 Q119 113 91 114Z" fill="#F77765" stroke="#712D35" stroke-width="2.5"/><path d="M143 75 Q159 82 165 101" fill="none" stroke="#712D35" stroke-width="4" stroke-linecap="round"/>'
        out += '<circle cx="231" cy="96" r="4.3" fill="#304927"/><path d="M232 108 q7 2 10 -2" fill="none" stroke="#304927" stroke-width="2.6" stroke-linecap="round"/>'
    out += '</g>'
    if watercolor:
        rng = random.Random(25)
        for _ in range(260):
            x, y = rng.uniform(0, width), rng.uniform(0, height)
            out += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(0.35, 1.5):.1f}" fill="{rng.choice(("#92794F", "#FFFAEC"))}" opacity=".22"/>'
    return out + '</g>'


defs = '''<defs>
<filter id="wash" x="-15%" y="-25%" width="130%" height="150%"><feGaussianBlur stdDeviation="2.2"/></filter>
<filter id="pigment" x="-10%" y="-12%" width="120%" height="124%">
<feTurbulence type="fractalNoise" baseFrequency=".09" numOctaves="3" seed="11" result="grain"/>
<feDisplacementMap in="SourceGraphic" in2="grain" scale="7" xChannelSelector="R" yChannelSelector="G"/>
</filter></defs>'''

def turtle_pair(name, backpack_in_watercolor=False):
    body = f'<g transform="translate(10 38)">{turtle_river(name + "-cartoon")}</g>'
    body += f'<g transform="translate(510 38)">{turtle_river(name + "-watercolor", watercolor=True, backpack=backpack_in_watercolor)}</g>'
    body += t(250, 27, 'Мультфильм', 24, 800, INK, 'middle') + t(750, 27, 'Акварель', 24, 800, INK, 'middle')
    body += t(500, 309, 'Обе картинки нарисованы для урока', 23, 600, GRAY, 'middle')
    svg(name, 1000, 319, 'Две учебные картинки с зелёной черепахой на берегу реки, мультфильм и акварель', body, defs)


turtle_pair('hw-pair')
turtle_pair('hw-offline', backpack_in_watercolor=True)

print('SVG:', sorted(p.name for p in OUT.glob('*.svg')))
