(() => {
  const grid = document.querySelector('#machine-grid');
  const search = document.querySelector('#search');
  const tabs = [...document.querySelectorAll('[data-tier]')];
  const live = document.querySelector('.live');
  const liveCount = document.querySelector('#live-count');
  const checkButton = document.querySelector('#check-all');
  let data = [];
  let activeTier = 'all';

  const domainFor = (target) => {
    const hostsMode = location.hostname.endsWith('.test');
    return hostsMode ? target.hosts_url : target.domain_url;
  };

  const card = (target) => `
    <article class="machine" data-service="${target.service}" style="--machine-accent:${target.accent}">
      <header><span class="machine-id">${target.machine_id} / ${target.tier.toUpperCase()}</span><span class="machine-status"><i></i><b>unchecked</b></span></header>
      <h3>${target.product}</h3><p>${target.family} · ${target.stack}</p>
      <dl><div><dt>Layout</dt><dd>${target.layout}</dd></div><div><dt>Objectives</dt><dd>${target.accepted_objectives} accepted</dd></div></dl>
      <footer><span>${target.service}</span><a href="${domainFor(target)}">Open machine →</a></footer>
    </article>`;

  function render() {
    const query = search.value.trim().toLowerCase();
    const filtered = data.filter((target) => (activeTier === 'all' || target.tier === activeTier) &&
      [target.machine_id, target.service, target.product, target.family, target.stack, target.layout].join(' ').toLowerCase().includes(query));
    grid.innerHTML = filtered.length ? filtered.map(card).join('') : '<div class="empty">No machines match this view.</div>';
  }

  async function ping(target) {
    const element = grid.querySelector(`[data-service="${target.service}"]`);
    if (!element) return false;
    try {
      await fetch(domainFor(target) + '/', { mode: 'no-cors', cache: 'no-store', signal: AbortSignal.timeout(5000) });
      element.classList.add('reachable');
      element.querySelector('.machine-status b').textContent = 'reachable';
      return true;
    } catch (_) {
      element.classList.remove('reachable');
      element.querySelector('.machine-status b').textContent = 'offline';
      return false;
    }
  }

  async function checkAll() {
    checkButton.disabled = true;
    checkButton.textContent = 'Checking…';
    const visible = data.filter((target) => grid.querySelector(`[data-service="${target.service}"]`));
    const results = await Promise.all(visible.map(ping));
    const count = results.filter(Boolean).length;
    liveCount.textContent = `${count}/${visible.length} reachable`;
    live.classList.toggle('ready', count === visible.length && visible.length > 0);
    checkButton.disabled = false;
    checkButton.textContent = 'Check reachability';
  }

  fetch('/targets.json').then((response) => response.json()).then((payload) => {
    data = payload.targets;
    render();
    setTimeout(checkAll, 250);
  }).catch(() => { grid.innerHTML = '<div class="empty">Target data could not be loaded.</div>'; });

  search.addEventListener('input', render);
  tabs.forEach((tab) => tab.addEventListener('click', () => {
    tabs.forEach((item) => item.classList.remove('active'));
    tab.classList.add('active');
    activeTier = tab.dataset.tier;
    render();
  }));
  checkButton.addEventListener('click', checkAll);
})();
