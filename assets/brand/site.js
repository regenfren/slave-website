/* S.L.A.V.É. site behaviour: nav dropdown, mobile menu, the home reel, the static contact form.
   The film player (showcase.js), school picker (schools.js) and films page (films.js) are separate. */
(function () {
  'use strict';
  var fr = (document.documentElement.lang || 'en').slice(0, 2) === 'fr';

  /* ---------- Projects dropdown ---------- */
  document.querySelectorAll('.nav-projects').forEach(function (wrap) {
    var btn = wrap.querySelector('button');
    function set(open) { wrap.classList.toggle('open', open); btn.setAttribute('aria-expanded', open ? 'true' : 'false'); }
    btn.addEventListener('click', function (e) { e.stopPropagation(); set(!wrap.classList.contains('open')); });
    wrap.addEventListener('mouseenter', function () { set(true); });
    wrap.addEventListener('mouseleave', function () { set(false); });
    wrap.addEventListener('focusout', function (e) { if (!wrap.contains(e.relatedTarget)) set(false); });
    document.addEventListener('click', function (e) { if (!wrap.contains(e.target)) set(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { set(false); } });
  });

  /* ---------- mobile menu ---------- */
  var burger = document.querySelector('.burger');
  var menu = document.getElementById('mobile-menu');
  if (burger && menu) {
    burger.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = !menu.classList.contains('open');
      menu.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { menu.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); } });
  }

  /* ---------- home reel ----------
     The poster (a 26 KB image) is the first paint. The video is only fetched after the page has
     loaded, never with reduced motion or Save-Data on, and it pauses when scrolled out of view. */
  var video = document.querySelector('.hero-media video[data-src]');
  if (video) {
    var credit = document.querySelector('.credit');
    var film = credit && credit.querySelector('[data-film]');
    var school = credit && credit.querySelector('[data-school]');
    var toggle = credit && credit.querySelector('button');
    var cuts = JSON.parse(video.getAttribute('data-credits') || '[]');
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var saveData = navigator.connection && navigator.connection.saveData;
    var userPaused = false;
    var L = fr ? { pause: 'Pause', play: 'Lecture' } : { pause: 'Pause', play: 'Play' };

    function label() { if (toggle) toggle.textContent = video.paused ? L.play : L.pause; }
    function start() {
      var small = window.matchMedia('(max-width: 760px)').matches;
      video.src = video.getAttribute(small ? 'data-src-small' : 'data-src');
      video.load();
      var p = video.play();
      if (p && p.catch) p.catch(function () { label(); });
    }
    video.addEventListener('playing', function () { video.classList.add('playing'); label(); });
    video.addEventListener('pause', label);
    video.addEventListener('timeupdate', function () {
      if (!film || !cuts.length) return;
      var t = video.currentTime + 0.15, c = cuts[0];
      for (var i = 0; i < cuts.length; i++) if (cuts[i][0] <= t) c = cuts[i];
      if (film.textContent !== c[1]) film.textContent = c[1];
      if (school.textContent !== c[2]) school.textContent = c[2];
    });
    if (toggle) {
      toggle.addEventListener('click', function () {
        if (!video.currentSrc) { userPaused = false; start(); return; }
        if (video.paused) { userPaused = false; video.play(); } else { userPaused = true; video.pause(); }
      });
    }
    if (reduce || saveData) {
      if (toggle) toggle.textContent = L.play;
    } else if (document.readyState === 'complete') {
      start();
    } else {
      window.addEventListener('load', function () { setTimeout(start, 150); });
    }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!video.currentSrc || userPaused) return;
          if (en.isIntersecting) video.play().catch(function () {}); else video.pause();
        });
      }, { threshold: 0.05 }).observe(video);
    }
  }

  /* ---------- contact form: the site has no mail backend yet ---------- */
  document.querySelectorAll('form[data-static]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = f.querySelector('.form-note');
      if (note) note.textContent = fr ? 'Le formulaire n’est pas encore relié. Écrivez-nous à asso.slave@gmail.com.' : 'This form is not connected yet. Write to us at asso.slave@gmail.com.';
    });
  });

  /* ---------- 404: back button ---------- */
  document.querySelectorAll('[data-back]').forEach(function (b) {
    b.addEventListener('click', function () { history.length > 1 ? history.back() : (location.href = fr ? '/fr/' : '/'); });
  });
})();
