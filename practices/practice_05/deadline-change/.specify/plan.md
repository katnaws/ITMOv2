Plan: Реализация переноса дедлайна

Steps
1) Backend MCP: реализовать update_task_deadline(task_id, deadline) в practices/practice_04/mcp/study_tracker/server.py (валидации, обновление только поля deadline, пересчёт days_left/overdue, идемпотентность для same-date).
2) MCP catalog: добавить tool в TOOLS с inputSchema (additionalProperties: false), annotations как у существующих.
3) HTTP bridge: добавить "update_task_deadline" в множество TOOLS в practices/practice_04/dashboard/server.py (без доступа к DB напрямую).
4) UI: добавить кнопку «Перенести срок», модалку, форму date; блокировать «Сохранить» при same-date/no-change; по успеху — закрыть и вызвать GET /api/state?mode=…
5) Tests/Demo: на временной БД (STUDY_TRACKER_DB) проверить успех, ошибки и граничные случаи; не менять реальную БД.
6) Runner: перезапустить и приложить логи успешной проверки.

Notes
- Не добавлять новые API; использовать существующий мост /api/tools/<tool>.
- Europe/Moscow для расчётов; прошлая дата разрешена; сегодня не overdue; done не overdue.
