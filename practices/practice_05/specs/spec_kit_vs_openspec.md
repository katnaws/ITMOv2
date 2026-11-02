# Spec Kit vs OpenSpec — сравнение и ссылки

Официальные ссылки
- Spec Kit (GitHub): https://github.com/github/spec-kit
  - Документация: https://github.github.io/spec-kit/
- OpenSpec: https://github.com/Fission-AI/OpenSpec (официальный репозиторий)

Сравнение
- Процесс:
  - Spec Kit: Specify CLI + workflows (speckit: specify → plan → tasks → implement) с gate‑ревью.
  - OpenSpec: CLI openspec, хранит артефакты в каталоге openspec/; фокус на лёгких изменениям, “stores” и интеграциях.
- Хранение артефактов:
  - Spec Kit: шаблоны в .specify/templates; штатная «память/конституция» — в .specify/memory (constitution.md). В этом проекте .specify/spec.md, .specify/plan.md, .specify/tasks.md — наша ручная template‑driven адаптация во вложенном каталоге практики, не «автоматически канонические» файлы CLI.
  - OpenSpec: своя структура и команды (init/list/validate/view), в этом проекте не использовался.

Выбор для ДЗ5
- По требованию «другой SDD‑framework» используем GitHub Spec Kit.
- Две спеки (UI/Logic) и общий контракт согласуем до кода; затем реализуем по ручному workflow speckit (template‑driven), без автоматического pipeline.
