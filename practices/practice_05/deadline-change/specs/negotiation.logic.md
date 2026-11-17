Согласование (logic vs UI) — перенос дедлайна задания

Итоговый общий контракт (минимальный, совместимый с текущим мостом)
- MCP tool: update_task_deadline
  - Вход: { task_id: integer (type(task_id) is int, minimum 1; булевы недопустимы), deadline: string YYYY-MM-DD }
  - Выход: MCP‑envelope: { content: [{ type: "text", text: JSON_строка_объекта_задания }], isError: false }
  - Ошибки: MCP‑envelope с isError: true и текстом ошибки в content[0].text
- HTTP bridge (существующий): POST /api/tools/update_task_deadline?mode=real|demo
  - Mode: real — общая БД; demo — временная БД, seed и изоляция как в существующем bridge.
  - Body: { task_id, deadline }, Content-Type: application/json, ≤16 KB
  - Ответы: 200 на успех; 400 при валидационных и бизнес‑ошибках; 502 при недоступности MCP.
  - Авторизация/Origin — как уже реализовано (localhost + белый список Origin).

Инварианты (обязательные)
- Формат даты — строго YYYY-MM-DD, календарная проверка; прошлая дата разрешена.
- Europe/Moscow timezone для расчёта days_left/overdue; deadline — дата без времени.
- Сегодня не overdue; status==done никогда не overdue.
- Меняем только deadline; title/course/status/created_at/id неизменны.
- same-date перенос — успешный идемпотентный no-op (объект возвращается без изменения); UI держит «Сохранить» disabled при отсутствии изменений.
- После успеха UI выполняет GET /api/state?mode=… чтобы обновить все проекции и сортировки.
- Источник данных — только MCP/SQLite; bridge не ходит напрямую в БД.
- Не создаём новых API, только расширяем существующий набор tools и bridge.
- На ошибках не выдаём трассировку СУБД/стека, только короткие сообщения (как в текущих логах MCP).

Реальные различия и решения
- В UI before предлагался упрощённый успех формата `{ ok: true }`. Решение: соблюдаем фактический формат bridge/MCP — возвращаем MCP‑envelope с объектом задачи в `content[0].text` (JSON‑строка). UI парсит и может сразу обновить строку, но всё равно делает GET /api/state.
- В UI before ошибки были заданны как `{ error: string, result: ... }`. Решение: используем текущий формат моста — тело ответа само есть MCP‑envelope (или `{error: "..."}` валидационные ошибки bridge), статус 400. UI выводит дружелюбный текст, не показывает трассы.
- Формулы overdue и timezone: подтверждены правилами практики 4 (task_view) — сегодня не overdue; done не overdue; Europe/Moscow.
- Идентификатор: подтверждаем строгую проверку `type(task_id) is int`, минимум 1, не булево — как в update_task_status.

Открытые пункты для UI (не блокируют контракт)
- Отображение истории: человекочитаемое имя инструмента и аргументы — UI решает локально.
- Inline сообщения об ошибке: тексты мост/сервер возвращают кратко; UI локализует/смягчает.

Примеры ответов
- Успех 200 (MCP): { "content": [{ "type": "text", "text": "{\"id\":1,\"title\":\"...\",\"course\":\"...\",\"deadline\":\"2026-11-10\",\"status\":\"todo\",\"created_at\":\"...\",\"days_left\":8,\"overdue\":false}" }], "isError": false }
- Ошибка 400 (MCP isError): { "content": [{ "type": "text", "text": "Task 999999 not found" }], "isError": true }
- Ошибка 400 (bridge валидация): { "error": "Content-Type must be application/json" }
