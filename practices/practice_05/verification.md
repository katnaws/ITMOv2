# Проверки итогового прогона

После переноса в основную рабочую папку повторно выполнены:

| Проверка | Результат | Сохранённый вывод |
| --- | --- | --- |
| Обязательный runner практики 4, MCP, bridge, React build | Пройдена | [runner.txt](frameworks/evidence/integrated/runner.txt) |
| Расширенная проверка MCP/HTTP на временных БД | Пройдена, 31 вызов, 6 групп | [backend-contract.json](frameworks/evidence/integrated/backend-contract.json) |
| Полный HTTP check | Пройдена, 17 запросов | [http.json](frameworks/evidence/integrated/http.json) |
| Chrome/Playwright: UI, сохранение, границы, ошибка, повтор | Пройдена, 4 группы, ошибок JS нет | [browser.json](frameworks/evidence/integrated/browser.json) |
| OpenSpec validate --all --json | 1 спецификация, 0 ошибок | [openspec-validate.json](frameworks/evidence/integrated/openspec-validate.json) |
| Spec Kit check-prerequisites с tasks | Пройдена | [speckit-prerequisites.json](frameworks/evidence/integrated/speckit-prerequisites.json) |

OpenSpec archive реально выполнен: [вывод CLI](frameworks/evidence/continuation/openspec-archive.json), [архив изменения](frameworks/openspec/changes/archive/2026-11-02-deadline-change/). В Spec Kit закрыты T001–T009; сверка по инструкции converge выполнена Codex: [отчёт](frameworks/evidence/continuation/speckit-converge.json). Валидатор OpenSpec проверяет структуру спецификации; prerequisite-скрипт Spec Kit — наличие документов. Корректность приложения подтверждают отдельные тесты.

## Воспроизведение из корня

```sh
bash practices/practice_04/runner.sh
python3 practices/practice_04/dashboard/check.py
python3 practices/practice_05/frameworks/tests/deadline_check.py
```

Python-проверки выводят JSON в stdout, сами новый отчёт не сохраняют. Пример: `python3 practices/practice_05/frameworks/tests/deadline_check.py > /tmp/practice05-check.json`.

Браузерный скрипт: `frameworks/tests/browser.cjs`. Требует установленный Playwright и Chrome, работающий временный сервер из [DEMO](DEMO.md). В этом прогоне использован внешний тестовый runtime `/tmp/practice05-ui-check/node_modules`, без изменения зависимостей приложения:

```sh
NODE_PATH=/tmp/practice05-ui-check/node_modules BASE_URL=http://127.0.0.1:8765 node practices/practice_05/frameworks/tests/browser.cjs
```

Временный runtime не входит в репозиторий; на другом компьютере Playwright надо установить отдельно. Скрипт не обращается к персональным заданиям: используется demo и отдельные временные базы серверных тестов.

Реальны HTTP 200/400/403, запись в SQLite и повтор после перезапуска MCP. Только 502 в браузере подменён через page.route в отдельном контексте; после снятия подмены выполнен настоящий успешный запрос. Не измерялись процент надёжности и время выполнения сравнительных реализаций.

Ранние отчёты первой попытки в `deadline-change/` исторические. Текущий источник результатов — `frameworks/evidence/integrated/`. Информация об авторах и передаче работы — [WORKFLOW](frameworks/WORKFLOW.md).
