"""Доска поверх слайда: панель инструментов на drauu (MIT, Anthony Fu).

Перенесено из проекта «Роблокс котокод» (Kotokod_v3_preview/board_v3.py) и адаптировано
под презентации Eduson Kids: сцена 1280×720, активный слайд .slide.active, без лайтбокса и лупы.

inject(html, stage) -> html: вшивает библиотеку, панель и кнопку «Доска». Работает без интернета.
Панель скрыта, пока её не откроют кнопкой или клавишей D. Рисунки на слайде стираются при
перелистывании; «чистый лист» один на всю презентацию и хранится только в памяти вкладки.
"""
from pathlib import Path

VENDOR = Path(__file__).resolve().parent / 'vendor'


def _drauu_iife():
    src = (VENDOR / 'drauu-core-1.0.0.mjs').read_text(encoding='utf8')
    export_line = 'export { Drauu, DrawModel, EllipseModel, EraserModel, LineModel, RectModel, StylusModel, createDrauu };'
    assert export_line in src, 'drauu: неожиданный формат сборки'
    src = src.replace(export_line, 'window.Drauu = { createDrauu: createDrauu, Drauu: Drauu };')
    lic = (VENDOR / 'drauu-LICENSE.txt').read_text(encoding='utf8').strip().replace('*/', '* /')
    return f'/*! drauu 1.0.0 (@drauu/core) · https://github.com/antfu/drauu\n{lic}\n*/\n;(function(){{\n{src}\n}})();'


ICON = {
    'board':  '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>',
    'pen':    '<path d="M4 20h4L19 9l-4-4L4 16z"/>',
    'marker': '<path d="M9 15l-4 4v1h5l4-4"/><path d="M8 12l6-9 7 7-9 6z"/>',
    'arrow':  '<path d="M5 19L19 5"/><path d="M10 5h9v9"/>',
    'rect':   '<rect x="4" y="6" width="16" height="12" rx="3"/>',
    'laser':  '<circle cx="12" cy="12" r="3.5" fill="currentColor"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
    'eraser': '<path d="M16 3l5 5-10 10H6l-3-3z"/><path d="M9 21h12"/>',
    'undo':   '<path d="M9 14L4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-3"/>',
    'redo':   '<path d="M15 14l5-5-5-5"/><path d="M20 9H10a6 6 0 0 0 0 12h3"/>',
    'sheet':  '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4"/>',
    'clear':  '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
    'close':  '<path d="M6 6l12 12M18 6L6 18"/>',
}


def _ico(name):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[name]}</svg>')


# Цвета дизайнбука Eduson Kids: красный, зелёный, фиолетовый и чернила. Жёлтый добавлен для контраста на белом и фиолетовом.
COLORS = [('#E04848', 'Красный'), ('#FFC53D', 'Жёлтый'), ('#0FBF6E', 'Зелёный'), ('#6F61E8', 'Фиолетовый'), ('#17171C', 'Тёмный')]

TOOLS = [('pen', 'Ручка'), ('marker', 'Маркер'), ('arrow', 'Стрелка'), ('rect', 'Рамка'), ('laser', 'Указка'), ('eraser', 'Ластик')]


def _bar():
    tools = ''.join(f'<button type="button" class="kb-btn" data-tool="{k}" aria-pressed="false" title="{t}" aria-label="{t}">{_ico(k)}</button>' for k, t in TOOLS)
    sw = ''.join(f'<button type="button" class="kb-sw" data-color="{c}" style="--sw:{c}" aria-pressed="false" title="{n}" aria-label="Цвет: {n}"></button>' for c, n in COLORS)
    acts = (f'<button type="button" class="kb-btn" data-act="undo" title="Отменить (Ctrl+Z)" aria-label="Отменить">{_ico("undo")}</button>'
            f'<button type="button" class="kb-btn" data-act="redo" title="Вернуть (Ctrl+Shift+Z)" aria-label="Вернуть">{_ico("redo")}</button>'
            f'<button type="button" class="kb-btn" data-act="sheet" aria-pressed="false" title="Чистый лист: один на всю презентацию" aria-label="Чистый лист">{_ico("sheet")}</button>'
            f'<button type="button" class="kb-btn" data-act="clear" title="Стереть всё на этом слайде" aria-label="Стереть всё на этом слайде">{_ico("clear")}</button>'
            f'<button type="button" class="kb-btn" data-act="close" title="Закрыть доску (D или Esc)" aria-label="Закрыть доску">{_ico("close")}</button>')
    return (f'<div class="kb-bar" id="kb-bar" role="toolbar" aria-label="Доска" hidden>'
            f'<div class="kb-group">{tools}</div><div class="kb-group kb-colors">{sw}</div><div class="kb-group">{acts}</div></div>')


CSS = r'''
/* ================= Доска (drauu) ================= */
.kb-svg{position:absolute;left:0;top:0;width:100%;height:100%;z-index:40;pointer-events:none;overflow:visible}
.kb-svg[hidden]{display:none}
#kb-sheet{position:absolute;inset:0;z-index:39;background:#fff}
#kb-sheet[hidden]{display:none}
.kb-on .kb-svg{pointer-events:auto;cursor:crosshair;touch-action:none}
.kb-on.kb-t-eraser .kb-svg{cursor:cell}
.kb-on.kb-t-laser .kb-svg{pointer-events:none}
.kb-on.kb-t-laser,.kb-on.kb-t-laser *{cursor:none}
.kb-on.kb-t-laser .slide.active{pointer-events:none}
#kb-laser{position:absolute;left:0;top:0;width:24px;height:24px;margin:-12px 0 0 -12px;border-radius:50%;z-index:41;pointer-events:none;
  background:radial-gradient(circle,#fff 0 18%,#FF3B3B 20% 60%,rgba(255,59,59,.35) 62% 100%);box-shadow:0 0 16px 6px rgba(255,59,59,.45)}
#kb-laser[hidden]{display:none}
.kb-bar{position:fixed;left:50%;bottom:64px;transform:translateX(-50%);z-index:60;display:flex;gap:6px;align-items:center;flex-wrap:wrap;justify-content:center;max-width:96vw;
  background:#fff;border:2px solid #E3E3EA;border-radius:16px;box-shadow:0 10px 30px rgba(23,23,28,.18);padding:4px 6px}
.kb-bar[hidden]{display:none}
.kb-group{display:flex;gap:2px;align-items:center}
.kb-group+.kb-group{padding-left:6px;border-left:2px solid #E3E3EA}
button.kb-btn{display:flex;align-items:center;justify-content:center;width:36px;height:36px;padding:8px;border:0;border-radius:10px;background:transparent;color:#17171C;cursor:pointer}
.kb-btn svg{width:20px;height:20px;display:block}
button.kb-btn:hover{background:#F0EEFE}
button.kb-btn[aria-pressed="true"]{background:#8C7FF6;color:#fff}
button.kb-btn:disabled{opacity:.3;cursor:default;background:transparent}
.kb-colors{gap:6px;padding-right:2px}
button.kb-sw{width:22px;height:22px;border:0;padding:0;cursor:pointer;background:var(--sw);border-radius:50%}
button.kb-sw:hover{background:var(--sw)}
button.kb-sw[aria-pressed="true"]{outline:2px solid #17171C;outline-offset:2px}
#kb-toggle{display:inline-flex;align-items:center;gap:6px}
#kb-toggle svg{width:16px;height:16px;display:block}
#kb-toggle[aria-pressed="true"]{background:#8C7FF6;border-color:#8C7FF6;color:#fff}
#kb-toggle.kb-float{position:fixed;top:10px;right:12px;z-index:20;opacity:0;pointer-events:none;transition:opacity .15s}
.show-controls #kb-toggle.kb-float,body.kb-active #kb-toggle.kb-float,#kb-toggle.kb-float:focus-visible{opacity:1;pointer-events:auto}
@media print{.kb-bar,#kb-toggle,#kb-laser{display:none!important}}
'''

JS = r'''
/* ============ Доска: drauu поверх активного слайда ============ */
(function(){
  if(!window.Drauu)return;
  var W=1280,H=720,NS='http://www.w3.org/2000/svg';
  var stage=document.querySelector(document.currentScript.dataset.stage),bar=document.getElementById('kb-bar'),tog=document.getElementById('kb-toggle');
  var slides=[].slice.call(document.querySelectorAll('.slide'));
  var sheet=document.createElement('div'),laser=document.createElement('div');
  sheet.id='kb-sheet';sheet.hidden=true;laser.id='kb-laser';laser.hidden=true;
  stage.appendChild(sheet);stage.appendChild(laser);
  var TOOLS={
    pen:   function(c){return {mode:'stylus',color:c,size:6}},
    marker:function(c){return {mode:'draw',color:c+'66',size:26}},
    arrow: function(c){return {mode:'line',color:c,size:6,arrowEnd:true}},
    rect:  function(c){return {mode:'rectangle',color:c,size:5,cornerRadius:11}},
    eraser:function(c){return {mode:'eraseLine',color:c,size:6}}
  };
  /* слои: слайд (стирается при перелистывании) и «лист» (один на презентацию) */
  var layers={},L=null,d=null,active=false,tool='pen',color='#E04848',shown=-1;
  function idx(){for(var i=0;i<slides.length;i++)if(slides[i].classList.contains('active'))return i;return 0;}
  function key(){return sheet.hidden?String(idx()):'sheet';}
  function brush(){return TOOLS[tool==='laser'?'pen':tool](color);}
  function layer(k){
    if(!layers[k]){
      var s=document.createElementNS(NS,'svg');
      s.setAttribute('class','kb-svg');s.setAttribute('viewBox','0 0 '+W+' '+H);s.setAttribute('preserveAspectRatio','none');
      s.setAttribute('aria-label','Рисунки');s.setAttribute('hidden','');
      stage.insertBefore(s,laser);
      var inst=Drauu.createDrauu({el:s,brush:brush()});
      inst.on('changed',sync);inst.on('committed',sync);
      layers[k]={k:k,svg:s,d:inst};
    }
    return layers[k];
  }
  function drop(k){var x=layers[k];if(!x)return;x.d.unmount();x.svg.remove();delete layers[k];}
  function restore(){
    var k=key();
    for(var x in layers){if(x===k)layers[x].svg.removeAttribute('hidden');else layers[x].svg.setAttribute('hidden','');}
    L=layer(k);L.svg.removeAttribute('hidden');d=L.d;
    var br=brush();d.mode=br.mode;d.brush=br;sync();
  }
  function sync(){
    if(!d)return;
    bar.querySelector('[data-act="undo"]').disabled=!d.canUndo();
    bar.querySelector('[data-act="redo"]').disabled=!d.canRedo();
    bar.querySelector('[data-act="sheet"]').setAttribute('aria-pressed',String(!sheet.hidden));
  }
  function applyClasses(){
    stage.className=stage.className.replace(/\bkb-t-\w+/g,'').replace(/\bkb-on\b/g,'').replace(/\s+/g,' ').trim();
    if(active)stage.classList.add('kb-on','kb-t-'+tool);
  }
  function setTool(t){
    tool=t;
    [].forEach.call(bar.querySelectorAll('[data-tool]'),function(b){b.setAttribute('aria-pressed',String(b.dataset.tool===t));});
    applyClasses();
    if(t!=='laser'&&d){var b=TOOLS[t](color);d.mode=b.mode;d.brush=b;laser.hidden=true;}
  }
  function setColor(c){
    color=c;
    [].forEach.call(bar.querySelectorAll('[data-color]'),function(b){b.setAttribute('aria-pressed',String(b.dataset.color===c));});
    if(tool==='laser'||tool==='eraser')setTool('pen');else setTool(tool);
  }
  function setActive(v){
    active=v;document.body.classList.toggle('kb-active',v);applyClasses();
    bar.hidden=!v;tog.setAttribute('aria-pressed',String(v));
    if(!v){laser.hidden=true;if(!sheet.hidden){sheet.hidden=true;restore();}}
  }
  /* сцена масштабируется целиком: координаты считаем по её положению на экране */
  function fixScale(){if(!d)return;var r=d.el.getBoundingClientRect();if(!r.width)return;
    d.options.coordinateTransform=false;d.options.cssZoom=1;d.options.coordinateScale=W/r.width;}
  document.addEventListener('pointerdown',fixScale,true);
  /* смена слайда: рисунки прошлого слайда стираются, лист закрывается */
  function onSlide(){var i=idx();if(i===shown)return;shown=i;
    for(var x in layers)if(x!=='sheet')drop(x);
    sheet.hidden=true;restore();}
  var mo=new MutationObserver(onSlide);
  slides.forEach(function(s){mo.observe(s,{attributes:true,attributeFilter:['class']});});
  tog.addEventListener('click',function(){setActive(!active);tog.blur();});
  bar.addEventListener('click',function(e){
    var b=e.target.closest('button');if(!b)return;
    if(b.dataset.tool)setTool(b.dataset.tool);
    else if(b.dataset.color)setColor(b.dataset.color);
    else if(b.dataset.act==='undo'){d.undo();sync();}
    else if(b.dataset.act==='redo'){d.redo();sync();}
    else if(b.dataset.act==='clear'){d.clear();sync();}
    else if(b.dataset.act==='sheet'){sheet.hidden=!sheet.hidden;restore();}
    else if(b.dataset.act==='close')setActive(false);
    b.blur();
  });
  /* указка: точка в координатах сцены */
  document.addEventListener('pointermove',function(e){
    if(!active||tool!=='laser')return;
    var r=stage.getBoundingClientRect(),z=r.width/W;
    var x=(e.clientX-r.left)/z,y=(e.clientY-r.top)/z;
    if(x<0||y<0||x>W||y>H){laser.hidden=true;return;}
    laser.style.transform='translate('+x+'px,'+y+'px)';laser.hidden=false;
  });
  /* клавиши: D — доска, Esc — закрыть только доску, Ctrl+Z / Ctrl+Shift+Z / Ctrl+Y */
  document.addEventListener('keydown',function(e){
    var t=e.target;if(t&&(t.isContentEditable||/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)))return;
    if(document.querySelector('dialog[open]'))return;
    if(e.code==='KeyD'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&!e.repeat){e.preventDefault();setActive(!active);return;}
    if(!active)return;
    if(e.key==='Escape'||e.key==='Esc'){setActive(false);e.stopImmediatePropagation();return;}
    if((e.ctrlKey||e.metaKey)&&e.code==='KeyZ'){e.preventDefault();if(e.shiftKey)d.redo();else d.undo();sync();}
    else if((e.ctrlKey||e.metaKey)&&e.code==='KeyY'){e.preventDefault();d.redo();sync();}
  },true);
  shown=idx();restore();setColor(color);setTool('pen');
})();
'''


def inject(html, stage):
    """stage — CSS-селектор сцены: '#stage' в уроке 1, '#deck' в уроках 2–3."""
    toggle = f'<button id="kb-toggle" type="button" aria-pressed="false" title="Доска (D)">{_ico("board")}Доска</button>'
    anchor = '<button id="fullBtn"'
    if html.count(anchor) == 1:
        html = html.replace(anchor, toggle + anchor)
    else:
        toggle = toggle.replace('id="kb-toggle"', 'id="kb-toggle" class="kb-float"')
        before, sep, after = html.rpartition('</body>')
        html = before + toggle + sep + after
    # rpartition: в тексте скриптов могут встречаться те же подстроки раньше закрывающего тега
    before, sep, after = html.rpartition('</body>')
    assert sep, 'В документе нет </body>'
    html = (before + _bar() + f'\n<script>{_drauu_iife()}</script>\n<script data-stage="{stage}">{JS}</script>\n' + sep + after)
    assert html.count('</head>') >= 1
    return html.replace('</head>', f'<style>{CSS}</style>\n</head>', 1)
