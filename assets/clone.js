// Static SLAVÉ clone interactivity (React removed).
(function(){
  var path=location.pathname, file=path.substring(path.lastIndexOf('/')+1)||'index.html', inFr=/\/fr\//.test(path);
  var home = inFr ? '../index.html' : 'index.html';

  // --- Language switcher (EN root / FR under /fr/) ---
  document.querySelectorAll('button, a').forEach(function(b){
    var t=(b.textContent||'').trim(); if(t!=='EN'&&t!=='FR') return;
    var target=(t==='FR')?(inFr?file:'fr/'+file):(inFr?'../'+file:file);
    var active=(t==='FR')===inFr; b.style.cursor='pointer';
    if(active){ b.style.background='#A8552F'; b.style.color='#fff'; b.style.borderRadius='8px'; b.style.padding='3px 10px'; }
    else { b.style.background='transparent'; b.style.color='#3A2E20'; }
    b.addEventListener('click',function(e){ e.preventDefault(); location.href=target; });
  });

  // --- Logo (brand button / wordmark) -> home ---
  var header=document.querySelector('header');
  if(header){
    var brand=[].slice.call(header.querySelectorAll('button,a')).find(function(el){ return el.querySelector('img[src*="slave-emblem"],img[src*="logo"]'); });
    if(brand){ brand.style.cursor='pointer'; brand.addEventListener('click',function(e){ e.preventDefault(); location.href=home; }); }
  }

  // --- Top-nav "Projects/Projets" dropdown ---
  document.querySelectorAll('button').forEach(function(b){
    var t=(b.textContent||'').trim().replace(/\s+/g,' '); if(!/^(Projects|Projets)\b/.test(t)) return;
    var wrap=b.parentElement, menu=wrap&&wrap.querySelector(':scope > div'); if(!menu) return;
    var show=function(){menu.classList.remove('opacity-0','scale-95','pointer-events-none');menu.classList.add('opacity-100','scale-100');menu.style.pointerEvents='auto';};
    var hide=function(){menu.classList.add('opacity-0','scale-95','pointer-events-none');menu.classList.remove('opacity-100','scale-100');menu.style.pointerEvents='';};
    b.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();menu.classList.contains('opacity-0')?show():hide();});
    wrap.addEventListener('mouseenter',show); wrap.addEventListener('mouseleave',hide);
    document.addEventListener('click',function(e){ if(!wrap.contains(e.target)) hide(); });
  });

  // --- Mobile menu (build a panel from nav links; wire the hamburger) ---
  if(header){
    var burger=[].slice.call(header.querySelectorAll('button')).find(function(b){ return b.querySelector('.lucide-menu'); });
    if(burger){
      var panel=document.createElement('div'); panel.id='mobile-menu';
      panel.style.cssText='display:none;position:absolute;top:100%;left:0;right:0;background:#FAF6EF;border-top:1px solid #EAE0CF;box-shadow:0 14px 28px -14px rgba(58,46,32,.28);padding:.5rem 1.25rem 1.1rem;z-index:60;';
      ['index.html','association.html','projects.html','dignity.html','films.html','contact.html'].forEach(function(h){
        var src=[].slice.call(header.querySelectorAll('a[href$="'+h+'"]')).find(function(x){return x.textContent.trim();});
        if(!src) return; var a=document.createElement('a'); a.href=src.getAttribute('href'); a.textContent=src.textContent.trim();
        a.style.cssText='display:block;padding:.8rem .25rem;color:#3A2E20;font-weight:600;border-bottom:1px solid #EAE0CF;text-decoration:none;font-family:inherit;';
        panel.appendChild(a);
      });
      header.style.position='relative'; header.appendChild(panel);
      burger.addEventListener('click',function(e){ e.preventDefault(); e.stopPropagation(); panel.style.display = panel.style.display==='none'?'block':'none'; });
      document.addEventListener('click',function(e){ if(!header.contains(e.target)) panel.style.display='none'; });
    }
  }

  // --- Gallery carousel (prev/next/dots) ---
  document.querySelectorAll('.transition-transform').forEach(function(track){
    var slides=track.querySelectorAll(':scope > .flex-shrink-0'); if(slides.length<2) return;
    var wrap=track.closest('section'); if(!wrap) return;
    var btns=[].slice.call(wrap.querySelectorAll('button'));
    var arrows=btns.filter(function(b){return b.querySelector('svg');});
    var dots=btns.filter(function(b){return !b.querySelector('svg');});
    var n=slides.length, idx=0;
    function go(i){ idx=(i+n)%n; track.style.transform='translateX(-'+(idx*100)+'%)'; dots.forEach(function(d,j){ d.style.opacity=j===idx?'1':'.45'; }); }
    arrows.forEach(function(b){ var left=/left-/.test(b.className); b.style.cursor='pointer'; b.addEventListener('click',function(e){e.preventDefault();go(idx+(left?-1:1));}); });
    dots.forEach(function(d,j){ d.style.cursor='pointer'; d.addEventListener('click',function(e){e.preventDefault();go(j);}); });
    go(0);
  });

  // --- Contact form: prevent real submit ---
  document.querySelectorAll('form').forEach(function(f){ f.addEventListener('submit',function(ev){ ev.preventDefault(); alert('This is a static preview — form is not wired.'); }); });
})();
