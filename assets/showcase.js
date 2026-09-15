// Home page film stage: one big player, a searchable queue filtered by school, prev/next.
// Same manifest as the films page (assets/films.json). Nothing from YouTube loads before the
// first play: the stage shows the poster, and the youtube-nocookie iframe is injected on click.
// After that first play, picking another film plays it straight away.
(function () {
  'use strict';
  var stage = document.getElementById('rot-films');
  if (!stage) return;
  var lang = (document.documentElement.lang || 'en').slice(0, 2) === 'fr' ? 'fr' : 'en';
  var isLocal = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname);
  var preview = /[?&]preview(=|&|$)/.test(location.search);

  var T = {
    en: {
      all: 'All schools', allTag: 'Every cohort, newest first.', schools: 'Choose a school', play: 'Play', prev: 'Previous film', next: 'Next film', watch: 'Watch on YouTube',
      queue: 'Film list', search: stage.getAttribute('data-search') || 'Search',
      soon: 'This film is being uploaded. Check back soon.',
      empty: 'No film matches that.', loadError: 'The films could not be loaded.',
      count: function (n, t) { return n === t ? t + ' films' : n + ' of ' + t + ' films'; },
      films: function (n) { return n === 1 ? '1 film' : n + ' films'; },
      minutes: function (m) { return m + ' min'; }
    },
    fr: {
      all: 'Toutes les écoles', allTag: 'Toutes les promotions, les plus récentes d’abord.', schools: 'Choisir une école', play: 'Lire', prev: 'Film précédent', next: 'Film suivant', watch: 'Voir sur YouTube',
      queue: 'Liste des films', search: stage.getAttribute('data-search') || 'Chercher',
      soon: 'Ce film est en cours de mise en ligne. Revenez bientôt.',
      empty: 'Aucun film ne correspond.', loadError: 'Les films n’ont pas pu être chargés.',
      count: function (n, t) { return n === t ? t + ' films' : n + ' sur ' + t + ' films'; },
      films: function (n) { return n === 1 ? '1 film' : n + ' films'; },
      minutes: function (m) { return m + ' min'; }
    }
  }[lang];

  var ICON = {
    play: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>',
    left: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>',
    right: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>',
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>'
  };

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === 'html') n.innerHTML = attrs[k];
      else if (k === 'text') n.textContent = attrs[k];
      else n.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) n.appendChild(c); });
    return n;
  }
  function pick(v) { return (v && typeof v === 'object') ? (v[lang] || v.en || v.fr || '') : (v || ''); }
  function both(v) { return (v && typeof v === 'object') ? [v.en, v.fr].filter(Boolean).join(' ') : (v || ''); }
  function fold(s) { return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function mmss(s) { s = Math.round(s || 0); if (!s) return ''; var m = Math.floor(s / 60), r = s % 60; return m + ':' + (r < 10 ? '0' : '') + r; }
  function posterUrl(f) {
    if (f.poster) return '/' + String(f.poster).replace(/^\/?/, '');
    if (f.youtube) return 'https://i.ytimg.com/vi/' + encodeURIComponent(f.youtube) + '/hqdefault.jpg';
    return '';
  }
  function hasVideo(f) { return !!(f.youtube || (isLocal && f.file)); }

  fetch('/assets/films.json', { cache: 'no-cache' })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(render)
    .catch(function () { stage.appendChild(el('p', { 'class': 'rot-empty', text: T.loadError })); });

  function render(data) {
    var schools = data.schools || {}, terms = data.terms || {};
    var films = (data.films || []).filter(function (f) { return f && f.id && (hasVideo(f) || preview); });
    if (!films.length) { stage.appendChild(el('p', { 'class': 'rot-empty', text: T.loadError })); return; }

    // manifest order by school, newest term first (same as the films page)
    var schoolOrder = Object.keys(schools);
    films.sort(function (a, b) {
      var sa = schoolOrder.indexOf(a.school), sb = schoolOrder.indexOf(b.school);
      if (sa !== sb) return (sa < 0 ? 99 : sa) - (sb < 0 ? 99 : sb);
      return a.term < b.term ? 1 : a.term > b.term ? -1 : 0;
    });
    films.forEach(function (f) {
      var s = schools[f.school] || { name: f.school };
      f._where = s.name + (f.term ? ', ' + (pick(terms[f.term]) || f.term) : '');
      f._hay = fold([both(f.title), f.team, s.name, s.city, f.school, both(f.course), both(f.tagline), both(terms[f.term]), f.term].join(' '));
    });

    // ---- player ----
    var poster = el('img', { alt: '', decoding: 'async' });
    var playBtn = el('button', { type: 'button', 'class': 'rot-play', 'aria-label': T.play }, [poster, el('span', { 'class': 'rot-play-btn', html: ICON.play })]);
    var screen = el('div', { 'class': 'rot-screen' }, [playBtn]);
    var h3 = el('h3', { 'class': 'rot-title' });
    var where = el('p', { 'class': 'rot-where' });
    var syn = el('p', { 'class': 'rot-syn' });
    var yt = el('a', { 'class': 'rot-yt', target: '_blank', rel: 'noopener', text: T.watch });
    var prevBtn = el('button', { type: 'button', 'aria-label': T.prev, html: ICON.left });
    var nextBtn = el('button', { type: 'button', 'aria-label': T.next, html: ICON.right });
    var player = el('div', { 'class': 'rot-player' }, [
      screen,
      el('div', { 'class': 'rot-now' }, [el('div', null, [h3, where, syn, yt]), el('div', { 'class': 'rot-nav' }, [prevBtn, nextBtn])])
    ]);

    // ---- queue ----
    var present = schoolOrder.filter(function (s) { return films.some(function (f) { return f.school === s; }); });
    var counts = {}; films.forEach(function (f) { counts[f.school] = (counts[f.school] || 0) + 1; });
    var picker = window.RoTSchools.render({
      schools: schools, order: present, counts: counts, total: films.length, lang: lang,
      T: { all: T.all, allTag: T.allTag, films: T.films, label: T.schools },
      onSelect: function (id) { school = id; applyFilter(); }
    });
    stage.parentNode.insertBefore(picker.el, stage);
    var search = el('input', { type: 'search', placeholder: T.search, 'aria-label': T.search, autocomplete: 'off' });
    var count = el('p', { 'class': 'rot-count', 'aria-live': 'polite' });
    var queue = el('ol', { 'class': 'rot-queue', 'aria-label': T.queue });
    var list = el('aside', { 'class': 'rot-list' }, [el('div', { 'class': 'rot-list-inner' }, [
      el('div', { 'class': 'rot-tools' }, [el('label', { 'class': 'rot-search', html: ICON.search }, [search]), count]),
      queue
    ])]);
    stage.appendChild(player); stage.appendChild(list);

    var items = {};
    films.forEach(function (f) {
      var p = posterUrl(f);
      var b = el('button', { type: 'button', 'class': 'rot-item', 'data-id': f.id }, [
        el('span', { 'class': 'rot-thumb' }, [p ? el('img', { src: p, alt: '', loading: 'lazy', decoding: 'async' }) : null, f.duration ? el('span', { 'class': 'rot-dur', text: mmss(f.duration) }) : null]),
        el('span', { 'class': 'rot-item-text' }, [el('span', { 'class': 'rot-item-title', text: pick(f.title) }), el('span', { 'class': 'rot-item-meta', text: f._where })])
      ]);
      b.addEventListener('click', function () { select(f, played); });
      items[f.id] = el('li', null, [b]);
      queue.appendChild(items[f.id]);
    });
    var emptyLi = el('li', { 'class': 'rot-empty', text: T.empty, hidden: '' });
    queue.appendChild(emptyLi);

    // ---- state ----
    var current = null, played = false, school = '', q = '', visible = films.slice();

    function applyFilter() {
      var needle = fold(q).trim();
      visible = films.filter(function (f) { return (!school || f.school === school) && (!needle || f._hay.indexOf(needle) >= 0); });
      films.forEach(function (f) { items[f.id].hidden = visible.indexOf(f) < 0; });
      emptyLi.hidden = visible.length > 0;
      count.textContent = T.count(visible.length, films.length);
      syncNav();
    }
    function syncNav() {
      var i = visible.indexOf(current);
      prevBtn.disabled = visible.length === 0 || (i >= 0 && i === 0);
      nextBtn.disabled = visible.length === 0 || (i >= 0 && i === visible.length - 1);
    }
    function select(f, autoplay) {
      current = f;
      h3.textContent = pick(f.title);
      where.textContent = f._where + (pick(f.course) ? '. ' + pick(f.course) : '') + (f.team && f.team !== pick(f.title) ? '. ' + f.team : '') + (f.duration ? '. ' + T.minutes(Math.round(f.duration / 60)) : '');
      var s = pick(f.synopsis) || pick(f.tagline);
      syn.textContent = s; syn.hidden = !s;
      if (f.youtube) { yt.href = 'https://www.youtube.com/watch?v=' + encodeURIComponent(f.youtube); yt.hidden = false; } else { yt.hidden = true; }
      Object.keys(items).forEach(function (id) { items[id].firstChild.setAttribute('aria-current', id === f.id ? 'true' : 'false'); });
      var li = items[f.id]; if (li && !li.hidden) li.scrollIntoView({ block: 'nearest', inline: 'nearest' });
      if (autoplay) mount(f); else showPoster(f);
      syncNav();
    }
    function showPoster(f) {
      screen.innerHTML = '';
      poster.src = posterUrl(f);
      playBtn.setAttribute('aria-label', T.play + ': ' + pick(f.title));
      screen.appendChild(playBtn);
    }
    function mount(f) {
      played = true;
      screen.innerHTML = '';
      if (f.youtube) {
        screen.appendChild(el('iframe', {
          src: 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(f.youtube) + '?autoplay=1&rel=0&modestbranding=1&hl=' + lang,
          title: pick(f.title), allow: 'autoplay; fullscreen; picture-in-picture; encrypted-media', allowfullscreen: '', referrerpolicy: 'strict-origin-when-cross-origin'
        }));
      } else if (isLocal && f.file) {
        screen.appendChild(el('video', { controls: '', autoplay: '', playsinline: '', preload: 'metadata', src: '/media/' + encodeURIComponent(f.file), poster: posterUrl(f) }));
      } else {
        var p = posterUrl(f);
        screen.appendChild(el('div', { 'class': 'rot-unavailable' }, [p ? el('img', { src: p, alt: '' }) : null, el('span', { text: T.soon })]));
      }
    }
    function step(dir) {
      if (!visible.length) return;
      var i = visible.indexOf(current);
      var n = i < 0 ? (dir > 0 ? 0 : visible.length - 1) : i + dir;
      if (n < 0 || n >= visible.length) return;
      select(visible[n], played);
    }

    playBtn.addEventListener('click', function () { if (current) mount(current); });
    prevBtn.addEventListener('click', function () { step(-1); });
    nextBtn.addEventListener('click', function () { step(1); });
    search.addEventListener('input', function () { q = search.value; applyFilter(); });
    queue.addEventListener('keydown', function (e) {
      if (['ArrowDown', 'ArrowUp', 'Home', 'End'].indexOf(e.key) < 0) return;
      var btns = [].slice.call(queue.querySelectorAll('li:not([hidden]) .rot-item'));
      var i = btns.indexOf(document.activeElement); if (i < 0) return;
      e.preventDefault();
      var n = e.key === 'ArrowDown' ? i + 1 : e.key === 'ArrowUp' ? i - 1 : e.key === 'Home' ? 0 : btns.length - 1;
      if (btns[n]) btns[n].focus();
    });

    applyFilter();
    var m = /film=([\w-]+)/.exec(location.hash);
    var start = m && films.find(function (f) { return f.id === m[1]; });
    select(start || films[0], false);
    if (start) stage.scrollIntoView({ block: 'start' });
  }
})();
