// School picker shared by the home stage (showcase.js) and the films page (films.js).
// Two panes in one block: the selected school's details on the left (logo, full name, city,
// film count, one-line tagline), a compact name-only list on the right that drives it.
// Data comes from the `schools` section of assets/films.json; the rule that every school carries
// `logo` and `tagline` (en + fr) is enforced by tools/films-pages.py.
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

    var entries = [{ id: '', name: opts.T.all, meta: opts.T.films(opts.total), tag: opts.T.allTag, logo: null, count: opts.total }];
    opts.order.forEach(function (id) {
      var s = opts.schools[id] || { name: id };
      entries.push({
        id: id, name: s.name || id, logo: s.logo ? '/' + String(s.logo).replace(/^\/?/, '') : null,
        meta: [s.city, opts.T.films(opts.counts[id] || 0)].filter(Boolean).join(', '), tag: pick(s.tagline), count: opts.counts[id] || 0
      });
    });

    var logo = el('div', { 'class': 'schools-logo' });
    var name = el('h3', { 'class': 'schools-name' });
    var meta = el('p', { 'class': 'schools-meta' });
    var tag = el('p', { 'class': 'schools-tag' });
    var detail = el('div', { 'class': 'schools-detail', 'aria-live': 'polite' }, [logo, name, meta, tag]);

    var buttons = {};
    var list = el('ol', { 'class': 'schools-list', 'aria-label': opts.T.label });
    entries.forEach(function (e) {
      var b = el('button', { type: 'button', 'aria-pressed': 'false', 'data-school': e.id }, [
        el('span', { 'class': 'schools-list-name', text: e.name }), el('span', { 'class': 'schools-list-n', text: String(e.count) })
      ]);
      b.addEventListener('click', function () { set(e.id); if (opts.onSelect) opts.onSelect(e.id); });
      buttons[e.id] = b;
      list.appendChild(el('li', null, [b]));
    });
    list.addEventListener('keydown', function (e) {
      if (['ArrowDown', 'ArrowUp'].indexOf(e.key) < 0) return;
      var bs = [].slice.call(list.querySelectorAll('button')); var i = bs.indexOf(document.activeElement); if (i < 0) return;
      e.preventDefault(); var n = bs[i + (e.key === 'ArrowDown' ? 1 : -1)]; if (n) { n.focus(); n.click(); }
    });

    var wrap = el('div', { 'class': 'schools' }, [detail, list]);

    function set(id) {
      var e = entries.filter(function (x) { return x.id === id; })[0] || entries[0];
      logo.innerHTML = e.logo ? '<img src="' + e.logo + '" alt="" decoding="async">' : FILM_SVG;
      logo.classList.toggle('schools-logo-all', !e.logo);
      name.textContent = e.name; meta.textContent = e.meta; tag.textContent = e.tag || ''; tag.hidden = !e.tag;
      Object.keys(buttons).forEach(function (k) { buttons[k].setAttribute('aria-pressed', k === e.id ? 'true' : 'false'); });
    }
    set('');
    return { el: wrap, set: set };
  }

  window.RoTSchools = { render: render };
})();
