"""Проверяет экран урока, заметки и доску в Microsoft Edge."""
import re
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
QA = ROOT / 'qa'
QA.mkdir(exist_ok=True)
N = 24
EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
md = (ROOT / 'Сценарий урока.md').read_text(encoding='utf-8')
idx, aud = ((ROOT / 'dist' / name).read_text(encoding='utf-8') for name in ('index.html', 'audience.html'))
assert not re.search(r'scratch|скретч|герой', md, re.I)
assert len(re.findall(r'^\*\*На экране:\*\*', md, re.M)) == N
assert len(re.findall(r'^\*\*Действие:\*\*', md, re.M)) == N
times = [(int(a), int(b)) for a, b in re.findall(r'^\*\*Время:\*\* (\d+)–(\d+)', md, re.M)]
assert len(times) == N and times[0][0] == 0 and times[-1][1] == 60
assert all(a < b for a, b in times) and all(left[1] == right[0] for left, right in zip(times, times[1:]))
for private in ('class="speaker"', 'id="notesPanel"', 'const lessonData=', 'Дайте детям ответить', 'Запасной учебный ответ'):
    assert private not in aud, private
for html in (idx, aud):
    for obsolete in ('Открыть дальше', 'Показать ответ', 'data-step=', 'id="reveal"', 'Палец вверх'):
        assert obsolete not in html, obsolete

MEASURE = """() => {
    const s = document.querySelector('.slide.active');
    const bounds = s.getBoundingClientRect();
    const bad = [];
    for (const x of s.querySelectorAll('h1,h2,h3,p,li,.fig,.visual,.qz-opt,.strip,.agenda-row,.tap text')) {
        const r = x.getBoundingClientRect();
        if (!r.width || getComputedStyle(x).visibility === 'hidden') continue;
        if (r.bottom > bounds.bottom + 1 || r.right > bounds.right + 1 ||
            r.top < bounds.top - 1 || r.left < bounds.left - 1) bad.push(x.textContent.slice(0,85));
        if (x.matches('.visual') && x.scrollHeight > x.clientHeight + 3) bad.push('visual: ' + x.textContent.slice(0, 75));
    }
    const svgs = [...s.querySelectorAll('.fig > svg')];
    for (const svg of svgs) {
        const [vx,vy,w,h] = svg.viewBox.baseVal
          ? [svg.viewBox.baseVal.x,svg.viewBox.baseVal.y,svg.viewBox.baseVal.width,svg.viewBox.baseVal.height] : [];
        for (const t of svg.querySelectorAll('text')) {
            if (getComputedStyle(t).visibility === 'hidden') continue;
            const m = t.getScreenCTM();
            const font = Number(t.getAttribute('font-size')) * Math.hypot(m.c, m.d);
            if (font < 16.98) bad.push('font ' + font.toFixed(1) + ': ' + t.textContent);
            if (t.parentElement.closest('[transform]')) continue;
            const r = t.getBBox();
            if (r.x < vx - 1 || r.y < vy - 1 || r.x + r.width > vx + w + 1 || r.y + r.height > vy + h + 1)
                bad.push('SVG text: ' + t.textContent);
        }
    }
    return bad;
}"""

ANCHORS = """() => [...document.querySelectorAll('.slide.active h2,.slide.active .fig,.slide.active .qz-q,.slide.active .row-prompt > p:first-child,.slide.active .prompt-card')]
  .map(x => {const r = x.getBoundingClientRect(); return [r.x,r.y,r.width,r.height]})"""


def goto(page, slide):
    page.evaluate('(slide) => location.hash = String(slide)', slide)
    page.locator(f'.slide.active[data-page="{slide}"]').wait_for()


def nearby(before, after, context):
    assert len(before) == len(after) and all(
        abs(a - b) < 1.1 for pair in zip(before, after) for a, b in zip(*pair)
    ), (context, before, after)


def click_tap(page, tap):
    if tap.evaluate("x => x instanceof SVGElement"):
        # Нажатие внутри видимой карточки, в области её метки.
        chip = tap.locator('[data-hide]').last.bounding_box()
        page.mouse.click(chip['x'] + chip['width'] / 2, chip['y'] + chip['height'] / 2)
    else:
        tap.click()


errors = []
layout = []
interactive = set()
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path=EDGE, headless=True)
    for width, height in ((1280, 720), (1920, 1080)):
        context = browser.new_context(viewport={'width': width, 'height': height}, reduced_motion='reduce')
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto((ROOT / 'dist/index.html').as_uri())
        page.evaluate('document.fonts.ready')
        assert page.locator('.slide').count() == N
        assert page.locator('#notesPanel').is_hidden()
        for n in range(1, N + 1):
            goto(page, n)
            slide = page.locator('.slide.active')
            layout.extend((width, n, 'closed', problem) for problem in page.evaluate(MEASURE))
            if width == 1280:
                page.screenshot(path=str(QA / f'slide-{n:02}.png'))
            for quiz in slide.locator('.qz').all():
                right = quiz.locator('.qz-opt[data-ok]')
                wrong = quiz.locator('.qz-opt:not([data-ok])').first
                feedback = quiz.locator('.qz-fb')
                assert right.count() == 1 and feedback.is_hidden()
                assert feedback.evaluate("x => x.getBoundingClientRect().height") == 0
                before = page.evaluate(ANCHORS)
                position = right.bounding_box()
                wrong.click()
                assert 'is-no' in wrong.get_attribute('class') and feedback.is_hidden()
                nearby([[position['x'], position['y'], position['width']]], [[right.bounding_box()[k] for k in ('x', 'y', 'width')]], n)
                right.click()
                assert 'is-ok' in right.get_attribute('class') and feedback.is_visible()
                pressed = right.bounding_box()
                scale = width / 1280
                nearby([[position['x'], position['y'] + 5 * scale, position['width']]], [[pressed[k] for k in ('x', 'y', 'width')]], n)
                wrong.click()
                assert 'is-ok' in right.get_attribute('class') and 'is-no' not in wrong.get_attribute('class')
                after = page.evaluate(ANCHORS)
                if n in (4, 9):
                    # У последующих строк могут измениться координаты, всё выше остаётся на месте.
                    bottom = position['y'] + position['height']
                    anchors = [(a, b) for a, b in zip(before, after) if a[1] < bottom]
                    before, after = zip(*anchors)
                nearby(before, after, n)
            taps = slide.locator('.tap').all()
            for tap in reversed(taps):
                name = tap.get_attribute('data-tap')
                revealed = slide.locator(f'[data-show="{name}"]')
                assert all(item.is_hidden() for item in revealed.all())
                assert 'Нажмите' in tap.text_content()
                position = tap.bounding_box()
                click_tap(page, tap)
                assert 'opened' in tap.get_attribute('class')
                assert all(item.is_visible() for item in revealed.all())
                page.mouse.click(position['x'] + 14, position['y'] + position['height'] / 2)
                assert all(item.is_visible() for item in revealed.all())
                assert abs(tap.bounding_box()['y'] - position['y']) < 1.1
            layout.extend((width, n, 'open', problem) for problem in page.evaluate(MEASURE))
            if width == 1280 and (taps or slide.locator('.qz').count()):
                interactive.add(n)
                page.screenshot(path=str(QA / f'slide-{n:02}-open.png'))

        goto(page, 21)
        click_tap(page, page.locator('.slide.active .tap').first)
        page.keyboard.press('ArrowLeft')
        page.keyboard.press('ArrowRight')
        assert page.locator('.slide.active .opened').count() == 0
        before = page.url
        page.keyboard.press('Space')
        assert page.url == before

        goto(page, 13)
        page.mouse.move(width / 2, 10)
        page.locator('#notesBtn').click()
        assert page.locator('#notesPanel').is_visible()
        assert 'Промт уже в чате урока' in page.locator('.speaker:not([hidden])').inner_text()
        page.locator('#copyPrompt').click()
        page.wait_for_function("document.querySelector('#copyStatus').textContent.length > 0")
        page.keyboard.press('ArrowRight')
        assert page.locator('.slide.active[data-page="14"]').count() == 1
        page.locator('#fontUp').click()
        page.keyboard.press('ArrowRight')
        assert page.locator('.slide.active[data-page="15"]').count() == 1
        page.locator('#showFallback').click()
        assert 'робота синим' in page.locator('.fallback-text').inner_text()
        page.wait_for_function("document.querySelector('.fallback-image').naturalWidth > 0")
        page.screenshot(path=str(QA / f'fallback-{width}.png'))
        page.locator('#closeFallback').click()
        page.keyboard.press('ArrowLeft')
        assert page.locator('.slide.active[data-page="14"]').count() == 1
        page.locator('#closeNotes').click()
        page.keyboard.press('ArrowLeft')
        assert page.locator('.slide.active[data-page="13"]').count() == 1
        page.mouse.move(width / 2, height - 16)
        page.locator('#next').click()
        page.keyboard.press('ArrowRight')
        assert page.locator('.slide.active[data-page="15"]').count() == 1
        for n in (13, 15):
            assert page.evaluate('n => lessonData[n-1].prompt', n) in md

        audience = context.new_page()
        audience.on('pageerror', lambda error: errors.append(str(error)))
        audience.goto((ROOT / 'dist/audience.html').as_uri() + '#4')
        audience.locator('.slide.active .qz-opt[data-ok]').first.click()
        assert audience.locator('.slide.active .is-ok').count() == 1
        audience.keyboard.press('d')
        assert audience.locator('#kb-toggle').get_attribute('aria-pressed') == 'true'
        audience.mouse.move(width * .41, height * .55)
        audience.mouse.down()
        audience.mouse.move(width * .53, height * .59, steps=8)
        audience.mouse.up()
        assert audience.locator('.kb-svg path').count() > 0
        audience.locator('[data-act="undo"]').click()
        assert audience.locator('.kb-svg path').count() == 0
        audience.locator('[data-act="close"]').click()
        audience.keyboard.press('ArrowRight')
        assert audience.locator('.slide.active[data-page="5"]').count() == 1
        context.close()
    browser.close()

assert not errors, errors
assert not layout, '\n'.join(map(str, layout))
thumbs = []
for n in range(1, N + 1):
    path = QA / f'slide-{n:02}-open.png'
    with Image.open(path if n in interactive else QA / f'slide-{n:02}.png') as shot:
        thumbs.append(shot.convert('RGB').resize((384, 216)))
sheet = Image.new('RGB', (1574, 1592), '#e3e2e9')
for i, thumb in enumerate(thumbs):
    sheet.paste(thumb, (10 + i % 4 * 394, 10 + i // 4 * 226))
sheet.save(QA / 'contact-sheet.jpg', quality=90)
print(f'OK: {N} слайдов в Edge при 1280×720 и 1920×1080, переполнения, SVG, нажатия, заметки, экран показа и доска.')
