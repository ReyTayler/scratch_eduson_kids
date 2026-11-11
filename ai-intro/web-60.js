(()=>{'use strict';
const slides=[...document.querySelectorAll('.slide')],panel=document.querySelector('#notesPanel');
const hash=Number.parseInt(location.hash.slice(1),10);
let index=Number.isInteger(hash)&&hash>=1&&hash<=slides.length?hash-1:0,font=19,idle;
function fit(){document.querySelector('#stage').style.transform=`translate(-50%,-50%) scale(${Math.min(innerWidth/1280,innerHeight/720)})`}
function wake(){document.body.classList.add('show-controls');clearTimeout(idle);idle=setTimeout(()=>document.body.classList.remove('show-controls'),1800)}
function render(){
 slides.forEach((s,i)=>{s.hidden=i!==index;s.inert=i!==index;s.classList.toggle('active',i===index);});
 document.querySelectorAll('.speaker').forEach((s,i)=>s.hidden=i!==index);
 document.querySelectorAll('.jump').forEach((b,i)=>b.classList.toggle('current',i===index));
 const counter=document.querySelector('#counter');if(counter)counter.textContent=`${index+1} / ${slides.length}`;
 const prev=document.querySelector('#prev'),next=document.querySelector('#next');
 if(prev)prev.disabled=index===0;if(next)next.disabled=index===slides.length-1;
 if(panel){document.querySelector('#copyPrompt').hidden=lessonData[index].kind!=='prompt';document.querySelector('#showFallback').hidden=!['response','revision'].includes(lessonData[index].kind)}
 try{history.replaceState(null,'',`#${index+1}`)}catch{}
}
function go(n){index=Math.max(0,Math.min(slides.length-1,n));resetInteractive();render();if(panel){document.querySelector('#notesScroll').scrollTop=0;document.querySelector('#copyStatus').textContent=''}}
function toggleNotes(force){if(!panel)return;const show=force??panel.hidden;panel.hidden=!show;document.querySelector('#notesBtn').setAttribute('aria-expanded',String(show));if(show)wake()}
async function full(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen()}catch{}}
function resetInteractive(){
 document.querySelectorAll('.qz-opt').forEach(x=>x.classList.remove('is-ok','is-no'));
 document.querySelectorAll('.qz').forEach(x=>x.classList.remove('done'));
 document.querySelectorAll('.qz-fb').forEach(x=>x.classList.remove('show'));
 document.querySelectorAll('[data-show],[data-hide]').forEach(x=>x.classList.remove('on'));
 document.querySelectorAll('.tap').forEach(x=>x.classList.remove('opened'));
}
/* Интерактив прямо на слайде: нажатие на ответ или на вопрос с меткой «Нажмите». */
document.querySelectorAll('.qz-opt').forEach(b=>b.addEventListener('click',()=>{
 const q=b.closest('.qz');if(q.classList.contains('done')){b.blur();return}q.querySelectorAll('.qz-opt').forEach(x=>x.classList.remove('is-ok','is-no'));
 const ok=b.dataset.ok!==undefined;b.classList.add(ok?'is-ok':'is-no');q.classList.toggle('done',ok);
 const f=q.querySelector('.qz-fb');if(f)f.classList.toggle('show',ok);b.blur();
}));
function tapOpen(t){
 const s=t.closest('.slide'),id=t.dataset.tap;
 s.querySelectorAll(`[data-show="${id}"],[data-hide="${id}"]`).forEach(x=>x.classList.add('on'));t.classList.add('opened');t.blur();
}
document.querySelectorAll('.tap').forEach(t=>{t.addEventListener('click',()=>tapOpen(t));t.addEventListener('keydown',ev=>{if(ev.key==='Enter'){ev.preventDefault();tapOpen(t)}})});
document.addEventListener('pointermove',wake,{passive:true});
/* После нажатия кнопки панели фокус снимается, чтобы клавиши-стрелки сразу работали. */
document.addEventListener('click',ev=>{const b=ev.target.closest('.deck-toolbar button,.deck-controls button');if(b)b.blur()});
document.addEventListener('keydown',ev=>{
 if(ev.target.closest('input,textarea,select')||document.querySelector('dialog[open]'))return;
 const key=ev.key.toLowerCase();
 if(key==='escape'){toggleNotes(false);document.body.classList.remove('show-controls');return}
 if(key==='n'||key==='т'){ev.preventDefault();toggleNotes();return}
 if(key==='f'||key==='а'){ev.preventDefault();full();return}
 if(ev.target.closest('button,a,summary'))return;
 if(['ArrowRight','PageDown'].includes(ev.key)){ev.preventDefault();go(index+1)}
 if(['ArrowLeft','PageUp'].includes(ev.key)){ev.preventDefault();go(index-1)}
 if(ev.key==='Home'){ev.preventDefault();go(0)}
 if(ev.key==='End'){ev.preventDefault();go(slides.length-1)}
});
window.addEventListener('hashchange',()=>{const n=Number.parseInt(location.hash.slice(1),10);if(Number.isInteger(n))go(n-1)});
window.addEventListener('resize',fit);
if(panel){
 document.querySelector('#notesBtn').onclick=()=>toggleNotes();document.querySelector('#closeNotes').onclick=()=>toggleNotes(false);
 document.querySelector('#prev').onclick=()=>go(index-1);document.querySelector('#next').onclick=()=>go(index+1);document.querySelector('#fullBtn').onclick=full;
 const contents=document.querySelector('#contents');document.querySelector('#contentsBtn').onclick=()=>contents.showModal();document.querySelector('#closeContents').onclick=()=>contents.close();document.querySelectorAll('.jump').forEach(b=>b.onclick=()=>{go(+b.dataset.to);contents.close()});
 document.querySelector('#fontUp').onclick=()=>{font=Math.min(28,font+1);document.documentElement.style.setProperty('--notes-size',font+'px')};document.querySelector('#fontDown').onclick=()=>{font=Math.max(16,font-1);document.documentElement.style.setProperty('--notes-size',font+'px')};
 document.querySelector('#copyPrompt').onclick=async()=>{try{await navigator.clipboard.writeText(lessonData[index].lead);document.querySelector('#copyStatus').textContent='Скопировано. Отправьте запрос вручную в подготовленный чат.'}catch{document.querySelector('#copyStatus').textContent='Скопируйте вручную: '+lessonData[index].lead}};
 const fallback=document.querySelector('#fallback');document.querySelector('#showFallback').onclick=()=>fallback.showModal();document.querySelector('#closeFallback').onclick=()=>fallback.close();
}
render();fit();
})();
