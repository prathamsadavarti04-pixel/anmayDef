/* Anmay Defence — shared behaviour: mobile nav, reveal on scroll, gallery filter,
   lightbox, contact form stub. No dependencies. */
(function () {
  var d = document;
  d.documentElement.classList.add('js');

  /* mobile navigation ------------------------------------------------------ */
  var btn = d.querySelector('.menu-btn');
  var mnav = d.getElementById('mobile-nav');
  if (btn && mnav) {
    btn.addEventListener('click', function () {
      var open = mnav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? 'Close' : 'Menu';
    });
  }

  /* reveal on scroll ------------------------------------------------------- */
  var rv = [].slice.call(d.querySelectorAll('.rv'));
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    rv.forEach(function (el) { io.observe(el); });
  } else {
    rv.forEach(function (el) { el.classList.add('in'); });
  }

  /* footer year ------------------------------------------------------------ */
  var y = d.getElementById('year');
  if (y) { y.textContent = new Date().getFullYear(); }

  /* gallery filter --------------------------------------------------------- */
  var filters = d.getElementById('filters');
  var gallery = d.getElementById('gallery');
  if (filters && gallery) {
    var cards = [].slice.call(gallery.querySelectorAll('figure'));
    filters.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (!b) return;
      var cat = b.dataset.cat;
      [].forEach.call(filters.querySelectorAll('button'), function (x) {
        x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
      });
      cards.forEach(function (c) {
        var show = cat === 'all' || c.dataset.cat === cat;
        c.classList.toggle('hidden', !show);
      });
      var count = d.getElementById('count');
      if (count) {
        var n = cards.filter(function (c) { return !c.classList.contains('hidden'); }).length;
        count.textContent = n + ' frames';
      }
    });
  }

  /* lightbox --------------------------------------------------------------- */
  var lb = d.getElementById('lb');
  if (lb && gallery) {
    var lbImg = lb.querySelector('img');
    var lbCap = lb.querySelector('figcaption');
    var close = function () { lb.classList.remove('open'); d.body.style.overflow = ''; };
    gallery.addEventListener('click', function (ev) {
      var fig = ev.target.closest('figure');
      if (!fig) return;
      var a = fig.querySelector('a');
      if (!a) return;
      ev.preventDefault();
      lbImg.src = a.getAttribute('href');
      lbImg.alt = fig.querySelector('img').alt;
      lbCap.textContent = fig.dataset.caption || fig.querySelector('img').alt;
      lb.classList.add('open');
      d.body.style.overflow = 'hidden';
    });
    lb.addEventListener('click', function (ev) {
      if (ev.target === lb || ev.target.tagName === 'BUTTON') close();
    });
    d.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') close(); });
  }

  /* contact form stub ------------------------------------------------------ */
  var form = d.getElementById('briefing-form');
  if (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var out = d.getElementById('form-status');
      out.hidden = false;
      out.textContent = 'This form is a front-end stub: no endpoint is configured yet. ' +
        'Wire it to your form service (or a mailto: action) in contact.html before publishing.';
    });
  }
})();
