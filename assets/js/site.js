/* Anmay Defence — shared site behaviour */
(function () {
  var d = document;
  d.documentElement.classList.add('js');

  /* mobile nav */
  var toggle = d.querySelector('.nav-toggle');
  var mnav = d.getElementById('mobile-nav');
  if (toggle && mnav) {
    toggle.addEventListener('click', function () {
      var open = mnav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* scroll reveal */
  var reveals = [].slice.call(d.querySelectorAll('.reveal'));
  if ('IntersectionObserver' in window && reveals.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }

  /* year stamp */
  var y = d.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  /* ---------- gallery ---------- */
  var gallery = d.getElementById('gallery');
  if (!gallery) return;

  var items = [].slice.call(gallery.querySelectorAll('.gi'));
  var filters = [].slice.call(d.querySelectorAll('.filter'));
  var countEl = d.getElementById('gal-count');
  var visible = items.slice();

  function updateCount() {
    if (!countEl) return;
    countEl.textContent = visible.length + ' of ' + items.length + ' files';
  }

  filters.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var cat = btn.getAttribute('data-cat');
      filters.forEach(function (b) { b.classList.toggle('is-active', b === btn); });
      visible = [];
      items.forEach(function (it) {
        var show = cat === 'all' || it.getAttribute('data-cat') === cat;
        it.classList.toggle('is-hidden', !show);
        if (show) visible.push(it);
      });
      updateCount();
    });
  });
  updateCount();

  /* deep link: gallery.html?cat=strike-m */
  var wanted = new URLSearchParams(location.search).get('cat');
  if (wanted) {
    var match = filters.filter(function (b) { return b.getAttribute('data-cat') === wanted; })[0];
    if (match) match.click();
  }

  /* keyboard: open a tile with Enter or Space */
  gallery.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    var fig = e.target.closest('.gi');
    if (!fig) return;
    e.preventDefault();
    var i = visible.indexOf(fig);
    if (i > -1) show(i);
  });

  /* ---------- lightbox ---------- */
  var lb = d.getElementById('lb');
  if (!lb) return;
  var lbImg = lb.querySelector('.lb__img');
  var lbCap = lb.querySelector('.lb__cap');
  var lbClose = lb.querySelector('.lb__close');
  var current = -1;

  function show(i) {
    if (!visible.length) return;
    current = (i + visible.length) % visible.length;
    var it = visible[current];
    var img = it.querySelector('img');
    lbImg.src = it.getAttribute('data-full') || img.src;
    lbImg.alt = img.alt;
    lbCap.textContent = it.getAttribute('data-desc') || img.alt;
    lb.classList.add('open');
    d.body.style.overflow = 'hidden';
  }
  function close() {
    lb.classList.remove('open');
    d.body.style.overflow = '';
    current = -1;
  }

  gallery.addEventListener('click', function (e) {
    var fig = e.target.closest('.gi');
    if (!fig) return;
    var i = visible.indexOf(fig);
    if (i > -1) show(i);
  });
  lbClose.addEventListener('click', close);
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  lb.querySelector('.lb__prev').addEventListener('click', function (e) { e.stopPropagation(); show(current - 1); });
  lb.querySelector('.lb__next').addEventListener('click', function (e) { e.stopPropagation(); show(current + 1); });
  d.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(current - 1);
    if (e.key === 'ArrowRight') show(current + 1);
  });
})();
