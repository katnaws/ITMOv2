import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, BookOpen, CalendarDays, Check, CheckCheck, ChevronDown, Circle, Clock3, Code2, FlaskConical, LayoutDashboard, ListTodo, LoaderCircle, Plus, RefreshCw, Search, Sparkles, TriangleAlert, X } from 'lucide-react';
import './style.css';

const STATUS = { todo: 'К выполнению', in_progress: 'В работе', done: 'Готово' };
const LABELS = { add_task: 'Добавление задания', update_task_status: 'Изменение статуса', list_tasks: 'Список заданий', study_dashboard: 'Сводка прогресса' };
const dateLabel = value => new Date(`${value}T12:00:00`).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
const courseColors = ['purple', 'blue', 'orange', 'teal'];
const courseWord = count => count % 10 === 1 && count % 100 !== 11 ? 'курс' : count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 12 || count % 100 > 14) ? 'курса' : 'курсов';

async function api(path, options = {}) {
  const response = await fetch(path, { ...options, headers: { 'Content-Type': 'application/json', ...options.headers } });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || result.content?.[0]?.text || 'Не удалось выполнить запрос');
  return result;
}

function App() {
  const [mode, setMode] = useState(new URLSearchParams(location.search).get('mode') === 'demo' ? 'demo' : 'real');
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [view, setView] = useState('overview');
  const [status, setStatus] = useState('all');
  const [course, setCourse] = useState('all');
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const generation = useRef(0);

  async function refresh(currentMode = mode, quiet = false) {
    const ticket = ++generation.current;
    if (!quiet) setLoading(true);
    setError('');
    try {
      const result = await api(`/api/state?mode=${currentMode}`);
      if (ticket === generation.current) setState(result);
    } catch (e) {
      if (ticket === generation.current) setError(e.message);
    } finally {
      if (ticket === generation.current) setLoading(false);
    }
  }

  useEffect(() => {
    setState(null);
    setCourse('all');
    setStatus('all');
    setSearch('');
    setNotice('');
    refresh(mode);
    const interval = setInterval(() => { if (document.visibilityState === 'visible') refresh(mode, true); }, 30000);
    return () => { clearInterval(interval); generation.current++; };
  }, [mode]);

  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(() => setNotice(''), 4500);
    return () => clearTimeout(timer);
  }, [notice]);

  async function callTool(name, args) {
    return api(`/api/tools/${name}?mode=${mode}`, { method: 'POST', body: JSON.stringify(args) });
  }

  async function changeStatus(task, nextStatus) {
    setBusy(true);
    setError('');
    try {
      await callTool('update_task_status', { task_id: task.id, status: nextStatus });
      await refresh(mode, true);
      setNotice(nextStatus === 'done' ? 'Задание выполнено. Отличная работа!' : 'Статус задания обновлён');
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }

  const tasks = state?.tasks || [];
  const dashboard = state?.dashboard;
  const courses = [...new Set(tasks.map(t => t.course))];
  const colorFor = name => courseColors[Math.max(0, courses.indexOf(name)) % courseColors.length];
  const filtered = tasks.filter(t =>
    (status === 'all' || t.status === status) && (course === 'all' || t.course === course) &&
    `${t.title} ${t.course}`.toLowerCase().includes(search.toLowerCase()) &&
    (view !== 'deadlines' || t.status !== 'done')
  );
  const nearest = tasks.filter(t => t.status !== 'done').slice(0, 4);

  function switchMode(value) {
    const url = new URL(location.href);
    value === 'demo' ? url.searchParams.set('mode', 'demo') : url.searchParams.delete('mode');
    history.replaceState({}, '', url);
    setMode(value);
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <a href="/" className="brand"><span className="brand-icon"><BookOpen size={23} /></span><span>study<span className="brand-light">space</span><small>ЛИЧНЫЙ КАБИНЕТ</small></span></a>
      <div className="workspace"><span className="workspace-avatar">S</span><div>Моя учёба<small>Этот семестр</small></div></div>
      <p className="nav-caption">ПРОСТРАНСТВО</p>
      <nav aria-label="Основная навигация">
        <button className={view === 'overview' ? 'nav-link active' : 'nav-link'} onClick={() => { setView('overview'); setStatus('all'); }}><LayoutDashboard size={19} />Обзор</button>
        <button className={view === 'tasks' ? 'nav-link active' : 'nav-link'} onClick={() => { setView('tasks'); setStatus('all'); }}><ListTodo size={19} />Все задания<span className="nav-count">{tasks.length}</span></button>
        <button className={view === 'deadlines' ? 'nav-link active' : 'nav-link'} onClick={() => { setView('deadlines'); setStatus('all'); }}><CalendarDays size={19} />Дедлайны</button>
      </nav>
      <div className="sidebar-bottom"><div className="connection"><span className={error ? 'connection-dot failed' : 'connection-dot'} />{loading ? 'Подключение…' : error ? 'Проверьте соединение' : 'MCP подключён'}</div><button className="history-link" onClick={() => setShowHistory(true)}><Code2 size={17} />История MCP-вызовов</button><div className="profile"><span className="profile-avatar">Я</span><div>Моё пространство<small>Study Tracker</small></div></div></div>
    </aside>

    <main>
      <div className="topbar"><div className="breadcrumb">Моя учёба<span>/</span><strong>{view === 'overview' ? 'Обзор' : view === 'tasks' ? 'Все задания' : 'Дедлайны'}</strong></div><div className="mode-switch" aria-label="Режим данных"><button disabled={busy} className={mode === 'real' ? 'selected' : ''} onClick={() => switchMode('real')}>Мои задания</button><button disabled={busy} className={mode === 'demo' ? 'selected' : ''} onClick={() => switchMode('demo')}><FlaskConical size={15} />Демо</button></div></div>
      <div className="page-content">
        <header className="page-heading"><div><div className="eyebrow">ТВОЙ УЧЕБНЫЙ РИТМ</div><h1>{view === 'overview' ? 'Всё по плану.' : view === 'tasks' ? 'Мои задания' : 'Ближайшие дедлайны'}</h1><p>{dashboard ? new Date(`${dashboard.as_of}T12:00:00`).toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' }) : 'Загружаем задания…'}<span className="heading-dot">·</span>Этот семестр</p></div><button className="button primary" disabled={loading || busy || !state} onClick={() => setShowForm(true)}><Plus size={19} />Добавить задание</button></header>
        {mode === 'demo' && <div className="demo-banner"><FlaskConical size={17} /><span>Деморежим: можно попробовать всё. Ваши задания хранятся отдельно.</span></div>}
        {error && <div className="error-banner" role="alert"><TriangleAlert size={18} /><span>{error}</span><button onClick={() => refresh()}>Повторить</button></div>}
        <section className="stats-grid" aria-label="Сводка заданий">
          <Stat icon={ListTodo} color="purple" label="Всего заданий" value={dashboard?.total ?? '—'} note={`${courses.length} ${courseWord(courses.length)} в пространстве`} />
          <Stat icon={Clock3} color="blue" label="В работе" value={dashboard?.by_status.in_progress ?? '—'} note="Шаг за шагом к результату" />
          <Stat icon={CheckCheck} color="teal" label="Выполнено" value={dashboard?.by_status.done ?? '—'} note={dashboard?.total ? `${dashboard.progress_percent}% от всех заданий` : 'Здесь будут ваши успехи'} />
          <Stat icon={TriangleAlert} color="orange" label="Просрочено" value={dashboard?.overdue.length ?? '—'} note={dashboard?.overdue.length ? 'Стоит уделить внимание' : 'Всё вовремя'} />
        </section>

        <div className="content-grid">
          <section className="panel tasks-panel">
            <div className="panel-heading"><div><h2>{view === 'deadlines' ? 'Незавершённые задания' : 'Задания'}<span className="count-pill">{tasks.length}</span></h2><p>Маленькие шаги. Большие результаты.</p></div><button className="icon-button" aria-label="Обновить задания" disabled={loading || busy} onClick={() => refresh()}><RefreshCw size={18} className={loading ? 'spin' : ''} /></button></div>
            <div className="task-tabs" role="group" aria-label="Фильтр по статусу">{[['all', 'Все'], ...Object.entries(STATUS)].map(([key, label]) => <button key={key} onClick={() => setStatus(key)} className={status === key ? 'active' : ''}>{label}{key === 'all' && <span>{tasks.length}</span>}</button>)}</div>
            <div className="filters"><label className="search-field"><Search size={17} /><input aria-label="Поиск задания" placeholder="Найти задание…" value={search} onChange={e => setSearch(e.target.value)} /></label><label className="course-filter"><BookOpen size={16} /><select aria-label="Фильтр по курсу" value={course} onChange={e => setCourse(e.target.value)}><option value="all">Все курсы</option>{courses.map(c => <option key={c}>{c}</option>)}</select><ChevronDown size={14} /></label></div>
            <div className="task-table-heading"><span>ЗАДАНИЕ</span><span>ДЕДЛАЙН</span><span>СТАТУС</span></div>
            <div className="task-list" aria-busy={loading}>
              {loading && !state ? <div className="empty-state"><LoaderCircle className="spin" size={28} /><h3>Загружаем задания</h3></div> : filtered.length ? filtered.map(task => <div key={task.id} className={`task-row ${task.status === 'done' ? 'completed' : ''}`}>
                <div className="task-info"><button className={`task-check ${task.status === 'done' ? 'checked' : ''}`} aria-label={`${task.status === 'done' ? 'Вернуть в задания' : 'Выполнить'}: ${task.title}`} disabled={busy} onClick={() => changeStatus(task, task.status === 'done' ? 'todo' : 'done')}>{task.status === 'done' && <Check size={14} />}</button><div><div className="task-title">{task.title}</div><span className={`course-label ${colorFor(task.course)}`}><span />{task.course}</span></div></div>
                <div className={`task-date ${task.overdue ? 'late' : ''}`}><CalendarDays size={14} /><div>{dateLabel(task.deadline)}<small>{task.status === 'done' ? 'Завершено' : task.days_left < 0 ? `${Math.abs(task.days_left)} дн. назад` : task.days_left === 0 ? 'Сегодня' : task.days_left === 1 ? 'Завтра' : `Через ${task.days_left} дн.`}</small></div></div>
                <label className={`status-select ${task.status}`}><span className="status-symbol">{task.status === 'done' ? <Check size={13} /> : task.status === 'in_progress' ? <Clock3 size={13} /> : <Circle size={9} />}</span><select aria-label={`Статус: ${task.title}`} value={task.status} disabled={busy} onChange={e => changeStatus(task, e.target.value)}>{Object.entries(STATUS).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select><ChevronDown size={12} /></label>
              </div>) : <div className="empty-state"><span className="empty-icon"><BookOpen size={28} /></span><h3>{tasks.length ? 'Ничего не найдено' : 'Начнём с первого задания'}</h3><p>{tasks.length ? 'Попробуйте изменить поиск или фильтры.' : 'Добавьте задание — и оно появится здесь.'}</p>{!tasks.length && <button className="button secondary" onClick={() => setShowForm(true)}><Plus size={16} />Добавить задание</button>}</div>}
            </div>
            <div className="table-footer"><span>Показано {filtered.length} из {tasks.length} заданий</span><span><RefreshCw size={12} />Обновление каждые 30 сек.</span></div>
          </section>

          <aside className="right-column">
            <section className="panel progress-panel"><div className="panel-heading"><h2>Твой прогресс</h2><Sparkles size={19} className="purple-text" /></div><div className="progress-ring" style={{ '--progress': `${dashboard?.progress_percent || 0}%` }}><div><strong>{dashboard?.progress_percent || 0}<span>%</span></strong><small>выполнено</small></div></div><p className="progress-caption">{dashboard?.by_status.done || 0} из {tasks.length} заданий позади</p><div className="progress-legend">{Object.entries(STATUS).map(([key, label]) => <div key={key}><span><i className={key} />{label}</span><strong>{dashboard?.by_status[key] || 0}</strong></div>)}</div></section>
            <section className="panel deadlines-panel"><div className="panel-heading"><h2>На горизонте</h2><CalendarDays size={19} className="muted" /></div>{nearest.length ? nearest.map(task => <div className="deadline-item" key={task.id}><div className={`date-tile ${task.overdue ? 'late' : ''}`}><strong>{new Date(`${task.deadline}T12:00:00`).getDate()}</strong><small>{new Date(`${task.deadline}T12:00:00`).toLocaleDateString('ru-RU', { month: 'short' }).replace('.', '')}</small></div><div><h3>{task.title}</h3><p>{task.overdue ? 'Срок прошёл' : task.days_left === 0 ? 'Сегодня' : task.days_left === 1 ? 'Завтра' : `Через ${task.days_left} дн.`}</p></div></div>) : <p className="quiet-empty">Незавершённых заданий пока нет.</p>}</section>
            <div className="focus-card"><span className="focus-icon"><Activity size={20} /></span><div><h3>В своём темпе</h3><p>{dashboard?.next_task ? `Следующий шаг — «${dashboard.next_task.title}».` : 'Одно небольшое задание — уже начало.'}</p></div></div>
          </aside>
        </div>
        <footer className="page-footer"><button className="footer-history" onClick={() => setShowHistory(true)}><Code2 size={13} />История MCP</button><span>Дедлайны по московскому времени</span></footer>
      </div>
    </main>
    {notice && <div className="toast" role="status"><CheckCheck size={18} />{notice}</div>}
    {showForm && <TaskForm mode={mode} courses={courses} onClose={() => setShowForm(false)} onSubmit={async args => { setBusy(true); try { await callTool('add_task', args); setShowForm(false); await refresh(mode, true); setNotice('Задание добавлено'); } finally { setBusy(false); } }} />}
    {showHistory && <History history={state?.history || []} mode={mode} onClose={() => setShowHistory(false)} />}
  </div>;
}

function Stat({ icon: Icon, color, label, value, note }) {
  return <article className="stat-card"><div className="stat-top"><span>{label}</span><span className={`stat-icon ${color}`}><Icon size={19} /></span></div><strong>{value}</strong><p>{note}</p></article>;
}

function Modal({ title, onClose, children, className = '' }) {
  const ref = useRef(null);
  useEffect(() => {
    const dialog = ref.current;
    dialog.showModal();
    return () => dialog.close();
  }, []);
  return <dialog ref={ref} className={`modal ${className}`} onCancel={e => { e.preventDefault(); onClose(); }} onClick={e => { if (e.target === ref.current) onClose(); }}><div className="modal-header"><h2>{title}</h2><button className="icon-button" onClick={onClose} aria-label="Закрыть"><X size={20} /></button></div>{children}</dialog>;
}

function TaskForm({ mode, courses, onClose, onSubmit }) {
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  return <Modal title="Новое задание" onClose={() => { if (!saving) onClose(); }}><p className="modal-description">{mode === 'demo' ? 'Задание будет добавлено в демопространство.' : 'Что нужно сделать и к какому сроку?'}</p><form onSubmit={async e => { e.preventDefault(); const data = new FormData(e.currentTarget); setSaving(true); setError(''); try { await onSubmit(Object.fromEntries(data)); } catch (err) { setError(err.message); } finally { setSaving(false); } }}><label>Название задания<input autoFocus name="title" required maxLength={500} placeholder="Например, подготовить защиту" /></label><label>Курс<input name="course" list="course-list" required maxLength={500} placeholder="Название предмета" /><datalist id="course-list">{courses.map(c => <option key={c} value={c} />)}</datalist></label><label>Дедлайн<input name="deadline" type="date" required /></label>{error && <p className="form-error" role="alert">{error}</p>}<div className="form-actions"><button type="button" className="button secondary" disabled={saving} onClick={onClose}>Отмена</button><button className="button primary" disabled={saving}>{saving ? <LoaderCircle size={17} className="spin" /> : <Plus size={17} />}{saving ? 'Сохраняем…' : 'Добавить задание'}</button></div></form></Modal>;
}

function History({ history, mode, onClose }) {
  return <Modal title="История MCP-вызовов" className="history-modal" onClose={onClose}><p className="modal-description">{mode === 'demo' ? 'Демопространство' : 'Мои задания'} · браузер → backend → MCP → SQLite</p><div className="history-list">{[...history].reverse().map((entry, index) => <details key={`${entry.time}-${index}`}><summary><span className={`history-status ${entry.result.isError ? 'failed' : ''}`}>{entry.result.isError ? <X size={14} /> : <Check size={14} />}</span><div><strong>{LABELS[entry.tool]}</strong><code>{entry.tool}</code></div><time>{new Date(entry.time).toLocaleTimeString('ru-RU')}</time><ChevronDown size={15} /></summary><pre>{JSON.stringify({ arguments: entry.arguments, result: entry.result }, null, 2)}</pre></details>)}{!history.length && <p>Вызовов пока нет.</p>}</div></Modal>;
}

createRoot(document.getElementById('root')).render(<App />);
