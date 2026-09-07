// Student films page. Reads assets/films.json and renders one block per school + term.
// No video is loaded until someone clicks a poster: then a youtube-nocookie iframe (or, on
// localhost, the original file from media/) is injected into the dialog.
(function () {
  'use strict';
  var script = document.currentScript;
  var assets = (script && script.getAttribute('data-assets')) || 'assets/';
  var media = assets.replace(/assets\/$/, 'media/');
  var lang = (document.documentElement.lang || 'en').slice(0, 2) === 'fr' ? 'fr' : 'en';
  var root = document.getElementById('films');
  if (!root) return;

  var isLocal = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname);
  var preview = /[?&]preview(=|&|$)/.test(location.search);

  var T = {
    en: {
      all: 'All schools', watch: 'Watch on YouTube', close: 'Close', prev: 'Previous film', next: 'Next film',
      scrollPrev: 'Scroll back', scrollNext: 'Scroll forward',
      soon: 'This film is being uploaded. Check back soon.', soonTag: 'Coming soon',
      empty: 'No films published yet.', loadError: 'The film list could not be loaded.',
      count: function (n) { return n === 1 ? '1 film' : n + ' films'; },
      minutes: function (m) { return m + ' min'; }
    },
    fr: {
      all: 'Toutes les écoles', watch: 'Voir sur YouTube', close: 'Fermer', prev: 'Film précédent', next: 'Film suivant',
      scrollPrev: 'Défiler vers l’arrière', scrollNext: 'Défiler vers l’avant',
      soon: 'Ce film est en cours de mise en ligne. Revenez bientôt.', soonTag: 'Bientôt',
      empty: 'Aucun film publié pour le moment.', loadError: 'La liste des films n’a pas pu être chargée.',
      count: function (n) { return n === 1 ? '1 film' : n + ' films'; },
      minutes: function (m) { return m + ' min'; }
    }
  }[lang];

  var ICON = {
    play: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>',
    left: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>',
    right: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>'
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
  function mmss(s) { s = Math.round(s || 0); if (!s) return ''; var m = Math.floor(s / 60), r = s % 60; return m + ':' + (r < 10 ? '0' : '') + r; }
  function posterUrl(f) {
    if (f.poster) return assets + String(f.poster).replace(/^assets\//, '');
    if (f.youtube) return 'https://i.ytimg.com/vi/' + encodeURIComponent(f.youtube) + '/hqdefault.jpg';
    return '';
  }
  function hasVideo(f) { return !!(f.youtube || (isLocal && f.file)); }

  fetch(assets + 'films.json', { cache: 'no-cache' })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(render)
    .catch(function () { root.appendChild(el('p', { 'class': 'films-empty', text: T.loadError })); });

  function render(data) {
    var schools = data.schools || {};
    var terms = data.terms || {};
    var films = (data.films || []).filter(function (f) { return f && f.id && (hasVideo(f) || preview); });

    var countEl = document.getElementById('films-count');
    if (countEl) countEl.textContent = films.length ? T.count(films.length) : '';
    if (!films.length) { root.appendChild(el('p', { 'class': 'films-empty', text: T.empty })); return; }

    // group by school (manifest order), then term (newest first), films in manifest order
    var schoolOrder = Object.keys(schools);
    var groups = {};
    films.forEach(function (f) {
      var key = f.school + '|' + f.term;
      if (!groups[key]) groups[key] = { school: f.school, term: f.term, films: [] };
      groups[key].films.push(f);
    });
    var ordered = Object.keys(groups).map(function (k) { return groups[k]; }).sort(function (a, b) {
      var sa = schoolOrder.indexOf(a.school), sb = schoolOrder.indexOf(b.school);
      if (sa !== sb) return (sa < 0 ? 99 : sa) - (sb < 0 ? 99 : sb);
      return a.term < b.term ? 1 : a.term > b.term ? -1 : 0;
    });

    // flat list in render order, for prev/next in the dialog
    var flat = [];
    ordered.forEach(function (g) { g.films.forEach(function (f) { flat.push(f); }); });

    // school filter, only when there is more than one school
    var schoolsPresent = schoolOrder.filter(function (s) { return ordered.some(function (g) { return g.school === s; }); });
    if (schoolsPresent.length > 1) {
      var filters = el('div', { 'class': 'films-filters', role: 'group' });
      var all = el('button', { type: 'button', 'aria-pressed': 'true', 'data-school': '', text: T.all });
      filters.appendChild(all);
      schoolsPresent.forEach(function (s) {
        filters.appendChild(el('button', { type: 'button', 'aria-pressed': 'false', 'data-school': s, text: (schools[s] && schools[s].name) || s }));
      });
      filters.addEventListener('click', function (e) {
        var b = e.target.closest('button'); if (!b) return;
        var s = b.getAttribute('data-school');
        filters.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        root.querySelectorAll('.films-group').forEach(function (sec) { sec.hidden = !!s && sec.getAttribute('data-school') !== s; });
      });
      root.appendChild(filters);
    }

    ordered.forEach(function (g) {
      var school = schools[g.school] || { name: g.school };
      var termLabel = pick(terms[g.term]) || g.term;
      var courses = []; g.films.forEach(function (f) { var c = pick(f.course); if (c && courses.indexOf(c) < 0) courses.push(c); });
      var sub = termLabel + (courses.length === 1 ? ', ' + courses[0] : '') + (school.city ? ' (' + school.city + ')' : '');

      var row = el('div', { 'class': 'films-row' });
      g.films.forEach(function (f) { row.appendChild(card(f)); });

      var prev = el('button', { type: 'button', 'class': 'films-arrow', 'aria-label': T.scrollPrev, html: ICON.left });
      var next = el('button', { type: 'button', 'class': 'films-arrow', 'aria-label': T.scrollNext, html: ICON.right });
      prev.addEventListener('click', function () { scrollRow(row, -1); });
      next.addEventListener('click', function () { scrollRow(row, 1); });
      function sync() {
        prev.disabled = row.scrollLeft <= 2;
        next.disabled = row.scrollLeft + row.clientWidth >= row.scrollWidth - 2;
      }
      row.addEventListener('scroll', sync, { passive: true });
      window.addEventListener('resize', sync);

      var sec = el('section', { 'class': 'films-group', 'data-school': g.school }, [
        el('div', { 'class': 'films-group-head' }, [
          el('div', null, [el('h2', { text: school.name }), el('p', { text: sub })]),
          el('div', { 'class': 'films-arrows' }, [prev, next])
        ]),
        el('div', { 'class': 'films-row-wrap' }, [row])
      ]);
      root.appendChild(sec);
      requestAnimationFrame(sync);
    });

    function scrollRow(row, dir) {
      var cardEl = row.querySelector('.film-card');
      var step = cardEl ? (cardEl.getBoundingClientRect().width + 20) * 2 : row.clientWidth * .8;
      row.scrollBy({ left: dir * step, behavior: 'smooth' });
    }

    function card(f) {
      var poster = posterUrl(f);
      var title = pick(f.title);
      var second = pick(f.tagline) || (f.team && f.team !== title ? f.team : '');
      var b = el('button', { type: 'button', 'class': 'film-card', 'data-id': f.id, 'aria-label': title }, [
        el('div', { 'class': 'film-poster' }, [
          poster ? el('img', { src: poster, alt: '', loading: 'lazy', decoding: 'async' }) : null,
          el('span', { 'class': 'film-play', html: ICON.play }),
          f.duration ? el('span', { 'class': 'film-dur', text: mmss(f.duration) }) : null,
          !hasVideo(f) ? el('span', { 'class': 'film-soon', text: T.soonTag }) : null
        ]),
        el('h3', { 'class': 'film-title', text: title }),
        second ? el('p', { 'class': 'film-meta', text: second }) : null
      ]);
      b.addEventListener('click', function () { open(flat.indexOf(f)); });
      return b;
    }

    // ---- dialog ----
    var dialog = el('dialog', { 'class': 'film-dialog', 'aria-label': '' });
    var player = el('div', { 'class': 'film-player' });
    var closeBtn = el('button', { type: 'button', 'class': 'film-close', 'aria-label': T.close, html: ICON.close });
    var h2 = el('h2');
    var where = el('p', { 'class': 'film-where' });
    var synopsis = el('p', { 'class': 'film-synopsis' });
    var yt = el('a', { 'class': 'film-yt', target: '_blank', rel: 'noopener', text: T.watch });
    var prevBtn = el('button', { type: 'button', 'aria-label': T.prev, html: ICON.left });
    var nextBtn = el('button', { type: 'button', 'aria-label': T.next, html: ICON.right });
    dialog.appendChild(el('div', { 'class': 'film-dialog-inner' }, [
      el('div', { style: 'position:relative' }, [player, closeBtn]),
      el('div', { 'class': 'film-info' }, [
        el('div', null, [h2, where, synopsis, yt]),
        el('div', { 'class': 'film-dialog-nav' }, [prevBtn, nextBtn])
      ])
    ]));
    document.body.appendChild(dialog);
    var current = -1;

    function open(i) {
      if (i < 0 || i >= flat.length) return;
      current = i;
      var f = flat[i];
      var title = pick(f.title);
      var school = schools[f.school] || { name: f.school };
      var course = pick(f.course);
      h2.textContent = title;
      dialog.setAttribute('aria-label', title);
      where.textContent = school.name + (f.term ? ', ' + (pick(terms[f.term]) || f.term) : '') + (course ? '. ' + course : '') +
        (f.team && f.team !== title ? '. ' + f.team : '') + (f.duration ? '. ' + T.minutes(Math.round(f.duration / 60)) : '');
      var syn = pick(f.synopsis) || pick(f.tagline);
      synopsis.textContent = syn; synopsis.hidden = !syn;
      if (f.youtube) { yt.href = 'https://www.youtube.com/watch?v=' + encodeURIComponent(f.youtube); yt.hidden = false; } else { yt.hidden = true; }
      prevBtn.disabled = i === 0; nextBtn.disabled = i === flat.length - 1;
      mount(f);
      if (!dialog.open) { dialog.showModal(); document.body.classList.add('film-dialog-open'); }
      closeBtn.focus();
    }
    function mount(f) {
      player.innerHTML = '';
      if (f.youtube) {
        player.appendChild(el('iframe', {
          src: 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(f.youtube) + '?autoplay=1&rel=0&modestbranding=1&hl=' + lang,
          title: pick(f.title), allow: 'autoplay; fullscreen; picture-in-picture; encrypted-media', allowfullscreen: '', referrerpolicy: 'strict-origin-when-cross-origin'
        }));
      } else if (isLocal && f.file) {
        var v = el('video', { controls: '', autoplay: '', playsinline: '', preload: 'metadata', src: media + encodeURIComponent(f.file), poster: posterUrl(f) });
        player.appendChild(v);
      } else {
        var p = posterUrl(f);
        player.appendChild(el('div', { 'class': 'film-unavailable' }, [p ? el('img', { src: p, alt: '' }) : null, el('span', { text: T.soon })]));
      }
    }
    function close() { if (dialog.open) dialog.close(); }
    dialog.addEventListener('close', function () {
      player.innerHTML = '';
      document.body.classList.remove('film-dialog-open');
      var back = root.querySelector('.film-card[data-id="' + (flat[current] && flat[current].id) + '"]');
      if (back) back.focus();
    });
    dialog.addEventListener('click', function (e) { if (e.target === dialog) close(); });
    closeBtn.addEventListener('click', close);
    prevBtn.addEventListener('click', function () { open(current - 1); });
    nextBtn.addEventListener('click', function () { open(current + 1); });
    dialog.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); open(current - 1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); open(current + 1); }
    });

    // deep link: films.html#film=<id>
    var m = /film=([\w-]+)/.exec(location.hash);
    if (m) { var idx = flat.findIndex(function (f) { return f.id === m[1]; }); if (idx >= 0) open(idx); }
  }
})();
