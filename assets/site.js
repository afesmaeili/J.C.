(() => {
  const button = document.querySelector('.theme-toggle');
  function syncThemeButton() {
    if (!button) return;
    const dark = document.documentElement.dataset.theme === 'dark';
    button.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
    button.setAttribute('aria-pressed', String(dark));
    button.querySelector('span').textContent = dark ? 'Light' : 'Dark';
  }
  syncThemeButton();
  button?.addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('physics-journal-theme', theme); } catch {}
    syncThemeButton();
  });
  document.querySelector('[data-print]')?.addEventListener('click', () => window.print());
  const input = document.getElementById('search-input');
  if (!input) return;
  const data = window.JOURNAL_INDEX || [];
  const output = document.getElementById('search-results');
  const status = document.getElementById('search-status');
  const params = new URLSearchParams(location.search);
  let topic = params.get('topic') || 'All topics';
  const filters = [...document.querySelectorAll('[data-topic]')];
  if (!filters.some(b => b.dataset.topic === topic)) topic = 'All topics';
  input.value = params.get('q') || '';
  const normalize = text => text.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  function el(tag, className, text) { const n = document.createElement(tag); n.className = className; if (text) n.textContent = text; return n; }
  function render(updateUrl = true) {
    const terms = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
    const matches = data.filter(p => (topic === 'All topics' || p.tags.includes(topic)) && terms.every(t => normalize(p.searchText).includes(t)));
    filters.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.topic === topic)));
    output.replaceChildren();
    status.textContent = `${matches.length} ${matches.length === 1 ? 'paper' : 'papers'}${topic === 'All topics' ? '' : ' · ' + topic}`;
    for (const p of matches) {
      const article = el('article', 'search-result');
      article.append(el('div', 'paper-label', p.label));
      const heading = el('h2', ''); const link = el('a', '', p.title); link.href = p.path; heading.append(link); article.append(heading);
      article.append(el('p', '', p.teaser));
      article.append(el('div', 'meta', `${p.authors} · arXiv:${p.arxiv}`));
      const meta = el('div', 'meta', `Report: ${p.reportDate} · ${p.tags.join(' / ')}`); article.append(meta); output.append(article);
    }
    if (!matches.length) {
      const box = el('div', 'empty'); box.append(el('h2', '', 'No matching papers yet'));
      box.append(el('p', '', 'Try a different phrase or choose another topic. Try a paper title, author, arXiv ID, or date.'));
      const reset = el('button', 'button secondary', 'Clear search and filters'); reset.type = 'button'; reset.addEventListener('click', () => { input.value = ''; topic = 'All topics'; render(); input.focus(); }); box.append(reset); output.append(box);
    }
    if (updateUrl) {
      const next = new URLSearchParams(); if (input.value.trim()) next.set('q', input.value.trim()); if (topic !== 'All topics') next.set('topic', topic);
      try { history.replaceState(null, '', location.pathname + (next.size ? '?' + next : '')); } catch {}
    }
  }
  input.addEventListener('input', () => render());
  filters.forEach(b => b.addEventListener('click', () => { topic = b.dataset.topic; render(); }));
  render(false);
})();
