# Practice 05 — Проект UI+Backend: Diff Secret Redactor

Этот каталог содержит backend-реализацию сервиса и согласованные спецификации; UI разрабатывается отдельно в practices/practice_05/web/ (этими тестами не изменяется).

Контракт API
- Endpoint: POST /api/reviews
- v2 Preview: POST /api/preview → { redacted, redactions_count }
- Provider status: GET /api/provider → { provider, model, configured }
- Тело: { "diff": string } (application/json)
- Ограничение: 20000 Unicode символов (len)
- Успех 200: { summary, risks≤3, checks }
- Ошибки: 422 UNPROCESSABLE_CONTENT, 413 CONTENT_TOO_LARGE, 502 LLM_UPSTREAM_ERROR (единый формат { error: { code, message } })
- OpenAPI: specs/contract.after.yaml (также contract.openapi.yaml)

Статика UI
- Корень: practices/practice_05/web/
- Backend раздаёт GET / и файлы (index.html, app.js, style.css) безопасно, с правильным Content-Type и ограничением по каталогу.
- В тестах используется временный STATIC_ROOT; реальные UI-файлы не перезаписываются.

Запуск backend (из корня репозитория)
- Вариант для разработки: python3 -c "from practices.practice_05.service import app; app.serve('127.0.0.1', 8000)"
- Живой demo (оставляем запущенным): см. /tmp/practice05_server.pid и /tmp/practice05_server.log
- Остановка: kill $(cat /tmp/practice05_server.pid) или Ctrl+C если запускали в foreground

Тесты (stdlib unittest)
- Запуск: python3 -m unittest discover -v -s practices/practice_05/tests -t .
- Доказательства в тестах:
  - Редакция секретов (PEM, sk-*/ghp_*, JWT с заголовком eyJ..., пары PASSWORD/SECRET/TOKEN/KEY, AWS ключи)
  - Границы/ошибки: 422/413/502; ограничение ровно 20000/20001; пустой/whitespace/нестроковый/невалидный JSON
  - Spy (unittest.mock) подтверждает: stub вызывается с очищенным текстом; на 422/413 не вызывается
  - Перехват stdout/stderr доказывает отсутствие утечки сырого diff/секретов
  - Статика: корректные Content-Type, containment, запрет traversal; тесты используют временный каталог

Безопасность и конфигурация
- v2: Реальный HTTPS вызов к VseLLM (openai/gpt-5) в /api/reviews; preview не вызывает сеть.
- Ключ провайдера загружается из ENV (в т.ч. безопасно из .env в память сервера), не выводится в ответы/логи.
- Логи не содержат сырых diff; блокируем cross-origin POST (строгая проверка Origin на тот же порт); Content-Type=application/json; проверка Content-Length.

Spec Kit (manual, template-driven)
- Штатный артефакт: .specify/memory/constitution.md (конституция)
- Документы адаптации (template‑driven во вложенной папке): .specify/spec.md, .specify/plan.md, .specify/tasks.md — документы нашей ручной template‑driven адаптации; автоматический workflow CLI не запускался. Артефакты .specify/* расположены во вложенной папке практики; CLI использовался вручную, без интеграции с CI/CD.

Ссылки
  - Spec Kit (официальный репозиторий): https://github.com/github/spec-kit
    - Документация: https://github.github.io/spec-kit/
  - Верификация UI v2: practices/practice_05/specs/ui_verification.v2.md (live + simulated результаты; скриншоты в /tmp/practice05-ui-check)
 - OpenAPI Specification: https://spec.openapis.org/oas/latest.html
