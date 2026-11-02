# DEMO — Backend Redaction API (UI+Backend)

Запуск сервера (foreground):
- python3 -c "from practices.practice_05.service import app; app.serve('127.0.0.1', 8000)"

Или запустить в фоне (журнал в /tmp/practice05_server.log, PID в /tmp/practice05_server.pid):
- см. verification.md и README.md

Примеры запросов (в другом терминале):
- curl -s -X POST http://127.0.0.1:8000/api/reviews -H 'Content-Type: application/json' -d '{"diff":"diff --git a a\n+ sk-SECRET\n+ -----BEGIN PRIVATE KEY-----\nABC\n-----END PRIVATE KEY-----\n"}'
- curl -s -X POST http://127.0.0.1:8000/api/preview -H 'Content-Type: application/json' -d '{"diff":"diff --git a a\n+ PASSWORD=demo\n+ sk-DEMOONLY123\n"}'
- curl -s http://127.0.0.1:8000/api/provider

Ожидаемый ответ: 200 JSON с summary, risks (≤3), checks (ответ формируется провайдером VseLLM; при недоступности — 502 или 503 при отсутствии ключа).

Ошибки:
- 422: отсутствует/нестроковый/whitespace diff, невалидный JSON
- 413: >20000 символов
- 502: включите "STUB_TIMEOUT" в diff для эмуляции upstream ошибки

UI статика:
- Backend раздаёт содержимое practices/practice_05/web/ безопасно; UI реализуется отдельно.
