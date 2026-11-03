"""Check the standalone slide deck, opt-in speaker notes and the drawing board."""
import json,re
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
Q=R/'qa-60';Q.mkdir(exist_ok=True)
lesson=json.loads((R/'lesson-60.json').read_text(encoding='utf-8'))
assert sum(s['minutes'] for s in lesson['slides'])==60
# Results mirror the goals one to one: same topics, same number of actions.
goals,results=lesson['slides'][2]['cards'],lesson['slides'][21]['cards']
assert results[0][1]==goals[0][1] and len(results[1][1].split('; '))==len(goals[1][1].split('; '))
# Practice teaches first steps in the chat: no hero card and no paper notes.
assert not re.search(r'геро|карандаш|линз|обсерват|Реми',json.dumps(lesson['slides'][:22],ensure_ascii=False))
assert not re.search(r'scratch|скретч|стрелк|толщин|почерк|берег|мусор|бутыл|\bбум\b|уже знаем|мой герой|quick|draw',json.dumps(lesson,ensure_ascii=False),re.I)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless=True)
    context=browser.new_context(viewport={'width':1600,'height':900},accept_downloads=True,reduced_motion='reduce')
    page=context.new_page()
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto((R/'dist/index.html').as_uri())
    page.evaluate('document.fonts.ready')
    assert page.locator('#notesPanel').is_hidden()
    assert page.locator('iframe').count()==0
    assert page.locator('#stage img').count()==0
    assert page.locator('.presenter-grid,.preview-column,.next-card,.timer-row').count()==0
    assert page.locator('.slide').count()==24
    assert page.evaluate("getComputedStyle(document.querySelector('.deck-toolbar')).opacity==='0'")
    violations=[]
    for i in range(24):
        page.evaluate('(i)=>location.hash=String(i+1)',i)
        page.wait_for_function('(i)=>!document.querySelectorAll(".slide")[i].hidden',arg=i)
        page.screenshot(path=str(Q/f'slide-{i+1:02}.png'))
        bad=page.evaluate('''()=>{const s=document.querySelector('.slide:not([hidden])');const els=[...s.querySelectorAll('h1,h2,h3,p,.visual,.info-card,.lesson-question,.lead,.strip,blockquote,.sl-body')];return els.filter(x=>{const r=x.getBoundingClientRect();return r.bottom>900.5||r.right>1600.5||r.top<-.5||x.scrollHeight>x.clientHeight+3&&['hidden','clip'].includes(getComputedStyle(x).overflow)||x.classList.contains('visual')&&x.scrollHeight>x.clientHeight+3}).map(x=>x.className+':'+x.textContent.slice(0,70))}''')
        if bad:violations.append([i+1,bad])
        if lesson['slides'][i]['answer']:
            page.keyboard.press('Space')
            page.locator(f'.slide[data-index="{i}"] .answer').wait_for(state='visible')
            page.keyboard.press('Space')
    # Homework follows the design book: label and three cards.
    page.evaluate('location.hash="23"')
    page.wait_for_function('!document.querySelectorAll(".slide")[22].hidden')
    home=page.locator('.slide:not([hidden])')
    assert 'Домашнее задание' in home.locator('.q-label').text_content()
    assert home.locator('.grid-3 .info-card').count()==3
    page.keyboard.press('Home')
    page.wait_for_function("location.hash==='#1'")
    # Mouse exposes small controls. Speaker notes remain opt-in.
    page.mouse.move(1540,30)
    page.locator('#notesBtn').click()
    assert page.locator('#notesPanel').is_visible()
    assert page.locator('#notesBtn').get_attribute('aria-expanded')=='true'
    assert 'цифр' in page.locator('.speaker:not([hidden])').inner_text()
    page.screenshot(path=str(Q/'speaker-notes.png'))
    page.locator('#fontUp').click()
    assert page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--notes-size').trim()")=='20px'
    page.keyboard.press('Escape')
    assert page.locator('#notesPanel').is_hidden()
    page.keyboard.press('n')
    assert page.locator('#notesPanel').is_visible()
    page.locator('#contentsBtn').click()
    page.locator('.jump[data-to="15"]').click()
    assert 'Расскажи про' in page.locator('.slide:not([hidden])').inner_text()
    page.locator('#closeNotes').click()
    assert page.locator('#notesPanel').is_hidden()
    assert page.locator('.slide:not([hidden])').get_attribute('data-index')=='15'
    # Notes stay closed after reload and do not change the slide dimensions.
    page.reload()
    assert page.locator('#notesPanel').is_hidden()
    assert page.evaluate("document.querySelector('#stage').offsetWidth===1280&&document.querySelector('#stage').offsetHeight===720")
    assert page.evaluate("[...document.fonts].some(f=>f.family==='Inter Tight'&&f.status==='loaded')")
    page.set_viewport_size({'width':700,'height':900})
    page.wait_for_timeout(300)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.keyboard.press('n')
    page.screenshot(path=str(Q/'notes-narrow.png'))
    assert page.locator('#notesPanel').bounding_box()['width']<=700
    public=context.new_page()
    public.goto((R/'dist/audience.html').as_uri())
    assert public.locator('.speaker,#notesPanel,.deck-toolbar').count()==0
    assert 'Здравствуйте! Проверьте' not in public.content()
    assert not re.search('scratch|скретч',page.locator('#stage').inner_text(),re.I)
    assert page.locator('a[href*="worksheet"]').count()==0
    # Доска: панель скрыта, открывается по D, рисует, отменяет, стирается при смене слайда.
    for target in (public,context.new_page()):
        if target is not public:target.goto((R/'dist/index.html').as_uri())
        target.keyboard.press('Home')
        assert target.locator('#kb-bar').is_hidden()
        target.keyboard.press('d')
        assert target.locator('#kb-bar').is_visible()
        box=target.locator('.stage').bounding_box()
        def stroke(dx=0):
            target.mouse.move(box['x']+box['width']*.3+dx,box['y']+box['height']*.4)
            target.mouse.down()
            for step in range(1,9):target.mouse.move(box['x']+box['width']*(.3+step*.03)+dx,box['y']+box['height']*(.4+step*.01))
            target.mouse.up()
            target.wait_for_timeout(250)
        drawn="document.querySelectorAll('.kb-svg:not([hidden]) path,.kb-svg:not([hidden]) line,.kb-svg:not([hidden]) rect').length"
        stroke()
        assert target.evaluate(drawn)>0
        target.keyboard.press('Control+z')
        target.wait_for_timeout(100)
        assert target.evaluate(drawn)==0
        target.keyboard.press('Control+Shift+z')
        target.wait_for_timeout(100)
        assert target.evaluate(drawn)>0
        # Рисунок попадает в точку под курсором и на масштабированной сцене.
        got=target.evaluate("(()=>{const r=document.querySelector('.kb-svg:not([hidden])').getBBox();return [r.x,r.y]})()")
        assert abs(got[0]-1280*.3)<40 and abs(got[1]-720*.4)<40,got
        target.keyboard.press('ArrowRight')
        target.wait_for_timeout(150)
        assert target.evaluate(drawn)==0
        target.locator('[data-tool="arrow"]').click()
        target.locator('[data-color="#0FBF6E"]').click()
        stroke()
        assert target.evaluate(drawn)>0
        target.locator('[data-act="sheet"]').click()
        assert target.locator('#kb-sheet').is_visible()
        target.locator('[data-tool="laser"]').click()
        target.mouse.move(box['x']+200,box['y']+200)
        assert target.locator('#kb-laser').is_visible()
        target.keyboard.press('Escape')
        assert target.locator('#kb-bar').is_hidden() and target.locator('#kb-sheet').is_hidden() and target.locator('#kb-laser').is_hidden()
    assert not errors,errors
    assert not violations,violations
    assert not errors,errors
    (Q/'checks.json').write_text(json.dumps({'slides':24,'minutes':60,'overflow':violations,'page_errors':errors,'checks':['slide-only default','no sidebar or iframe','opt-in notes button','N and Escape','content menu','note size','closed notes after reload','1280x720 stage','embedded fonts','narrow notes','separate public file without notes','no Scratch or arrow teaching examples','board: D, draw, undo, redo, clear on slide change, sheet, laser, Escape']},ensure_ascii=False,indent=2),encoding='utf-8')
    browser.close()
thumbs=[]
for i in range(1,25):
    im=Image.open(Q/f'slide-{i:02}.png').convert('RGB');im.thumbnail((400,225))
    tile=Image.new('RGB',(420,260),'#e9e9ef');tile.paste(im,(10,10));ImageDraw.Draw(tile).text((12,237),str(i),fill='#17171c');thumbs.append(tile)
contact=Image.new('RGB',(1680,1560),'#e9e9ef')
for i,tile in enumerate(thumbs):contact.paste(tile,((i%4)*420,(i//4)*260))
contact.save(Q/'contact-sheet.jpg')
print('Passed: 24 slides, independent content, handwritten digits case, slide-only interface and optional notes.')
