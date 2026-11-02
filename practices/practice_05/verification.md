Verification — Practice 05 UI v2

Документ: specs/ui_verification.v2.md — содержит фактические результаты проверки (live + simulated) и пути к скриншотам в /tmp.

Итог
- Базовый DOM и границы подтверждены.
- Live provider работает; preview и одно review — пройдены.
- Защита гонок/Abort подтверждена simulated route в отдельном контексте.
# Verification — Practice 05 (UI+Backend, v2)

Команда запуска (из корня):
- python3 -m unittest discover -v -s practices/practice_05/tests -t .

Фактический результат:
- OK — 12 tests (v2)
  - preview: редактированный текст и redactions_count≥1, идемпотентность
  - reviews: 413/422; 503 без ключа; 502 timeout/invalid provider; boundary 20000
  - provider: GET /api/provider возвращает JSON {provider, model, configured}
  - origin/mime/length: строгие проверки; статик — temp fixtures, корректные Content-Type; traversal блокируется

Модели в unit: провайдер замокан (urlopen)
- Реальные сетевые вызовы в тестах не выполнялись.

Live evidence
- Активный сервер: 127.0.0.1:8000; текущий PID записан в /tmp/practice05_server.pid (последний — 66099)
- GET /api/provider → 200; POST /api/preview → 200
- Реальный POST /api/reviews (синтетический diff) → 200; тело безопасное, без исходных секретов (англ./рус. ответ допустим)
- Ранний 200 от старой заглушки не считается live; текущий evidence — VseLLM
