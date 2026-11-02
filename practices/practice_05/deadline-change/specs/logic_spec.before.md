Спецификация логики (before) — Перенос дедлайна существующего задания

Контекст и цель
- Расширяем Study Space из практики 4 одной фичей: возможность изменить дедлайн уже существующего задания, без влияния на остальные поля. Эта спецификация независима от кода, фиксирует контракт и правила до реализации.

MCP tool: update_task_deadline (предложение)
- Назначение: изменить поле deadline для задания с заданным ID; остальные поля неизменны.
- Формат даты: YYYY-MM-DD, таймзона — Europe/Moscow (используется для расчётов days_left/overdue; само поле deadline хранится как дата без времени).
- Вход (JSON‑схема, additionalProperties: false):
  {
    "task_id": integer (type(task_id) is int, minimum: 1; булевы значения запрещены),
    "deadline": string (строка даты в формате YYYY-MM-DD)
  }
- Выход (успешно, 200): объект задания в том же формате, что возвращают существующие инструменты (id, title, course, deadline, status, created_at, days_left, overdue). Поля title/course/status/created_at не меняются.
- Ошибки:
  - Неверный формат даты: "Date must use YYYY-MM-DD" → MCP isError: true; HTTP bridge вернёт 400.
  - Некорректная календарная дата (например, 2026‑02‑30): стандартная ошибка Python дат (например, "day 30 must be in range 1..28 for month 2 in year 2026") → MCP isError: true; HTTP 400.
  - task_id не положительное целое или булево: "task_id must be a positive integer" → MCP isError: true; HTTP 400.
  - Задание не найдено: "Task <id> not found" → MCP isError: true; HTTP 400.

Правила и инварианты
- Допускается перенос на прошедшую дату (аналогично add_task). Это сразу может делать задание просроченным, если статус не "done".
- "Сегодня" не считается просроченным: days_left = 0, overdue = false.
- Выполненные задания (status == "done") никогда не просрочены: overdue = false независимо от даты.
- Меняются только deadline и производные поля (days_left, overdue). created_at/id/title/course/status остаются неизменными.

HTTP контракт через существующий bridge (предложение)
- Endpoint: POST /api/tools/update_task_deadline?mode=real|demo
  - mode=real — реальная база; mode=demo — временная база с seed данными.
- Тело запроса: { "task_id": number, "deadline": "YYYY-MM-DD" }
- Заголовки: Content-Type: application/json
- Ограничение тела: ≤ 16 KB (как в текущем bridge).
- Ответы:
  - 200 OK — успешный MCP‑вызов; форма ответа идентична другим tool: { content: [{ type: "text", text: JSON_строка_объекта_задания }], isError: false }.
  - 400 Bad Request — неверный запрос (валидатор bridge) или MCP isError: true.
  - 502 Bad Gateway — MCP недоступен/сбой субпроцесса.
- Авторизация/Origin: те же правила, что уже реализованы (Host ограничен на localhost, Origin — белый список).

E2E сценарии (для последующей реализации и проверки)
1) Успех: task_id существующего задания, deadline = дата в будущем → 200, вернулся объект; status не меняется; days_left > 0; overdue = false.
2) Граничный: deadline = сегодня → 200; days_left = 0; overdue = false; статус не меняется.
3) Перенос на прошлую дату (status != done) → 200; days_left < 0; overdue = true; статус не меняется.
4) Перенос на прошлую дату (status == done) → 200; days_left < 0; overdue = false (по правилу для выполненных).
5) Ошибка: deadline = "2026-02-30" → 400, isError: true, текст ошибки календаря.
6) Ошибка: deadline = "20261007" → 400, isError: true, "Date must use YYYY-MM-DD".
7) Ошибка: task_id = true или 0 или -5 → 400, isError: true, "task_id must be a positive integer".
8) Ошибка: task_id = 999999 → 400, isError: true, "Task 999999 not found".
9) Ошибка: дополнительные поля в теле запроса → 400, isError: true (additionalProperties: false на стороне MCP; bridge также вернёт 400 при общей валидации).

Соответствие текущим правилам и необходимые изменения
- Форматы дат и поведение overdue соответствуют уже существующим функциям (parse_date, task_view). Прошлая дата допустима, "сегодня" не overdue, completed не overdue — уже реализовано в task_view.
- Ограничение на тип идентификатора (исключение булевых) соответствует текущей проверке в update_task_status (type(x) is int).
- Для HTTP bridge потребуется добавить новый инструмент в белый список TOOLS: "update_task_deadline" (код будет изменён позже, после согласования контракта).
- Для MCP потребуется реализовать функцию update_task_deadline(task_id, deadline) по правилам выше и добавить её в каталог TOOLS с inputSchema и annotations (аналогично существующим tool).
- Реальные задания/БД не трогаем при проверках; демо/тесты работают на временной базе через STUDY_TRACKER_DB (совместимо с runner).

Применение Spec Kit (manual, без автопайплайна)
- В этом проекте используем ручной template‑driven подход (см. practices/practice_05/specs/spec_kit_vs_openspec.md). Данная before‑спека фиксирует цель, контракт MCP/HTTP, инварианты и E2E сценарии. После согласования будет создана after‑спека и выполнена реализация с проверками runner'ом.

Синхронизация с UI (контракт для согласования)
- UI вызывает POST /api/tools/update_task_deadline с JSON телом { task_id, deadline } и параметром mode (real|demo).
- На успехе UI декодирует поле result.content[0].text как JSON объекта задания и обновляет вид (days_left/overdue пересчёт локально не нужен — приходит из сервера).
- На ошибке (HTTP 400 с isError: true) UI показывает дружелюбную ошибку, не меняет локальное состояние; повтор отправки по решению пользователя.

Out of scope
- Изменение других полей задания, массовые апдейты, история изменений, аудит, аутентификация.
