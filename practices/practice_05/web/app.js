(() => {
  // Elements
  const providerEl = document.getElementById('provider-status');
  const form = document.getElementById('review-form');
  const textarea = document.getElementById('diff-input');
  const previewBtn = document.getElementById('preview-btn');
  const sampleBtn = document.getElementById('sample-btn');
  const clearBtn = document.getElementById('clear-btn');
  const counterEl = document.getElementById('diff-counter');
  const warnEl = document.getElementById('diff-warn');
  const errorEl = document.getElementById('error');
  const loadingEl = document.getElementById('loading');
  const previewSection = document.getElementById('preview');
  const redactionsWrap = document.getElementById('redactions-wrap');
  const redactionsCountEl = document.getElementById('redactions-count');
  const redactedView = document.getElementById('redacted-view');
  const reviewBtn = document.getElementById('review-btn');
  const editBtn = document.getElementById('edit-btn');
  const resultSection = document.getElementById('result');
  const summaryEl = document.getElementById('summary');
  const risksSection = document.getElementById('risks-section');
  const risksEl = document.getElementById('risks');
  const checksSection = document.getElementById('checks-section');
  const checksEl = document.getElementById('checks');

  const LIMIT = 20000;
  const REQUEST_TIMEOUT_MS = 1000 * 100; // 100s client timeout (server ~90s)
  let currentRequestToken = 0; // request version to invalidate late responses
  let lastRedacted = '';
  let busy = false;
  let activeController = null;

  function countCodePoints(str) { return [...str].length; }
  function looksLikeDiff(str) {
    const lines = str.split(/\n/);
    return lines.some(l => l.startsWith('diff --git') || l.startsWith('+++ ') || l.startsWith('--- ') || l.startsWith('@@'));
  }
  function clearChildren(n){ while(n.firstChild) n.removeChild(n.firstChild); }
  function showError(msg){ errorEl.textContent = msg; errorEl.hidden = false; }
  function clearError(){ errorEl.textContent = ''; errorEl.hidden = true; }
  function resetResult(){
    resultSection.hidden = true;
    summaryEl.textContent = '';
    clearChildren(risksEl); risksSection.hidden = true;
    clearChildren(checksEl); checksSection.hidden = true;
  }
  function resetPreview(){
    previewSection.hidden = true;
    redactionsCountEl.textContent = '0';
    redactedView.textContent = '';
    reviewBtn.disabled = true;
    lastRedacted = '';
  }
  function setLoading(msg){ loadingEl.textContent = msg || 'Загрузка…'; loadingEl.hidden = false; }
  function clearLoading(){ loadingEl.textContent = ''; loadingEl.hidden = true; }

  // Provider status
  (async () => {
    try {
      const resp = await fetch('/api/provider', { headers: { 'Accept': 'application/json' } });
      if (resp.ok) {
        const j = await resp.json();
        const name = (j && j.provider) || '—';
        const model = (j && j.model) ? `, модель: ${j.model}` : '';
        const cfg = (j && j.configured) ? 'сконфигурирован' : 'не сконфигурирован';
        providerEl.textContent = `Провайдер: ${name}${model} (${cfg})`;
      } else {
        providerEl.textContent = 'Провайдер: недоступен';
      }
    } catch(_) {
      providerEl.textContent = 'Провайдер: ошибка запроса';
    }
  })();

  function updateCounter(){
    const value = textarea.value;
    const len = countCodePoints(value);
    counterEl.textContent = `${len} / ${LIMIT}`;
    const isEmpty = value.trim().length === 0;
    const over = len > LIMIT;
    // soft warn
    if (!isEmpty && !looksLikeDiff(value)) { warnEl.textContent = 'Текст не похож на unified diff. Его всё равно можно отправить.'; warnEl.hidden = false; }
    else { warnEl.textContent = ''; warnEl.hidden = true; }
    // limit error inline
    if (over) showError('Лимит 20000 символов превышен');
    else if (!isEmpty && errorEl.textContent === 'Лимит 20000 символов превышен') clearError();
    else if (isEmpty) clearError();
    previewBtn.disabled = busy || isEmpty || over || !value;
    reviewBtn.disabled = busy || !lastRedacted;
  }

  function invalidateState(){
    if (activeController) { try { activeController.abort(new DOMException('User edit/reset','AbortError')); } catch(_){} }
    activeController = null;
    busy = false;
    clearLoading();
    currentRequestToken++;
    resetPreview();
    resetResult();
    clearError();
  }

  function withTimeoutAbort(){
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(new DOMException('Timeout','AbortError')), REQUEST_TIMEOUT_MS);
    return { controller, cancel: () => clearTimeout(timer) };
  }

  async function doPreview(){
    if (busy) return;
    const value = textarea.value;
    const len = countCodePoints(value);
    if (value.trim().length === 0) { showError('Введите diff'); return; }
    if (len > LIMIT) { showError('Лимит 20000 символов превышен'); return; }
    const myToken = ++currentRequestToken;
    setLoading('Подготовка предпросмотра…');
    busy = true; updateCounter();
    let cancel = null; const { controller, cancel: c } = withTimeoutAbort(); cancel = c; activeController = controller;
    try {
      activeController = controller;
      const resp = await fetch('/api/preview', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify({ diff: value }), signal: controller.signal });
      const ct = resp.headers.get('Content-Type') || '';
      const data = ct.includes('application/json') ? await resp.json() : null;
      if (myToken !== currentRequestToken) { cancel && cancel(); return; }
      if (!resp.ok) {
        const code = data && data.error && data.error.code;
        if (code === 'CONTENT_TOO_LARGE') showError('Лимит 20000 символов превышен');
        else if (code === 'UNPROCESSABLE_CONTENT') showError('Невалидный diff. Проверьте формат.');
        else showError('Ошибка сервера при предпросмотре. Повторите позже.');
        return;
      }
      // success
      const red = (data && data.redacted) || '';
      const cnt = (data && typeof data.redactions_count === 'number') ? data.redactions_count : 0;
      lastRedacted = red;
      redactionsCountEl.textContent = String(cnt);
      // Highlight [REDACTED] segments with <mark> while keeping safe DOM (no innerHTML)
      clearChildren(redactedView);
      const parts = red.split('[REDACTED]');
      for (let i = 0; i < parts.length; i++) {
        redactedView.appendChild(document.createTextNode(parts[i]));
        if (i < parts.length - 1) {
          const m = document.createElement('mark'); m.textContent = '[REDACTED]'; redactedView.appendChild(m);
        }
      }
      previewSection.hidden = false;
      reviewBtn.disabled = red.length === 0;
      clearError();
    } catch (e) {
      if (myToken !== currentRequestToken) { /* ignore */ }
      else if (e && e.name === 'AbortError') showError('Таймаут или отмена запроса предпросмотра.');
      else showError('Сеть недоступна или ошибка соединения для предпросмотра.');
    } finally {
      try { cancel && cancel(); } catch(_){}
      if (myToken === currentRequestToken) { clearLoading(); busy = false; updateCounter(); }
      if (activeController === controller) activeController = null;
    }
  }

  async function doReview(){
    if (busy) return;
    if (!lastRedacted) { showError('Нет очищенного diff для отправки'); return; }
    const myToken = ++currentRequestToken;
    setLoading('Отправка на ревью…');
    busy = true; updateCounter();
    resetResult();
    let cancel = null; const { controller, cancel: c } = withTimeoutAbort(); cancel = c; activeController = controller;
    try {
      const resp = await fetch('/api/reviews', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify({ diff: lastRedacted }), signal: controller.signal });
      const ct = resp.headers.get('Content-Type') || '';
      const data = ct.includes('application/json') ? await resp.json() : null;
      if (myToken !== currentRequestToken) { cancel && cancel(); return; }
      if (!resp.ok) {
        const code = data && data.error && data.error.code;
        if (code === 'CONTENT_TOO_LARGE') showError('Лимит 20000 символов превышен');
        else if (code === 'UNPROCESSABLE_CONTENT') showError('Невалидный diff. Проверьте формат.');
        else if (code === 'PROVIDER_NOT_CONFIGURED') showError('Провайдер не сконфигурирован. Попробуйте позже.');
        else if (code === 'LLM_UPSTREAM_ERROR') showError('Сервис ревью временно недоступен. Повторите позже.');
        else showError('Ошибка сервера при ревью. Повторите позже.');
        return;
      }
      const { summary, risks = [], checks = [] } = data || {};
      resultSection.hidden = false;
      summaryEl.textContent = summary || 'Ревью выполнено';
      if (Array.isArray(risks) && risks.length > 0) {
        risksSection.hidden = false; clearChildren(risksEl);
        risks.slice(0,3).forEach(r => {
          const li = document.createElement('li');
          const parts = [];
          if (r.file) parts.push(`Файл: ${r.file}`);
          if (typeof r.line === 'number') parts.push(`Строка: ${r.line}`);
          if (r.risk) parts.push(`Риск: ${r.risk}`);
          if (r.evidence) parts.push(`Доказательство: ${r.evidence}`);
          li.textContent = parts.join(' • ');
          risksEl.appendChild(li);
        });
      }
      if (Array.isArray(checks) && checks.length > 0) {
        checksSection.hidden = false; clearChildren(checksEl);
        checks.forEach(c => { const li = document.createElement('li'); li.textContent = String(c); checksEl.appendChild(li); });
      }
      clearError();
    } catch (e) {
      if (myToken !== currentRequestToken) { /* ignore */ }
      else if (e && e.name === 'AbortError') showError('Таймаут или отмена запроса ревью.');
      else showError('Сеть недоступна или ошибка соединения для ревью.');
    } finally {
      try { cancel && cancel(); } catch(_){}
      if (myToken === currentRequestToken) { clearLoading(); busy = false; updateCounter(); }
      if (activeController === controller) activeController = null;
    }
  }

  function onClear(){
    if (!confirm('Очистить введенный diff и состояния?')) return;
    textarea.value = '';
    invalidateState();
    updateCounter();
    textarea.focus();
  }

  function loadSample(){
    const sample = [
      'diff --git a/example.py b/example.py',
      '--- /dev/null',
      '+++ b/example.py',
      '@@ -0,0 +1,8 @@',
      "+API_KEY='sk-DEMOONLY123'",
      '+def divide(a, b):',
      '+    return a / 0  # TODO: fix division by zero',
      '+',
      '+def build_query(user):',
      "+    return f\"SELECT * FROM users WHERE name = '{user}'\"  # potential SQL injection",
      '+',
      '+print(divide(10, 0))'
    ].join('\n');
    textarea.value = sample;
    invalidateState();
    updateCounter();
    textarea.focus();
  }

  // Events
  textarea.addEventListener('input', () => { invalidateState(); updateCounter(); });
  previewBtn.addEventListener('click', (ev) => { ev.preventDefault(); clearError(); resetResult(); doPreview(); });
  reviewBtn.addEventListener('click', (ev) => { ev.preventDefault(); clearError(); doReview(); });
  form.addEventListener('submit', (ev) => { ev.preventDefault(); });
  editBtn.addEventListener('click', () => { textarea.focus(); });
  clearBtn.addEventListener('click', onClear);
  sampleBtn.addEventListener('click', loadSample);

  // init
  updateCounter();
})();
