# Актуальные артефакты двух фреймворков

- [Ход работы, команды и участники](WORKFLOW.md).
- [Практическое сравнение](COMPARISON.md).
- OpenSpec logic: [before](logic.before.md), [согласованная дельта до кода](logic.after.md), [основная спецификация после archive](openspec/specs/logic/spec.md), [архив](openspec/changes/archive/2026-11-02-deadline-change/).
- Spec Kit UI: [независимый before](ui.before.md), [согласованный after](ui.after.md), [текущая spec](specs/001-name-deadline-move/spec.md), [plan](specs/001-name-deadline-move/plan.md), [tasks](specs/001-name-deadline-move/tasks.md), [constitution](.specify/memory/constitution.md).
- Согласование: [logic](negotiation.logic.md), [UI](negotiation.ui.md), [контракт](contract.yaml).
- Фактические действия OpenCode: [журнал команд](evidence/opencode-commands.json), [анализ GPT‑5](evidence/speckit-analyze-gpt5.md).
- [Передача работы Codex](evidence/continuation/start.json), [перенос исходников](evidence/integration.json), [итоговые проверки](evidence/integrated/).

`before/`, `_evidence/`, `source_hashes/`, начальные `*.sha256` и корневые `openspec.*` сохраняют промежуточные состояния и попытки. Это не заявления о текущем результате. Хеши после прямой реализации находятся в `evidence/integration.json`. В сырых отчётах остаются пути исходного временного прогона; они не должны существовать на компьютере проверяющего. Перенесённая папка отдельно проверена, см. `evidence/integrated/`.
