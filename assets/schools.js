// School selector shared by the home stage (showcase.js) and the films page (films.js):
// one card per school with its logo, full name, city, film count and one-line tagline, plus an
// "all schools" card. Data comes from the `schools` section of assets/films.json; the rule that
// every school carries `logo` and `tagline` (en + fr) is enforced by tools/films-pages.py.
(function () {
  'use strict';
  var FILM_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 4v16M17 4v16M3 9h4M3 15h4M17 9h4M17 15h4"/></svg>';

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

  // opts: { schools, order: [ids present], counts: {id: n}, total, lang, T: {all, allTag, films(n), label}, onSelect(id) }
  function render(opts) {
    var lang = opts.lang === 'fr' ? 'fr' : 'en';
    function pick(v) { return (v && typeof v === 'object') ? (v[lang] || v.en || v.fr || '') : (v || ''); }
    var wrap = el('div', { 'class': 'schools', role: 'group', 'aria-label': opts.T.label });
    var cards = {};

    function card(id, logoHtml, name, meta, tag) {
      var b = el('button', { type: 'button', 'class': 'school-card', 'aria-pressed': 'false', 'data-school': id }, [
        el('span', { 'class': 'school-logo' + (id ? '' : ' school-logo-all'), html: logoHtml }),
        el('span', { 'class': 'school-name', text: name }),
        el('span', { 'class': 'school-meta', text: meta }),
        tag ? el('span', { 'class': 'school-tag', text: tag }) : null
      ]);
      b.addEventListener('click', function () { set(id); if (opts.onSelect) opts.onSelect(id); });
      cards[id] = b;
      return b;
    }

    wrap.appendChild(card('', FILM_SVG, opts.T.all, opts.T.films(opts.total), opts.T.allTag));
    opts.order.forEach(function (id) {
      var s = opts.schools[id] || { name: id };
      var logo = s.logo ? '<img src="/' + String(s.logo).replace(/^\/?/, '') + '" alt="" loading="lazy" decoding="async">' : '<span class="school-mono">' + (s.name || id).charAt(0) + '</span>';
      var meta = [s.city, opts.T.films(opts.counts[id] || 0)].filter(Boolean).join(', ');
      wrap.appendChild(card(id, logo, s.name || id, meta, pick(s.tagline)));
    });

    function set(id) {
      Object.keys(cards).forEach(function (k) { cards[k].setAttribute('aria-pressed', k === id ? 'true' : 'false'); });
      var c = cards[id]; if (c && c.scrollIntoView) c.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    }
    set('');
    return { el: wrap, set: set };
  }

  window.RoTSchools = { render: render };
})();
