"""Package the current web presentation and its editable sources."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
R=Path(__file__).resolve().parent
target=R.parent/'Введение в нейросети — 60 минут.zip'
files=['dist/index.html','dist/audience.html','Текст урока.md',
 'lesson-60.json','author-60.py','build-60.py','slide-art-60.py','README.md','web-60.css','web-60.js',
 'designbook-base.css','designbook-slides.css','designbook-fonts.css',
 'board.py','vendor/drauu-core-1.0.0.mjs','vendor/drauu-LICENSE.txt','designbook-sprite.svg','designbook-waves.svg','designbook-source.json','package-60.py','check-60.py']
with ZipFile(target,'w',ZIP_DEFLATED) as z:
    for name in files: z.write(R/name,name)
    for path in sorted((R/'font-licenses').glob('*.txt')):z.write(path,path.relative_to(R))
    z.writestr('Как открыть.txt','Введение в нейросети. 7–9 лет. 60 минут.\n\n1. Распакуйте архив целиком.\n2. Откройте dist/index.html в Edge или Chrome.\n3. На экране сразу слайды. Кнопки появляются при движении мыши.\n4. Заметки открываются кнопкой «Преподавателю» или клавишей N. Закрытие: N или Escape.\n5. Полный сценарий: Текст урока.md.\n\nКлавиши влево/вправо: слайды. Пробел: ответ. Home: начало. F: весь экран.\nПрактику каждый ребёнок или пара выполняет сам в Алисе AI.\n\nДизайн: https://github.com/terenta/eduson-kids-design-book\nБазовый CSS и SVG перенесены из дизайнбука. Шрифты встроены и работают без интернета.\n\nПересборка: python author-60.py, затем python build-60.py.\n')
with ZipFile(target) as z:
    assert z.testzip() is None
    print('Verified package:',len(z.namelist()),'files,',target.stat().st_size,'bytes')
