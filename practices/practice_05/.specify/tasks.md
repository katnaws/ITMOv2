# Tasks — Redaction Feature (before)

Phase 0 — Контракт и спецификации
- [x] Согласовать общий контракт с UI (contract.proposed.yaml)
- [x] Зафиксировать after‑версии логики/UI (contract.after.yaml/openapi.yaml, logic_spec.after.md)

Phase 1 — Тесты (до кода)
- [x] Unit‑тесты redaction по паттернам (PEM, токены, пары KEY=, quoted values)
- [x] Интеграционный тест POST /api/reviews: 200/422/413/502; доказать redacted вход stub
- [x] Отсутствие логов с сырым diff (Handler.log_message overridden)

Phase 2 — Реализация
- [x] Реализовать redaction (детерминированно)
- [x] Реализовать HTTP‑endpoint и заглушку LLM
- [x] Пройти все тесты, подготовить DEMO.md

Phase 3 — V2 Preview + Provider + Real Review
- [x] Добавить /api/preview (без сети), счётчик замен
- [x] Добавить /api/provider (provider/model/configured)
- [x] Реализовать реальный вызов VseLLM в /api/reviews с повторной редактцией и строгой проверкой JSON ответа
- [x] Обновить тесты (без реальной сети): preview, 422/413, 503 без ключа, 502 при timeout/невалидном ответе
- [x] Обновить README/DEMO/SUBMISSION/reflection/verification
