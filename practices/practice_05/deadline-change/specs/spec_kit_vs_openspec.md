> Историческое сравнение первой попытки. Итоговое применение обоих фреймворков и выводы: [COMPARISON](../../frameworks/COMPARISON.md).

# Spec Kit vs OpenSpec — применение к «Переносу дедлайна» (ДЗ5)

Официальные ссылки
- Spec Kit (GitHub): https://github.com/github/spec-kit
  - Документация: https://github.github.io/spec-kit/
- OpenSpec: https://github.com/Fission-AI/OpenSpec

Используемая версия и режим
- Установлен GitHub Spec Kit CLI: specify 1.2.5 (проверено: `specify --help`, `specify --version`).
- В этом проекте Spec Kit используется вручную (manual, template‑driven), без запуска автоматических workflow и без сетевых интеграций.

Артефакты и применение
- Стоковые шаблоны и скрипты доступны в practices/practice_05/.specify/templates и scripts/workflows/memory.
- Под старого «ревьюера» были custom .specify/spec.md/plan.md/tasks.md/constitution.md; они устарели и заменены актуальной ссылочной документацией на новую фичу:
  - Новые документы фичи размещены в practices/practice_05/deadline-change/.specify/ (feature.md, plan.md, tasks.md) — это ручная адаптация на основе стоковых template паттернов.
  - Мы не выдаём эти документы за сгенерированные автоматически: они заполнены вручную и содержат конкретные пути и контракты.
- Контракт и спеки фичи:
  - UI/logic before/after: practices/practice_05/deadline-change/specs/*.md
  - OpenAPI: practices/practice_05/deadline-change/specs/contract.yaml

Ограничения manual‑режима
- Не используется автоматический speckit.plan/tasks генератор; документы обновляются вручную.
- Нет CI/CD связки; проверка выполняется локальными скриптами практики 4 (runner.sh) и hand‑rolled демо.
- Нет внешней сети/секретов; MCP/SQLite — локальные.

Синхронизация план/таски с готовностью бэкенда
- Обновлённые feature.md/plan.md/tasks.md в practices/practice_05/deadline-change/.specify отражают текущий статус: реализован бэкенд (MCP tool + bridge whitelist + проверки), UI будет обновлён отдельно.
- Реальные проверки: bash practices/practice_04/runner.sh, MCP stdio demo, HTTP bridge demo. Артефакт подтверждения: practices/practice_04/logs/* и (опционально) backend.json в verification каталоге фичи.

Выбор фреймворка
- Требование «другой SDD‑framework» для ДЗ5 закрыто использованием Spec Kit; OpenSpec в этом проекте не используется.
