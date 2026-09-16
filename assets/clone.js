// Static SLAVÉ site interactivity (React removed). Pages live at clean folder URLs:
// / (Rails of Time), /films/, /asso/, /dignity/, /contact/, and the same under /fr/.
(function(){
  var path=location.pathname;
  // an old bookmark to /index.html still serves; drop the file name from the address bar
  if(/\/index\.html$/.test(path)){
    try{ history.replaceState(null,'',path.replace(/index\.html$/,'')+location.search+location.hash); path=location.pathname; }catch(e){}
  }
  var inFr=/^\/fr(\/|$)/.test(path);
  var home = inFr ? '/fr/' : '/';
  var counterpart = inFr ? (path.replace(/^\/fr/,'')||'/') : ('/fr'+path);

  // --- Language switcher (EN root / FR under /fr/) ---
  document.querySelectorAll('.language-toggle button').forEach(function(b){
    var t=(b.textContent||'').trim(); if(t!=='EN'&&t!=='FR') return;
    var active=(t==='FR')===inFr; b.style.cursor='pointer';
    if(active){ b.style.background='#c0521c'; b.style.color='#fff'; b.style.borderRadius='8px'; b.style.padding='3px 10px'; b.setAttribute('aria-current','true'); }
    else { b.style.background='transparent'; b.style.color='#12395f'; }
    b.addEventListener('click',function(e){ e.preventDefault(); if(!active) location.href=counterpart+location.hash; });
  });

  // --- Logo (brand button / wordmark) -> home ---
  var header=document.querySelector('header');
  if(header){
    var brand=[].slice.call(header.querySelectorAll('button,a')).find(function(el){ return el.querySelector('img[src*="slave-emblem"],img[src*="logo"]'); });
    if(brand){ brand.style.cursor='pointer'; brand.setAttribute('aria-label', inFr ? 'Accueil' : 'Home'); brand.addEventListener('click',function(e){ e.preventDefault(); location.href=home; }); }
  }

  // --- Top-nav "Projects/Projets" dropdown ---
  document.querySelectorAll('header nav button').forEach(function(b){
    var wrap=b.parentElement, menu=wrap&&wrap.querySelector(':scope > div'); if(!menu) return;
    var show=function(){menu.classList.remove('opacity-0','scale-95','pointer-events-none');menu.classList.add('opacity-100','scale-100');menu.style.pointerEvents='auto';b.setAttribute('aria-expanded','true');};
    var hide=function(){menu.classList.add('opacity-0','scale-95','pointer-events-none');menu.classList.remove('opacity-100','scale-100');menu.style.pointerEvents='';b.setAttribute('aria-expanded','false');};
    b.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();menu.classList.contains('opacity-0')?show():hide();});
    wrap.addEventListener('mouseenter',show); wrap.addEventListener('mouseleave',hide);
    wrap.addEventListener('focusout',function(e){ if(!wrap.contains(e.relatedTarget)) hide(); });
    document.addEventListener('click',function(e){ if(!wrap.contains(e.target)) hide(); });
    document.addEventListener('keydown',function(e){ if(e.key==='Escape') hide(); });
  });

  // --- Mobile menu (a panel built from the nav links + Contact; wired to the burger) ---
  if(header){
    var burger=[].slice.call(header.querySelectorAll('button')).find(function(b){ return b.querySelector('.lucide-menu'); });
    if(burger){
      var panel=document.createElement('div'); panel.id='mobile-menu';
      panel.style.cssText='display:none;position:absolute;top:100%;left:0;right:0;background:#f7f3eb;border-top:1px solid #ede4d3;box-shadow:0 14px 28px -14px rgba(18, 57, 95,.28);padding:.5rem 1.25rem 1.1rem;z-index:60;';
      var links=[].slice.call(header.querySelectorAll('nav a'));
      var contact=header.querySelector('a[href$="/contact/"]'); if(contact) links.push(contact);
      links.forEach(function(src){
        var a=document.createElement('a'); a.href=src.getAttribute('href'); a.textContent=src.textContent.trim();
        a.style.cssText='display:block;padding:.8rem .25rem;color:#12395f;font-weight:600;border-bottom:1px solid #ede4d3;text-decoration:none;font-family:inherit;';
        panel.appendChild(a);
      });
      header.style.position='relative'; header.appendChild(panel);
      burger.setAttribute('aria-expanded','false'); burger.setAttribute('aria-label', inFr ? 'Menu' : 'Menu');
      burger.addEventListener('click',function(e){ e.preventDefault(); e.stopPropagation(); var open=panel.style.display==='none'; panel.style.display=open?'block':'none'; burger.setAttribute('aria-expanded', open?'true':'false'); });
      document.addEventListener('click',function(e){ if(!header.contains(e.target)){ panel.style.display='none'; burger.setAttribute('aria-expanded','false'); } });
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
