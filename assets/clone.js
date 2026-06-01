// --- Language switcher (EN at root, FR under /fr/) ---
(function(){
  var path = location.pathname;
  var file = path.substring(path.lastIndexOf('/')+1) || 'index.html';
  var inFr = /\/fr\//.test(path);
  document.querySelectorAll('button, a').forEach(function(b){
    var t=(b.textContent||'').trim();
    if(t!=='EN' && t!=='FR') return;
    var target = (t==='FR') ? (inFr ? file : 'fr/'+file) : (inFr ? '../'+file : file);
    var active = (t==='FR')===inFr;
    b.style.cursor='pointer';
    if(active){ b.style.background='#C0452A'; b.style.color='#fff'; b.style.borderRadius='8px'; b.style.padding='3px 9px'; }
    else { b.style.background='transparent'; b.style.color='#1C1A17'; }
    b.addEventListener('click', function(e){ e.preventDefault(); location.href = target; });
  });
})();

// Interactivity for the static SLAVÉ clone (React removed).

// --- Top-nav "Projects" dropdown (Rails of Time + Right to Dignity) ---
function wireProjectsMenu(b){
  var wrap = b.parentElement;
  var menu = wrap && wrap.querySelector(':scope > div');
  if(!menu) return;
  var show=function(){menu.classList.remove('opacity-0','scale-95','pointer-events-none');menu.classList.add('opacity-100','scale-100');menu.style.pointerEvents='auto';};
  var hide=function(){menu.classList.add('opacity-0','scale-95','pointer-events-none');menu.classList.remove('opacity-100','scale-100');menu.style.pointerEvents='';};
  b.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();menu.classList.contains('opacity-0')?show():hide();});
  wrap.addEventListener('mouseenter',show);
  wrap.addEventListener('mouseleave',hide);
  document.addEventListener('click',function(e){ if(!wrap.contains(e.target)) hide(); });
}
document.querySelectorAll('button').forEach(function(b){
  var t=(b.textContent||'').trim().replace(/\s+/g,' ');
  if(t==='Projects'||/^Projects\b/.test(t)) wireProjectsMenu(b);
});

// --- Mobile menu toggle ---
document.addEventListener('click', function (e) {
  var btn = e.target.closest('button');
  if (!btn) return;
  var label = (btn.getAttribute('aria-label') || '').toLowerCase();
  if (label.indexOf('menu') !== -1 || btn.querySelector('.lucide-menu')) {
    var panel = document.getElementById('mobile-menu');
    if (panel) panel.classList.toggle('hidden');
  }
});

// --- Contact form: prevent real submit on the static clone ---
document.querySelectorAll('form').forEach(function (f) {
  f.addEventListener('submit', function (ev) { ev.preventDefault(); alert('This is a static preview — form is not wired.'); });
});
