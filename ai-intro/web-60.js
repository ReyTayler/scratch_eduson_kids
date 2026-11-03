(()=>{'use strict';
const slides=[...document.querySelectorAll('.slide')],panel=document.querySelector('#notesPanel');
const hash=Number.parseInt(location.hash.slice(1),10);
let index=Number.isInteger(hash)&&hash>=1&&hash<=slides.length?hash-1:0,revealed=false,font=19,idle;
function fit(){document.querySelector('#stage').style.transform=`translate(-50%,-50%) scale(${Math.min(innerWidth/1280,innerHeight/720)})`}
function wake(){document.body.classList.add('show-controls');clearTimeout(idle);idle=setTimeout(()=>document.body.classList.remove('show-controls'),1800)}
function render(){
 slides.forEach((s,i)=>{s.hidden=i!==index;s.inert=i!==index;s.classList.toggle('active',i===index);const answer=s.querySelector('.answer');if(answer)answer.hidden=!revealed});
 document.querySelectorAll('.speaker').forEach((s,i)=>s.hidden=i!==index);
 document.querySelectorAll('.jump').forEach((b,i)=>b.classList.toggle('current',i===index));
 const counter=document.querySelector('#counter');if(counter)counter.textContent=`${index+1} / ${slides.length}`;
 const prev=document.querySelector('#prev'),next=document.querySelector('#next'),reveal=document.querySelector('#reveal');
 if(prev)prev.disabled=index===0;if(next)next.disabled=index===slides.length-1;
 if(reveal){reveal.hidden=!slides[index].querySelector('.answer');reveal.textContent=revealed?'Скрыть ответ':'Показать ответ';reveal.setAttribute('aria-pressed',String(revealed))}
 if(panel){document.querySelector('#copyPrompt').hidden=lessonData[index].kind!=='prompt';document.querySelector('#showFallback').hidden=!['response','revision'].includes(lessonData[index].kind)}
 try{history.replaceState(null,'',`#${index+1}`)}catch{}
}
function go(n){index=Math.max(0,Math.min(slides.length-1,n));revealed=false;render();if(panel){document.querySelector('#notesScroll').scrollTop=0;document.querySelector('#copyStatus').textContent=''}}
function toggleAnswer(){if(slides[index].querySelector('.answer')){revealed=!revealed;render()}}
function toggleNotes(force){if(!panel)return;const show=force??panel.hidden;panel.hidden=!show;document.querySelector('#notesBtn').setAttribute('aria-expanded',String(show));if(show)wake()}
async function full(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen()}catch{}}
document.addEventListener('pointermove',wake,{passive:true});
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
 if(ev.code==='Space'){ev.preventDefault();toggleAnswer()}
});
window.addEventListener('hashchange',()=>{const n=Number.parseInt(location.hash.slice(1),10);if(Number.isInteger(n))go(n-1)});
window.addEventListener('resize',fit);
if(panel){
 document.querySelector('#notesBtn').onclick=()=>toggleNotes();document.querySelector('#closeNotes').onclick=()=>toggleNotes(false);
 document.querySelector('#prev').onclick=()=>go(index-1);document.querySelector('#next').onclick=()=>go(index+1);document.querySelector('#reveal').onclick=toggleAnswer;document.querySelector('#fullBtn').onclick=full;
 const contents=document.querySelector('#contents');document.querySelector('#contentsBtn').onclick=()=>contents.showModal();document.querySelector('#closeContents').onclick=()=>contents.close();document.querySelectorAll('.jump').forEach(b=>b.onclick=()=>{go(+b.dataset.to);contents.close()});
 document.querySelector('#fontUp').onclick=()=>{font=Math.min(28,font+1);document.documentElement.style.setProperty('--notes-size',font+'px')};document.querySelector('#fontDown').onclick=()=>{font=Math.max(16,font-1);document.documentElement.style.setProperty('--notes-size',font+'px')};
 document.querySelector('#copyPrompt').onclick=async()=>{try{await navigator.clipboard.writeText(lessonData[index].lead);document.querySelector('#copyStatus').textContent='Скопировано. Отправьте запрос вручную в подготовленный чат.'}catch{document.querySelector('#copyStatus').textContent='Скопируйте вручную: '+lessonData[index].lead}};
 const fallback=document.querySelector('#fallback');document.querySelector('#showFallback').onclick=()=>fallback.showModal();document.querySelector('#closeFallback').onclick=()=>fallback.close();
}
render();fit();
})();
