---
name: auto-check
description: Проверка практики 4 после изменений, реальные MCP-демо и сборка React.
---

Все shell-команды выполняй из корня репозитория. После правок файлов
`practices/practice_04/` запускай `bash practices/practice_04/runner.sh`.
Runner проверяет study-tracker через MCP stdio на временной базе, включая
сохранение между запусками, фильтры, дедлайны и ошибочный вход.

Изучи `practices/practice_04/logs/runner.log`, `study_tracker_demo.json`
и `dashboard_check.json`. В ответе укажи результат проверки.
Ненулевой exit code означает провал: исправь причину и повтори runner.
Не выдавай локальное демо за вызов языковой моделью в OpenCode.

Для использования трекера вызывай инструменты сервера `study_tracker`:
`add_task`, `list_tasks`, `update_task_status`, `study_dashboard`.
Не выдумывай реальные задания и даты: бери их из запроса пользователя.
Для демо используй временную БД через `STUDY_TRACKER_DB`.
Даты задавай как YYYY-MM-DD, статусы — todo / in_progress / done.
