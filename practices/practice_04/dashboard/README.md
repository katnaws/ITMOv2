# Study Space — React-дашборд для собственного MCP

React + Vite, Python HTTP backend и существующий `study_tracker` MCP.
Backend запускает MCP-сервер отдельным процессом, выполняет `initialize` и
`tools/call`. SQL и бизнес-логика остаются в MCP; прямого доступа backend к БД нет.

## Быстрый запуск из корня репозитория

```sh
npm --prefix practices/practice_04/dashboard ci
make p4-dashboard
```

Откройте http://127.0.0.1:8765. Демонстрация с примерами:
http://127.0.0.1:8765/?mode=demo.

Режим «Мои задания» использует ту же SQLite-базу, что и MCP в OpenCode.
«Демо» использует отдельную временную базу: примеры добавляются через MCP,
изменения сохраняются до остановки dashboard-сервера. Реальные задания
не затрагиваются. Демоданные сбрасываются при перезапуске backend.

Можно добавлять задания, выбирать статус, отмечать выполнение, искать по
названию и фильтровать по курсу. Сводка и список обновляются после действий,
по кнопке и каждые 30 секунд, пока вкладка видима.

«История MCP-вызовов» показывает последние запросы и ответы текущего запуска,
включая аргументы и `isError`. Полный журнал вызовов dashboard записывается
в `practices/practice_04/mcp/study_tracker/data/dashboard-calls.jsonl` (локальные данные, вне Git).

## Разработка

Два терминала, оба из корня репозитория:

```sh
python3 practices/practice_04/dashboard/server.py
```

```sh
npm --prefix practices/practice_04/dashboard run dev
```

Vite открывается на http://127.0.0.1:5173 и проксирует `/api` к Python.
Для проверки: `python3 practices/practice_04/dashboard/check.py`, для сборки:
`npm --prefix practices/practice_04/dashboard run build`. Требования: Node.js 22.12+ и Python 3.9+.

## Что показать на защите

1. `opencode mcp list` — сервер подключён агенту.
2. Открыть деморежим, добавить задание и поменять статус.
3. Открыть историю вызовов и показать `add_task`, `update_task_status`, `study_dashboard`.
4. Запустить `make p4-run`: логи содержат успешные вызовы и ошибки.
5. В реальном режиме добавить задание через агента и обновить dashboard:
   одна SQLite-база доступна обоим клиентам.

HTTP-маршруты: `GET /api/state?mode=real|demo` и
`POST /api/tools/<tool>?mode=real|demo`, тело — JSON аргументов инструмента.
Ошибки MCP возвращаются с HTTP 400 и исходным `isError: true`.
Backend слушает только loopback; это локальное учебное приложение без
авторизации и удалённого хостинга.
