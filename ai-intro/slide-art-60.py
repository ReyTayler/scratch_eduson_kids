"""Native SVG teaching diagrams and Eduson Kids slide components."""
from html import escape as e

INK='#17171C'
VIOLET='#6F61E8'
GREEN='#0FBF6E'
FONT='font-family="Inter, sans-serif"'
DIGITS={
 '1':'M18 24L33 8V72',
 '1s':'M31 8V72',
 '1b':'M15 27L32 9L30 70M17 71H44',
 '1k':'M38 8Q32 40 25 72',
 '17':'M17 20L39 11L29 72',
 '2':'M14 22Q20 6 34 8Q50 14 40 34L12 70H50',
 '3':'M14 16Q30 2 44 14Q50 28 30 38Q54 42 46 62Q30 80 12 64',
 '5':'M44 10H20L16 38Q34 28 44 44Q50 64 30 70Q18 72 12 62',
 '7':'M12 12H48L24 72',
 '7c':'M12 14Q30 8 48 12L26 72M18 42H42',
 '7k':'M14 10L50 14Q38 40 30 72',
 '8':'M42 18Q36 6 28 8Q12 12 20 26Q26 36 36 44Q50 56 40 68Q28 78 18 68Q8 54 28 38Q48 26 42 18Z',
}
def digit(name,color=INK):
    return f'<svg class="digit" viewBox="0 0 60 80" role="img" aria-label="Цифра {name[0]}, написанная от руки"><path d="{DIGITS[name]}" fill="none" stroke="{color}" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def cover_art():
    return '<div class="cover-digits">'+''.join(f'<div class="digit-tile">{digit(d)}</div>' for d in ['3','7c','1b','8','5'])+'</div>'

def icon(body,label):
    return f'<svg class="ability-icon" viewBox="0 0 96 96" role="img" aria-label="{label}"><circle cx="48" cy="48" r="48" fill="#F0EEFE"/>{body}</svg>'
ABILITIES=[
 icon(f'<g stroke="{INK}" stroke-width="3" stroke-linejoin="round"><path d="M18 24H52V50H32L24 58V50H18Z" fill="#fff"/><path d="M44 42H78V68H72V76L64 68H44Z" fill="#8C7FF6"/></g><text x="35" y="44" text-anchor="middle" {FONT} font-size="19" font-weight="800" fill="{INK}">A</text><text x="61" y="62" text-anchor="middle" {FONT} font-size="19" font-weight="800" fill="#fff">Я</text>','Два облачка с буквами разных языков'),
 icon(f'<path d="M26 40V56M34 30V66M42 40V56M18 46V50" stroke="{VIOLET}" stroke-width="5" stroke-linecap="round"/><rect x="52" y="28" width="28" height="40" rx="4" fill="#fff" stroke="{INK}" stroke-width="3"/><path d="M58 38H74M58 48H74M58 58H68" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>','Звуковая волна и страница с текстом'),
 icon(f'<rect x="24" y="18" width="44" height="60" rx="5" fill="#fff" stroke="{INK}" stroke-width="3"/><path d="M33 32H59M33 43H59M33 54H48" stroke="{INK}" stroke-width="3" stroke-linecap="round"/><path d="M50 72L54 60L72 42L80 50L62 68Z" fill="#8C7FF6" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>','Страница и карандаш'),
 icon(f'<rect x="18" y="24" width="60" height="48" rx="6" fill="#fff" stroke="{INK}" stroke-width="3"/><circle cx="62" cy="38" r="6" fill="#3DF79D" stroke="{INK}" stroke-width="2.5"/><path d="M24 66L40 44L52 58L60 50L72 66Z" fill="#8C7FF6" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>','Картинка с горами и солнцем'),
]
def box(x,y,w,h,text,fill='#fff',size=20):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{INK}" stroke-width="2.5"/><text x="{x+w/2}" y="{y+h/2+size*.36}" text-anchor="middle" {FONT} font-size="{size}" font-weight="700" fill="{INK}">{e(text)}</text>'
def pointer(x,y):
    return f'<path d="M{x} {y}H{x+24}M{x+16} {y-8}L{x+25} {y}L{x+16} {y+8}" fill="none" stroke="{VIOLET}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
def placed(name,x,y,h=72,color=INK):
    return f'<g transform="translate({x} {y}) scale({h/80})"><path d="{DIGITS[name]}" fill="none" stroke="{color}" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"/></g>'
def rules_art():
    left=f'<svg class="flow" viewBox="0 0 520 156" role="img" aria-label="Схема калькулятора: два плюс три, правило сложить, ответ пять">{box(4,41,118,74,"2 + 3",size=28)}{pointer(132,78)}{box(166,41,190,74,"Сложить",fill="#F0EEFE",size=24)}{pointer(366,78)}{box(400,41,116,74,"5",size=32)}</svg>'
    rows=''.join(f'<text x="2" y="{y+39}" {FONT} font-size="17" font-weight="700" fill="{INK}">{label}</text>'+''.join(placed(d,100+i*50,y,62) for i,d in enumerate(ds)) for y,label,ds in [(8,"Единицы",["1","1b","1k"]),(86,"Семёрки",["7","7c","7k"])])
    right=f'<svg class="flow" viewBox="0 0 520 156" role="img" aria-label="Три единицы и три семёрки, написанные по-разному, и вопрос: какое правило их различит?"><rect x="92" y="2" width="162" height="152" rx="14" fill="#fff" stroke="{INK}" stroke-width="2.5"/>{rows}{pointer(264,78)}{box(300,41,216,74,"Какое правило?",fill="#FFECEC",size=22)}</svg>'
    return f'<div class="rules"><div><h3>Обычная программа: калькулятор</h3>{left}<p>Правило заранее записал человек.</p></div><div class="new-sample"><h3>Задача: узнать цифру на картинке</h3>{right}<p>Каждый пишет цифры по-своему.</p></div></div>'
def labels_art():
    tiles=[('7','7'),('1s','1'),('3','3'),('8','8'),('1b','1'),('7c','7'),('5','5'),('2','2')]
    return '<div class="label-grid">'+''.join(f'<div class="digit-tile">{digit(d)}<span class="lbl"><i>?</i><b>{l}</b></span></div>' for d,l in tiles)+'</div>'
def training_art(s):
    rows=''.join(f'<path d="M14 {y}H106" stroke="{INK}" stroke-width="4" stroke-linecap="round"/><circle cx="{x}" cy="{y}" r="9" fill="#8C7FF6" stroke="{INK}" stroke-width="3"/>' for y,x in [(20,78),(46,36),(72,62)])
    step=[f'<svg class="step-art" viewBox="0 0 120 92" role="img" aria-label="Семёрка от руки с подписью семь"><rect x="8" y="6" width="62" height="80" rx="10" fill="#fff" stroke="{INK}" stroke-width="2.5"/>{placed("7c",14,16,60)}<text x="94" y="56" text-anchor="middle" {FONT} font-size="24" font-weight="800" fill="{GREEN}">«7»</text></svg>',
     f'<svg class="step-art" viewBox="0 0 120 92" role="img" aria-label="Ответ нейросети: один"><path d="M12 8H108V66H54L38 84V66H12Z" fill="#F0EEFE" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/><text x="60" y="49" text-anchor="middle" {FONT} font-size="32" font-weight="800" fill="{VIOLET}">«1»</text></svg>',
     f'<svg class="step-art" viewBox="0 0 120 92" role="img" aria-label="Семь не равно один"><text x="60" y="60" text-anchor="middle" {FONT} font-size="42" font-weight="800"><tspan fill="{GREEN}">7</tspan><tspan fill="#E04848"> ≠ </tspan><tspan fill="{VIOLET}">1</tspan></text></svg>',
     f'<svg class="step-art" viewBox="0 0 120 92" role="img" aria-label="Три регулятора в разных положениях">{rows}</svg>']
    return '<div class="pipeline">'+''.join(f'<div>{step[i]}<h3>{e(a)}</h3><p>{e(b)}</p></div>' for i,(a,b) in enumerate(s['cards']))+'</div><div class="strip">Шаги повторяются снова и снова на множестве примеров</div>'
def color_case_art():
    ones=''.join(f'<div class="digit-tile">{digit(d,VIOLET)}</div>' for d in ['1','1s','1b'])
    sevens=''.join(f'<div class="digit-tile">{digit(d,GREEN)}</div>' for d in ['7','7c','7k'])
    bubble=f'<svg class="guess-bubble" viewBox="0 0 210 120" role="img" aria-label="Нейросеть могла бы ответить: это семь"><path d="M24 4H200Q206 4 206 10V110Q206 116 200 116H24Q18 116 18 110V70L4 58L18 48V10Q18 4 24 4Z" fill="#fff" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/><text x="112" y="34" text-anchor="middle" {FONT} font-size="17" font-weight="600" fill="#3C3C45">Нейросеть могла</text><text x="112" y="56" text-anchor="middle" {FONT} font-size="17" font-weight="600" fill="#3C3C45">бы ответить:</text><text x="112" y="96" text-anchor="middle" {FONT} font-size="28" font-weight="800" fill="#E04848">«Это 7»</text></svg>'
    return f'<div class="color-case"><div><h3>Примеры для обучения</h3><div class="color-row"><span>Единицы</span>{ones}</div><div class="color-row"><span>Семёрки</span>{sevens}</div></div><div class="new-sample"><h3>Новая картинка: единица</h3><div class="guess"><div class="digit-tile big">{digit("1",GREEN)}</div>{bubble}</div></div></div>'
def missing_art():
    def filled(a,b,color):
        return f'<div class="combo-cell">{digit(a,color)}{digit(b,color)}</div>'
    def empty(a,b,color):
        return f'<div class="combo-cell is-missing"><i>?</i><span>{digit(a,color)}{digit(b,color)}</span></div>'
    return f'<div class="combo"><div class="combo-table"><b></b><b>Фиолетовая</b><b>Зелёная</b><b>Единица</b>{filled("1","1s",VIOLET)}{empty("1b","1k",GREEN)}<b>Семёрка</b>{empty("7c","7k",VIOLET)}{filled("7","7c",GREEN)}</div><div class="combo-note"><h3>Что дальше</h3><p>Добавить примеры.</p><p>Обучить заново.</p><p>Проверить на новых картинках.</p></div></div>'
def guess_art():
    cols=[(320,[50,110,170]),(410,[20,80,140,200]),(500,[50,110,170])]
    links=''.join(f'<path d="M{a[0]} {p}L{b[0]} {q}" stroke="#A79EF9" stroke-width="2"/>' for a,b in zip(cols,cols[1:]) for p in a[1] for q in b[1])
    nodes=''.join(f'<circle cx="{c[0]}" cy="{p}" r="14" fill="#8C7FF6" stroke="{INK}" stroke-width="2.5"/>' for c in cols for p in c[1])
    picture=f'<rect x="54" y="20" width="136" height="180" rx="18" fill="#fff" stroke="{INK}" stroke-width="2.5"/>{placed("17",68,36,148)}'
    bars=''.join(f'<text x="600" y="{y+33}" {FONT} font-size="32" font-weight="800" fill="{INK}">{d}</text><rect x="640" y="{y}" width="{w}" height="46" rx="12" fill="{c}" stroke="{INK}" stroke-width="2.5"/>' for y,d,w,c in [(30,"1",300,"#A79EF9"),(88,"7",230,"#C9C3FB"),(146,"2",60,"#E3E3EA")])
    return f'<svg class="live-flow" viewBox="0 0 1000 220" role="img" aria-label="Схема: неразборчивая цифра, нейросеть из связанных кружков и три полосы с ответами. Длиннее всего полоса единицы, затем семёрки, короче всего двойки">{picture}{pointer(246,110)}{links}{nodes}{pointer(538,110)}{bars}</svg><div class="strip">Это схема: длина полос условная</div>'
def text_art(s):
    chain=f'<svg class="flow" viewBox="0 0 560 172" role="img" aria-label="Схема: начало фразы и три возможных продолжения, чаще подходит слово дерево, реже облако"><text x="4" y="94" {FONT} font-size="26" font-weight="700" fill="{INK}">Кот залез на…</text><text x="4" y="124" {FONT} font-size="17" font-weight="500" fill="#62616C">Схема упрощена</text>{pointer(186,86)}'
    for y,w,word,fill in [(20,270,'дерево','#A79EF9'),(76,180,'крышу','#C9C3FB'),(132,72,'облако','#E3E3EA')]:
        chain+=f'<rect x="226" y="{y}" width="{w}" height="40" rx="10" fill="{fill}" stroke="{INK}" stroke-width="2"/><text x="{226+w+10 if w<120 else 240}" y="{y+27}" {FONT} font-size="21" font-weight="700" fill="{INK}">{word}</text>'
    chain+='</svg>'
    return f'<div class="text-demo"><div><h3>Выбирает, что подойдёт дальше</h3>{chain}</div><div class="text-reply"><h3>Складно, но неверно</h3><p class="wrong-fact">«У обычной кошки шесть лап».</p><p>Уверенный тон не доказывает, что это правда.</p></div></div><div class="strip">До разговора её обучали на текстах. В разговоре заново не учат</div>'

def steps(s):
    return '<ol class="steps">'+''.join(f'<li>{e(b)}</li>' for a,b in s['cards'])+'</ol>'

def cards(s):
    return '<div class="cards count-'+str(len(s['cards']))+'">'+''.join(f'<div class="info-card"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a,b in s['cards'])+'</div>'

def home_art(s):
    cards=''.join(f'<div class="info-card"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a,b in s['cards'])
    return f'<div class="grid-3">{cards}</div><div class="strip">Хотите иначе? Подойдёт свой формат: подпись к рисунку, девиз, название для команды</div>'
def home_example_art():
    card=lambda tag,ask,reply,check,cls:f'<div class="prompt-card"><span class="pc-tag">{tag}</span><p class="pc-text">{ask}</p><p class="hw-reply"><b>Ответ:</b> {reply}</p><p class="hw-check {cls}"><b>Шаг 2. Проверка:</b> {check}</p></div>'
    before=card('Шаг 1. Запрос','«Придумай загадку про жирафа»','«Он высокий, с длинной шеей, ест листья. Кто это?»','слишком легко, сразу понятно, кто это.','is-no')
    after=card('Шаг 3. Уточнение','«Сделай загадку сложнее. Про шею не пиши. Сравни жирафа с башней»','«Я живая башня, что тянется к облакам. Пятнистый узор — мой наряд, листья — мой обед. Кто я?»','получилась загадка, животное не названо.','is-yes')
    go=f'<svg class="hw-go" viewBox="0 0 40 40" aria-hidden="true"><path d="M6 20H32M22 10L33 20L22 30" fill="none" stroke="{VIOLET}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    return f'<div class="hw-compare">{before}{go}{after}</div><div class="strip">С первого раза получается редко. Уточнение — обычная часть работы</div>'

def art(s):
    k=s['kind']
    if k=='home':return home_art(s)
    if k=='home-example':return home_example_art()
    if k=='agenda':return '<div class="agenda">'+''.join('<div class="agenda-row"><span class="t">'+e(a)+'</span><div><div class="tt">'+e(b.split(': ',1)[0])+'</div><div class="dd">'+e(b.split(': ',1)[1][:1].upper()+b.split(': ',1)[1][1:])+'</div></div></div>' for a,b in s['cards'])+'</div>'
    if k=='goals':return '<div class="ek-note">'+e(s['lead'])+'</div><div class="grid-2">'+''.join('<div class="info-card"><h3>'+e(a)+'</h3><ul class="clean">'+''.join('<li>'+e(x)+'</li>' for x in b.split('; '))+'</ul></div>' for a,b in s['cards'])+'</div>'
    if k=='results':return '<div class="ek-note ek-note--green">'+e(s['lead'])+'</div><div class="grid-2">'+''.join('<div class="info-card"><h3>'+e(a)+'</h3><ul class="clean">'+''.join('<li>'+e(x)+'</li>' for x in b.split('; '))+'</ul></div>' for a,b in s['cards'])+'</div>'+'<div class="lesson-question ek-note"><p>'+e(s['question'])+'</p></div>'
    if k=='abilities':return '<div class="abilities">'+''.join(f'<div class="info-card">{ABILITIES[i]}<h3>{e(a)}</h3><p>{e(b)}</p></div>' for i,(a,b) in enumerate(s['cards']))+'</div>'
    if k=='rules':return rules_art()
    if k=='labels':return labels_art()
    if k=='pipeline':return training_art(s)
    if k=='new-case':return color_case_art()
    if k=='missing':return missing_art()
    if k=='guess':return guess_art()
    if k=='text':return text_art(s)
    if k=='privacy':return '<div class="privacy-demo"><h3>Этого достаточно для ответа</h3><p>«Расскажи про кошку. Напиши три предложения».</p></div>'+cards(s)
    if k in ['practice','response']:return steps(s)
    if k=='prompt':return '<div class="prompt-card"><span class="pc-tag">Новый чат · Алиса AI</span><p class="pc-text">'+e(s['lead'])+'</p></div>'+steps(s)
    if k=='revision':return '<div class="prompt-card"><span class="pc-tag">Тот же чат · выберите одну просьбу</span><p class="pc-text">'+e(s['lead'])+'</p></div>'+steps(s)
    if k=='own':return steps(s)+'<div class="strip">Личные сведения не пишем. Странный или неприятный ответ покажите взрослому</div>'
    if k in ['exit','feedback']:return steps(s)
    return cards(s)
