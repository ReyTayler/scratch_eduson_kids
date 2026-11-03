"""Vendor the supplied public design book and embed its prescribed fonts."""
import ast, base64, hashlib, json, re, urllib.request
from pathlib import Path
R=Path(__file__).resolve().parent
S=R.parent/'research/designbook-current'
source=(S/'src/lessons/deck_template.py').read_text(encoding='utf-8')
values={}
for node in ast.parse(source).body:
    if isinstance(node,ast.Assign):
        for target in node.targets:
            if isinstance(target,ast.Name) and target.id in ['CSS','SPRITE']:
                values[target.id]=ast.literal_eval(node.value)
(R/'designbook-base.css').write_text(values['CSS'],encoding='utf-8')
(R/'designbook-sprite.svg').write_text(values['SPRITE'],encoding='utf-8')
waves=(S/'src/codex-svg/decor-waves-mint.svg').read_text(encoding='utf-8')
(R/'designbook-waves.svg').write_text(waves[waves.index('<svg'):],encoding='utf-8')
url='https://fonts.googleapis.com/css2?family=Inter+Tight:wght@600..900&family=Inter:wght@400..800&family=JetBrains+Mono:wght@400..700&display=swap'
req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'})
css=urllib.request.urlopen(req,timeout=30).read().decode()
def embedded(m):
    raw=urllib.request.urlopen(m.group(1),timeout=30).read()
    return 'url(data:font/woff2;base64,'+base64.b64encode(raw).decode()+')'
css=re.sub(r'url\((https://[^)]+)\)',embedded,css)
(R/'designbook-fonts.css').write_text(css,encoding='utf-8')
metadata={'repository':'https://github.com/terenta/eduson-kids-design-book','downloaded':'2026-11-03','template':'src/lessons/deck_template.py','template_sha256':hashlib.sha256(source.encode()).hexdigest(),'rules':['src/parts/p02-principles.html','src/parts/p04-type.html','src/parts/p05-layout.html','src/parts/p05d-decor.html','src/parts/p06-components.html','src/parts/p07-slides.html','src/parts/p09-dodont.html','src/lessons/STYLE_GUIDE.md'],'fonts':'Inter Tight / Inter / JetBrains Mono, Google Fonts, embedded WOFF2 including Cyrillic'}
(R/'designbook-source.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
print('Vendored exact template CSS, SVG sprite, waves, and embedded font faces:',css.count('@font-face'))
