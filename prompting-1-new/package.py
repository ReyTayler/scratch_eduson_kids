"""Упаковка презентации и исходников."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
R = Path(__file__).resolve().parent
target = R.parent/'Текстовый промтинг 1 — 60 минут.zip'
names = ['dist/index.html', 'dist/audience.html', 'Сценарий урока.md', 'Сценарий урока.html', 'README.md', 'build.py', 'check.py', 'package.py', 'web.js', 'lesson.css', 'web-60.css', 'designbook-base.css', 'designbook-slides.css', 'designbook-fonts.css', 'designbook-sprite.svg', 'designbook-waves.svg', 'designbook-source.json', 'board.py', 'vendor/drauu-core-1.0.0.mjs', 'vendor/drauu-LICENSE.txt']
with ZipFile(target, 'w', ZIP_DEFLATED) as z:
    for n in names: z.write(R/n, n)
    for f in sorted((R/'svg').glob('*.svg')): z.write(f, f.relative_to(R))
    for f in sorted((R/'font-licenses').glob('*.txt')): z.write(f, f.relative_to(R))
with ZipFile(target) as z:
    assert z.testzip() is None
    print('Архив:', len(z.namelist()), 'файлов,', target.stat().st_size, 'байт')
