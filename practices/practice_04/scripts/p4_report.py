"""Render a self-contained HTML report from verified local evidence."""
from datetime import datetime
import html
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
PRACTICE = ROOT / "practices/practice_04"


def render():
    evidence = json.loads((PRACTICE / "logs/opencode_evidence.json").read_text())
    hook = json.loads((PRACTICE / "logs/hook_demo.json").read_text())
    assert evidence["ok"] and hook["ok"], "Evidence incomplete"
    calls = "\n".join(
        f'<tr><td><code>{html.escape(part["tool"])}</code></td><td>{html.escape(part["state"]["status"])}</td>'
        f'<td><code>{html.escape(json.dumps(part["state"].get("input", {}), ensure_ascii=False))}</code></td></tr>'
        for part in evidence["tool_calls"])
    author_line = next(line for line in (PRACTICE / "SUBMISSION.md").read_text().splitlines() if line.startswith("Автор:"))
    author = html.escape(author_line.replace("**", ""))
    date = datetime.now(ZoneInfo("Europe/Moscow")).strftime("%d.%m.%Y")
    report = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Практика 4 — Study Tracker MCP</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f5f6fa;color:#25283c;font:16px/1.7 system-ui,sans-serif}}
header{{background:#191c32;color:white;padding:46px max(24px,calc((100vw - 1050px)/2))}}header small{{color:#b4a5ed;letter-spacing:2px}}
h1{{font-size:38px;line-height:1.2;margin:15px 0}}header p{{color:#c0c2d4}}main{{max-width:1100px;padding:30px 25px 55px;margin:auto}}
section{{margin:0 0 26px;padding:26px 30px;background:white;border:1px solid #e4e6ef;border-radius:12px}}
h2{{font-size:23px;margin:0 0 16px}}h3{{font-size:18px;margin-bottom:8px}}p{{margin:10px 0}}a{{color:#6848c5}}code{{font:13px/1.6 ui-monospace,monospace;overflow-wrap:anywhere}}
.pill{{display:inline-block;background:#e8f4ec;color:#427459;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:700}}
.facts{{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}}.facts span{{padding:5px 12px;border-radius:7px;background:#2b2e47;color:#d6d8e8;font-size:13px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{padding:12px 10px;border-bottom:1px solid #ececf3;text-align:left;vertical-align:top}}th{{background:#f8f7fc}}.scroll{{overflow:auto}}
.architecture{{background:#f3f0fb;padding:18px;border-radius:8px;text-align:center;color:#6d53a8;font-weight:700}}
.note{{padding:15px;border-left:3px solid #ae96ec;background:#f8f6fc;color:#6e6387;font-size:14px}}
pre{{overflow:auto;padding:18px;background:#1e2237;color:#e0dfed;border-radius:8px;font-size:13px;white-space:pre-wrap}}img{{width:100%;border:1px solid #e7e8ef;border-radius:10px}}details summary{{cursor:pointer;font-weight:700}}footer{{text-align:center;color:#8f91a5;font-size:13px}}li{{margin:7px 0}}
@media(max-width:650px){{h1{{font-size:29px}}section{{padding:20px}}main{{padding:20px 14px}}table{{font-size:12px}}}}
@media print{{body{{background:white}}header{{padding:24px;background:white;color:#25283c}}header p{{color:#555}}main{{padding:0}}section{{break-inside:avoid;border:none;padding:16px 0}}a{{color:inherit}}details{{display:block}}.preview{{display:none}}}}
</style></head><body>
<header><small>ПРАКТИКА 04 · ТЕХНОЛОГИИ ИИ В РАЗРАБОТКЕ ПО</small><h1>Study Tracker MCP</h1>
<p>Собственный инструмент для заданий, дедлайнов и прогресса</p><p>{author}</p>
<div class="facts"><span>Python + SQLite</span><span>MCP stdio</span><span>React + Vite</span><span>OpenCode</span></div></header>
<main><section><span class="pill">Подтверждения собраны</span><h2>Что сделано</h2>
<p>Учебный трекер предоставляет четыре MCP-инструмента: добавить задание, показать список, изменить статус и получить сводку. Данные сохраняются между запусками.</p>
<div class="architecture">React → HTTP-мост → MCP tools/call → SQLite</div>
<p>Агент OpenCode и дашборд используют один MCP. Деморежим хранит примеры отдельно от личных заданий.</p>
<p><a href="SUBMISSION.md">Подробный отчёт</a> · <a href="HANDOFF.md">Инструкция по сдаче и защите</a> · <a href="reflection.md">Рефлексия</a></p></section>
<section><h2>Критерии задания</h2><div class="scroll"><table><thead><tr><th>Критерий</th><th>Реализация и доказательство</th></tr></thead><tbody>
<tr><td>Среда — 5 баллов</td><td>AGENTS.md, skill, MCP, hook и объяснение их назначения. <a href="logs/opencode_evidence.json">Вызовы агента</a>, <a href="logs/hook_demo.json">автозапуск hook</a>.</td></tr>
<tr><td>Skill — 2 балла</td><td>Процедурные инструкции авто-проверки. Агент загрузил <code>auto_check</code> через tool skill и выполнил runner.</td></tr>
<tr><td>Собственный MCP — 2 балла</td><td>Четыре полезных инструмента, реальный успешный вызов и ошибка на дате 2026-02-30. <a href="logs/study_tracker_demo.json">Интеграционное демо</a>.</td></tr>
<tr><td>Рефлексия — 1 балл</td><td><a href="reflection.md">Черновик по событиям работы</a>; студенту осталось проверить личные формулировки.</td></tr>
</tbody></table></div><p class="note">Таблица сопоставляет материалы с критериями и не гарантирует оценку. Дашборд — дополнительная наглядная демонстрация.</p></section>
<section><h2>Зачем нужны подключения</h2><ul>
<li><strong>AGENTS.md:</strong> правила запуска проверок и сохранения результатов.</li>
<li><strong>Skill:</strong> повторяемая инструкция агенту вместо ручного составления порядка действий.</li>
<li><strong>Study Tracker MCP:</strong> работа с учебными заданиями через инструменты с описанными аргументами.</li>
<li><strong>Runner и hook:</strong> проверка после изменений и автоматический запуск после коммита.</li></ul></section>
<section><h2>Реальные действия OpenCode</h2><div class="scroll"><table><thead><tr><th>Инструмент</th><th>Статус</th><th>Аргументы</th></tr></thead><tbody>{calls}</tbody></table></div>
<p><a href="logs/opencode_evidence.json">Компактное доказательство</a> · <a href="logs/opencode_session.jsonl">Исходный поток событий</a></p>
<p class="note">CLI ограничен 90 секундами и остановлен до итогового текстового ответа. Перечисленные вызовы инструментов успели завершиться. Ошибка add_task — ожидаемый результат проверки неверной даты.</p></section>
<section><h2>Автоматическая проверка</h2><p>Проверены сохранение между процессами, фильтры, сроки, прогресс, неверный ввод, MCP-мост и сборка React.</p>
<p><a href="logs/runner.log">Runner</a> · <a href="logs/dashboard_check.json">MCP-мост</a> · <a href="logs/dashboard_http_check.json">HTTP-проверки</a> · <a href="logs/changes.diff">Diff</a></p>
<h3>Git hook</h3><p>В изолированном временном Git-репозитории создан настоящий коммит. Post-commit автоматически выполнил runner. В основном репозитории демонстрационный коммит не создавался.</p>
<details><summary>Вывод коммита и hook</summary><pre>{html.escape(hook['commit_output'])}</pre></details>
<p class="note">В hook-демо npm-зависимости не устанавливались. React-сборка подтверждена отдельно основным runner.log.</p></section>
<section class="preview"><h2>Дашборд</h2><p>Добавление задания, смена статуса, поиск, дедлайны и история реальных MCP-запросов.</p><details><summary>Скриншот проверки интерфейса</summary><p><img src="logs/dashboard-preview.jpg" alt="React-дашборд Study Space с заданиями и прогрессом"></p></details></section>
<section><h2>Запуск из корня репозитория</h2><pre>npm --prefix practices/practice_04/dashboard ci
make p4-run
make p4-dashboard</pre><p>Открыть <a href="http://127.0.0.1:8765/?mode=demo">деморежим дашборда</a>.</p><p>Для подготовки архива: <code>make p4-pack</code>. Подробные шаги и сценарий защиты — <a href="HANDOFF.md">HANDOFF.md</a>.</p></section>
<footer>Собрано {date}, Europe/Moscow · Данные и секреты пользователя не включены в пакет</footer></main></body></html>'''
    (PRACTICE / "report.html").write_text(report)
    print("HTML report: practices/practice_04/report.html")


if __name__ == "__main__":
    render()
