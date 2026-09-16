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
     Two crops (wide for landscape headers, portrait for phones) in three codecs each. The poster is the
     first paint; the video is fetched only after the page has loaded, never with reduced motion or
     Save-Data on. The first codec the browser decodes smoothly and power-efficiently wins, so a
     laptop without AV1 hardware gets HEVC or H.264 instead of burning its CPU. Pauses off screen. */
  var video = document.querySelector('.hero-media video[data-sources]');
  if (video) {
    var credit = document.querySelector('.credit');
    var film = credit && credit.querySelector('[data-film]');
    var school = credit && credit.querySelector('[data-school]');
    var toggle = credit && credit.querySelector('button');
    var cuts = JSON.parse(video.getAttribute('data-credits') || '[]');
    var sources = JSON.parse(video.getAttribute('data-sources'));
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var conn = navigator.connection;
    var saveData = conn && (conn.saveData || /(^|-)2g$|^3g$/.test(conn.effectiveType || ''));
    var userPaused = false, started = false;
    var L = fr ? { pause: 'Pause', play: 'Lecture' } : { pause: 'Pause', play: 'Play' };

    function label() { if (toggle) toggle.textContent = video.paused ? L.play : L.pause; }
    function pick() {
      var box = video.parentElement.getBoundingClientRect();
      var list = sources[box.height > box.width * 0.75 ? 'phone' : 'wide'];
      var playable = list.filter(function (s) { return video.canPlayType(s.type) !== ''; });
      if (!navigator.mediaCapabilities || !navigator.mediaCapabilities.decodingInfo) return Promise.resolve(playable[0]);
      return Promise.all(playable.map(function (s) {
        return navigator.mediaCapabilities.decodingInfo({ type: 'file', video: { contentType: s.type, width: s.w, height: s.h, bitrate: s.bitrate, framerate: 27.27 } })
          .then(function (r) { return { s: s, r: r }; }, function () { return { s: s, r: { supported: false } }; });
      })).then(function (res) {
        var best = res.find(function (x) { return x.r.supported && x.r.smooth && x.r.powerEfficient; }) ||
                   res.find(function (x) { return x.r.supported && x.r.smooth; }) ||
                   res.find(function (x) { return x.r.supported; });
        return best ? best.s : playable[playable.length - 1];
      });
    }
    function start() {
      if (started) return; started = true;
      pick().then(function (s) {
        if (!s) return;
        video.src = s.src;
        var p = video.play();
        if (p && p.catch) p.catch(label);
      });
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
