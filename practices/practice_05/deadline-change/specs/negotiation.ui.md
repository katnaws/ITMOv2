# Согласование (UI) — перенос дедлайна

Основание: проверены исходники bridge и MCP из практики 4:
- practices/practice_04/dashboard/server.py
- practices/practice_04/mcp/study_tracker/server.py
- practices/practice_04/mcp/stdio.py

Фактический формат ответов и ошибок
- Успех MCP: объект-обёртка (envelope) с полями content (массив с одним элементом типа text) и isError=false. Сам объект задачи — внутри content[0].text как JSON-строка.
- Ошибка MCP: тот же envelope, но isError=true и текст ошибки в content[0].text. HTTP-статус от bridge — 400.
- Ошибка bridge (валидация/заголовки/размер/инвалидный host/origin): JSON { error: string }, HTTP 400 или 403/404 по коду в bridge.
- MCP недоступен: JSON { error: "MCP unavailable: ..." }, HTTP 502.

Различия с UI before и корректировки контракта
- До: UI предлагал успех `{ ok: true }`. Факт: требуется MCP envelope. Исправлено в contract.yaml и ui_spec.after.md.
- До: UI предлагал комбинированный `{ error, result }` на ошибки. Факт: либо MCP envelope isError, либо `{ error }` от bridge. Исправлено в contract.yaml и ui_spec.after.md.
- Endpoint: не добавляем новые, используем существующий `/api/tools/<tool>?mode=...`.

Точные требования к новому инструменту
- MCP tool: update_task_deadline(task_id, deadline)
  - Вход: { task_id: integer (type(task_id) is int, >=1, булевы недопустимы), deadline: string в формате YYYY-MM-DD }
  - Выходы/ошибки соответствуют формату MCP envelope из практики 4.
  - Идемпотентность: same-date — успешный no-op (возвращает тот же объект).

Правки UI поведения
- Модалка блокирует переключатели режима на время открытия. При закрытии блокировка снимается.
- На saving (отправка) блокируются повторы и закрытие (ESC/backdrop/крестик).
- Фоновые refresh не перетирают введённую дату; после успеха UI делает GET /api/state.
- Inline ошибки локализуются, текст извлекается из MCP/bridge и показывается на русском.

Просьба к команде логики
- Реализовать MCP tool `update_task_deadline` по указанному контракту (envelope с isError, контент JSON строки задачи, валидации как у существующих инструментов add_task/update_task_status/parse_date).
- Не менять формат bridge: HTTP 200/400/502, без новых эндпоинтов.
