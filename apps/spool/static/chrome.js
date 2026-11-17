(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.reveal').forEach((el) => {
    if (reduce) { el.classList.add('is-in'); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { threshold: 0.15 });
    io.observe(el);
  });
  const vis = document.querySelector('.hero-visual');
  if (vis && !reduce) {
    window.addEventListener('pointermove', (e) => {
      const r = vis.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      vis.style.transform = `rotateY(${-8 + x * 6}deg) rotateX(${4 - y * 6}deg)`;
    }, { passive: true });
  }
})();
