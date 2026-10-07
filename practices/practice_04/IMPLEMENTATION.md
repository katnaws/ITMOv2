# Практика 4 — Study Tracker MCP

Все файлы реализации собраны в этой папке:

- `auto_check/` — skill с инструкциями проверки.
- `mcp/` — собственный трекер, клиент и проверки.
- `dashboard/` — React-интерфейс и HTTP-мост к MCP.
- `hooks/` — post-commit и его изолированная проверка.
- `scripts/` — запись OpenCode-демо, HTML-отчёт и упаковка.
- `logs/` — доказательства реальных вызовов и результаты проверок.
- `artifacts/` — архив сдачи.
- `AGENTS.md`, `runner.sh`, `reflection.md`, `SUBMISSION.md`, `report.html`, `HANDOFF.md` — правила, проверки и материалы сдачи.

В корне репозитория остаются только точки подключения: `AGENTS.md`,
`opencode.json`, `Makefile` и `.gitignore`. Исходное задание — `README.md`, презентации преподавателя находятся здесь же.

Все shell-команды выполняются из корня репозитория:

```sh
make p4-run
make p4-dashboard
make p4-pack
```

Перед первым запуском на новом компьютере:
`npm --prefix practices/practice_04/dashboard ci`.
Подробная инструкция — `practices/practice_04/HANDOFF.md`.

Записи OpenCode в logs сохранены в исходном виде: они сделаны до переноса
файлов и могут содержать прежние пути. Текущие проверки, конфигурация,
инструкция и архив используют новую структуру.
