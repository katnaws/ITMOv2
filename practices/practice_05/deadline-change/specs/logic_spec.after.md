Спецификация логики (after) — Перенос дедлайна существующего задания

Итоговый контракт (согласован с UI)
- MCP инструмент: update_task_deadline(task_id, deadline)
  - Вход: { task_id: integer, deadline: string YYYY-MM-DD }, additionalProperties: false.
  - Валидация: type(task_id) is int и >=1; булевы значения недопустимы; deadline — строго YYYY-MM-DD; календарные ошибки → isError: true.
  - Поведение: изменить только deadline; id/title/course/status/created_at остаются неизменными. Пересчитать days_left и overdue по Europe/Moscow.
  - Идемпотентность: если deadline совпадает со старым — успешный no-op, возвращается объект без изменений.
  - Выход: MCP envelope как в практике 4: { content: [{ type: "text", text: JSON_строка_объекта_задания }], isError: false }.
  - Ошибки: isError: true с текстом в content[0].text: "Date must use YYYY-MM-DD", "day 30 must be in range ...", "task_id must be a positive integer", "Task <id> not found".

- HTTP мост: POST /api/tools/update_task_deadline?mode=real|demo
  - Тело: { task_id, deadline }, Content-Type: application/json, ≤16 KB.
  - Ответы: 200 — MCP envelope успех; 400 — MCP isError или bridge валидация; 502 — MCP недоступен.
  - Авторизация/Origin: как в практике 4 (localhost + белый список).
  - Источник данных: только MCP/SQLite; bridge не обращается к БД напрямую.

Инварианты
- Прошлые даты разрешены; «сегодня» не overdue; статус done никогда не overdue.
- Только deadline меняется; id/title/course/status/created_at сохраняются.
- UI после успеха вызывает GET /api/state?mode=… для обновления всех проекций/сортировки.
- На ошибках не возвращать трассировки/стек; только сообщения как у существующих инструментов.

E2E сценарии
1) Успех (в будущем): days_left > 0, overdue=false, статус неизменен.
2) Граничный (сегодня): days_left=0, overdue=false.
3) Прошлое (todo/in_progress): days_left<0, overdue=true.
4) Прошлое (done): days_left<0, overdue=false.
5) Неверная дата: 400, isError=true, текст календаря.
6) Неверный формат даты: 400, isError=true, "Date must use YYYY-MM-DD".
7) Неверный task_id (true/0/-5): 400, isError=true, "task_id must be a positive integer".
8) Не найдено: 400, isError=true, "Task <id> not found".
9) Доп. поля: 400, isError=true (или bridge 400), без изменений в БД.

Различия UI before vs logic before и принятые решения
- Формат успеха: UI предлагал `{ ok: true }`; принято MCP‑envelope с объектом задачи (как в практике 4).
- Ошибки: UI предлагал комбинированный объект с полем `result`; принято — либо MCP isError envelope, либо bridge `{ error: string }` для валидации.
- Обновление данных: UI подтверждает вызов GET /api/state после успеха.
- Нейминг/endpoint: единый `update_task_deadline` через существующий `/api/tools/...` мост, без новых API.

Связанные артефакты
- Контракт OpenAPI: practices/practice_05/deadline-change/specs/contract.yaml
- Согласование: practices/practice_05/deadline-change/specs/negotiation.logic.md
