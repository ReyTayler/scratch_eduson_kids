"""Проверка презентации: все слайды, переполнения, нажатия на слайде, заметки, доска, сверка со сценарием."""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
R = Path(__file__).resolve().parent
Q = R/'qa'; Q.mkdir(exist_ok=True)
md = (R/'Сценарий урока.md').read_text(encoding='utf-8')
idx = (R/'dist/index.html').read_text(encoding='utf-8'); aud = (R/'dist/audience.html').read_text(encoding='utf-8')
assert not re.search(r'scratch|скретч|мой герой', md, re.I)
assert 'class="speaker"' not in aud, 'В audience.html попала речь'
for h in (idx, aud):
    assert 'Открыть дальше' not in h and 'data-step' not in h and 'id="reveal"' not in h, 'Осталась механика шагов'
assert 'Палец вверх' not in idx
N = 26
EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
MEASURE = '''()=>{const s=document.querySelector('.slide:not([hidden])');const bad=[];
  const stage=document.querySelector('#stage').getBoundingClientRect();
  for(const x of s.querySelectorAll('h1,h2,h3,p,li,.visual,.info-card,.lesson-question,.lead,.strip,.sl-body,.hints,.fig,.prompt-card,.ek-note,.agenda-row,.qz-row,.qz-opt')){
    const r=x.getBoundingClientRect();if(!r.width)continue;
    if(r.bottom>stage.bottom+.5||r.right>stage.right+.5||r.top<stage.top-.5)bad.push('OUT '+x.className+':'+x.textContent.slice(0,50));
    if(x.scrollHeight>x.clientHeight+3&&(['hidden','clip'].includes(getComputedStyle(x).overflow)||x.classList.contains('visual')))bad.push('CLIP '+x.className+':'+x.textContent.slice(0,50));
  }
  const v=s.querySelector('.sl-body');if(v){const vb=v.getBoundingClientRect();const kids=[...v.children];const last=kids[kids.length-1].getBoundingClientRect();if(last.bottom>vb.bottom+1)bad.push('BODY overflow by '+Math.round(last.bottom-vb.bottom))}
  const fig=[...s.querySelectorAll('.fig>svg')].map(v=>{const r=v.getBoundingClientRect();const k=stage.width/1280;const [,,w,h]=v.getAttribute('viewBox').split(' ').map(Number);const sc=Math.min(r.width/w,r.height/h)/k;const min=Math.min(...[...v.querySelectorAll('text')].map(t=>+t.getAttribute('font-size')));return Math.round(sc*min*10)/10});
  return {bad,fig}}'''
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True)
    ctx = b.new_context(viewport={'width': 1600, 'height': 900}, reduced_motion='reduce')
    pg = ctx.new_page(); errors = []
    pg.on('pageerror', lambda x: errors.append(str(x)))
    pg.goto((R/'dist/index.html').as_uri()); pg.evaluate('document.fonts.ready')
    assert pg.locator('.slide').count() == N and pg.locator('#notesPanel').is_hidden()
    bad_all = []; used = {}
    for i in range(N):
        pg.evaluate('(i)=>location.hash=String(i+1)', i)
        pg.wait_for_function('(i)=>!document.querySelectorAll(".slide")[i].hidden', arg=i)
        pg.screenshot(path=str(Q/f'slide-{i+1:02}.png'))
        cur = pg.locator('.slide:not([hidden])')
        opts, taps = cur.locator('.qz-opt').count(), cur.locator('.tap').count()
        used[i+1] = (opts, taps)
        # неверный вариант красный, верный зелёный, пояснение только после верного
        for qi in range(cur.locator('.qz').count()):
            q = cur.locator('.qz').nth(qi)
            wrong = q.locator('.qz-opt:not([data-ok])').first; right = q.locator('.qz-opt[data-ok]').first
            assert q.locator('.qz-opt[data-ok]').count() == 1, f'слайд {i+1}: нет верного варианта'
            x0 = right.bounding_box()['x']; w0 = right.bounding_box()['width']
            wrong.click(); assert 'is-no' in wrong.get_attribute('class')
            assert abs(right.bounding_box()['x']-x0) < 1 and abs(right.bounding_box()['width']-w0) < 1, f'слайд {i+1}: кнопка сдвинулась'
            if q.locator('.qz-fb').count(): assert q.locator('.qz-fb').is_hidden()
            right.click(); assert 'is-ok' in right.get_attribute('class') and 'is-no' not in wrong.get_attribute('class')
            if q.locator('.qz-fb').count(): assert q.locator('.qz-fb').is_visible()
        # нажатие на элемент показывает скрытое
        hid = pg.evaluate("()=>[...document.querySelectorAll('.slide:not([hidden]) [data-show]')].every(x=>getComputedStyle(x).visibility==='hidden')")
        assert hid, f'слайд {i+1}: скрытое видно сразу'
        # у каждого раскрытия видна метка «Нажмите», после нажатия она исчезает
        if taps:
            assert pg.evaluate("()=>[...document.querySelectorAll('.slide:not([hidden]) .tap')].every(t=>t.textContent.includes('Нажмите'))"), f'слайд {i+1}: нет метки'
        for ti in range(taps):
            cur.locator('.tap').nth(ti).click(force=True)
        # повторное нажатие ничего не скрывает
        for ti in range(taps):
            cur.locator('.tap').nth(ti).click(force=True)
        if taps:
            assert pg.evaluate("()=>[...document.querySelectorAll('.slide:not([hidden]) [data-hide]')].every(x=>getComputedStyle(x).visibility==='hidden')"), f'слайд {i+1}: метка осталась'
        ok = pg.evaluate("()=>[...document.querySelectorAll('.slide:not([hidden]) [data-show]')].every(x=>getComputedStyle(x).visibility==='visible')")
        assert ok, f'слайд {i+1}: нажатие не сработало'
        if opts or taps: pg.screenshot(path=str(Q/f'slide-{i+1:02}-open.png'))
        m = pg.evaluate(MEASURE)
        if m['bad']: bad_all.append((i+1, m['bad']))
        if m['fig'] and min(m['fig']) < 17: bad_all.append((i+1, ['MINFONT %s' % m['fig']]))
    # нажатие по краю строки на слайде 23 тоже работает
    pg.evaluate('location.hash="1"'); pg.wait_for_function('!document.querySelectorAll(".slide")[0].hidden')
    pg.evaluate('location.hash="23"'); pg.wait_for_function('!document.querySelectorAll(".slide")[22].hidden')
    li = pg.locator('.slide:not([hidden]) li.tap').first; box = li.bounding_box()
    pg.mouse.click(box['x']+box['width']-6, box['y']+box['height']/2)
    assert pg.locator('.slide:not([hidden]) li.tap.opened').count() == 1, 'край строки не нажимается'
    # нажатия сбрасываются при перелистывании, стрелки работают сразу после нажатия
    pg.evaluate('location.hash="1"'); pg.wait_for_function('!document.querySelectorAll(".slide")[0].hidden')
    pg.evaluate('location.hash="4"'); pg.wait_for_function('!document.querySelectorAll(".slide")[3].hidden')
    assert pg.locator('.slide:not([hidden]) .is-ok').count() == 0, 'нажатия не сброшены'
    pg.locator('.slide:not([hidden]) .qz-opt').first.click()
    pg.keyboard.press('ArrowRight'); pg.wait_for_function('!document.querySelectorAll(".slide")[4].hidden')
    pg.keyboard.press('ArrowLeft'); pg.wait_for_function('!document.querySelectorAll(".slide")[3].hidden')
    # пробел ничего не делает
    before = pg.evaluate('location.hash'); pg.keyboard.press('Space'); assert pg.evaluate('location.hash') == before
    # заметки, копирование, запасной ответ
    pg.evaluate('location.hash="15"'); pg.wait_for_function('!document.querySelectorAll(".slide")[14].hidden')
    pg.keyboard.press('n'); assert pg.locator('#notesPanel').is_visible()
    assert 'Начните новый чат' in pg.locator('.speaker:not([hidden])').inner_text()
    assert pg.locator('#copyPrompt').is_visible() and pg.locator('#showFallback').is_visible()
    pg.screenshot(path=str(Q/'notes.png'))
    pg.locator('#showFallback').click(); assert 'робот Болт' in pg.locator('#fallback').inner_text(); pg.locator('#closeFallback').click()
    pg.keyboard.press('Escape'); assert pg.locator('#notesPanel').is_hidden()
    data = pg.evaluate('lessonData')
    for n in (15, 18):
        assert data[n-1]['prompt'] and data[n-1]['prompt'] in md
    pg.keyboard.press('d'); assert pg.locator('#kb-toggle').get_attribute('aria-pressed') == 'true'; pg.keyboard.press('d')
    assert not errors, errors
    # версия для показа: нажатия тоже работают
    pg2 = ctx.new_page(); pg2.goto((R/'dist/audience.html').as_uri()+'#4')
    pg2.locator('.slide:not([hidden]) .qz-opt[data-ok]').first.click()
    assert pg2.locator('.slide:not([hidden]) .is-ok').count() == 1
    b.close()
print('интерактив (варианты, нажатия):', {k: v for k, v in used.items() if v != (0, 0)})
print('PROBLEMS' if bad_all else 'OK: переполнений нет')
for x in bad_all: print(x)
ims = []
for i in range(1, N+1):
    f = Q/f'slide-{i:02}-open.png'
    ims.append(Image.open(f if f.exists() else Q/f'slide-{i:02}.png').convert('RGB').resize((480, 270)))
W = 4; H = (N+W-1)//W; sheet = Image.new('RGB', (W*490+10, H*280+10), '#ddd')
for i, im in enumerate(ims): sheet.paste(im, (10+(i % W)*490, 10+(i//W)*280))
sheet.save(Q/'contact-sheet.jpg', quality=88)
