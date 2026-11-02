Feature: Перенос дедлайна существующего задания

Контекст
- Study Space (практика 4): MCP study_tracker + HTTP bridge + React dashboard.
- Цель: добавить инструмент переноса дедлайна, без изменения других полей.

Артефакты
- UI before: practices/practice_05/deadline-change/specs/ui_spec.before.md
- Logic before: practices/practice_05/deadline-change/specs/logic_spec.before.md
- Negotiation: practices/practice_05/deadline-change/specs/negotiation.logic.md
- Contract (OpenAPI): practices/practice_05/deadline-change/specs/contract.yaml
- Logic after: practices/practice_05/deadline-change/specs/logic_spec.after.md

Примечание
- Manual template-driven Spec Kit: проект не инициализирован как Spec Kit (нет корневого .specify/), артефакты ведём локально в каталоге фичи, без автоматического workflow.
