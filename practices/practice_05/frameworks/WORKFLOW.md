# Реальный ход работы и авторство

## Почему был новый прогон

В первой попытке перенос дедлайна уже существовал в незакоммиченном рабочем дереве, но два разных фреймворка не были применены полноценно. Чтобы не выдавать спецификации задним числом за предшествующие коду, подготовлен отдельный временный прогон из исходников коммита `57d74e9bfe387f76ef8eeca7eca9f64c9ea82039`. Несмотря на название этого старого коммита «practice_5 done», в его коде практики 4 инструмента переноса дедлайна ещё не было.

Исходники извлечены через Git archive в `/tmp/practice05-framework-replay-20261102`, без Git-репозитория, персональных БД и секретов. Наличие прежнего прототипа в основном рабочем дереве не скрывается: его начальные хеши записаны в [start.json](evidence/continuation/start.json). Хеши baseline и отсутствие нового инструмента: [manifest](manifest.json), [logic before](logic.before.md), [исходные фрагменты](./_evidence/).

## Участники и этапы

| Этап | Кто | Результат |
| --- | --- | --- |
| Независимые исходные требования | GPT‑5 через OpenCode, отдельные UI/logic чаты | `logic.before.md`, `ui.before.md` |
| OpenSpec подготовка | GPT‑5, `ses_e639c5137ffe7k3fU7U8EyutH1` | init/instructions, proposal/specs/design/tasks, agreed delta |
| Spec Kit подготовка | GPT‑5, `ses_e639a88daffeLNIh3Xhg4R66SP` | init, constitution/spec/clarify/plan/tasks, analyze |
| Согласование перед кодом | Два чата, координация Codex | negotiation, after-спеки, общий contract |
| Передача | Пользователь после двух `402 provider.quota`: «видимо кончились лимиты делай сам» | Прямое выполнение Codex разрешено |
| Реализация нового прогона | Codex | MCP/bridge, React UI, проверки, фокус модалки |
| Завершение | Codex по инструкциям фреймворков | OpenSpec apply/validate/archive; Spec Kit implement/converge |
| Интеграция | Codex | Перенос семи файлов в основной проект после сверки исходных хешей; повтор всех основных проверок |

GPT‑5 не завершил реализацию этого прогона: относительный патч не применился, затем закончилась квота. Эти действия не приписываются ему. Снимки `before` и согласованные спецификации подготовлены до новой реализации; уточнения Codex о тестах и измеримых критериях внесены до кода. Финальный статус tasks изменён после проверок.

## OpenSpec 1.14.1

Фактически использован `npx -y @fission-ai/openspec@1.14.1`. Ниже команды процесса в его рабочей папке; конкретные строки и результаты сохранены в [журнале OpenCode](evidence/opencode-commands.json) и [CLI evidence](evidence/openspec/).

```text
init --tools none .
new change deadline-change --json          # первая попытка: already exists
instructions proposal --change deadline-change --json
instructions specs --change deadline-change --json
instructions design --change deadline-change --json
instructions tasks --change deadline-change --json
instructions apply --change deadline-change --json
status --change deadline-change --json
validate --all --json
archive deadline-change --yes --json
validate --all --json
```

Созданный агентом ранее каталог retained; ошибку new change не скрываем. В apply закрыты 5/5 задач. Перед archive валидны change и spec; archive синхронизировал один добавленный requirement. Изменение находится в `openspec/changes/archive/2026-11-02-deadline-change/`. После archive основная spec валидна, незавершённого change нет. Это архив OpenSpec, не Git-фиксация.

Итоговые CLI-выводы: [apply](evidence/continuation/openspec-apply-completed.json), [archive](evidence/continuation/openspec-archive.json), [валидация после интеграции](evidence/integrated/openspec-validate.json).

## GitHub Spec Kit 1.2.5

Реальный init: `specify init --here --integration opencode --force --non-interactive`. Он создал `.specify/` и инструкции `.opencode/commands/speckit.*.md`. Обработаны стадии constitution, specify, clarify, plan, tasks, analyze; затем Codex выполнил implement и converge по этим инструкциям.

Официальные скрипты, которые действительно вызывались:

- `.specify/scripts/bash/create-new-feature.sh` — выдал `specs/001-name-deadline-move`.
- `resolve-template.sh constitution-template --json` — источник constitution.
- `setup-plan.sh --json`, `setup-tasks.sh --json` — подготовка документов.
- `check-prerequisites.sh --json --require-tasks --include-tasks` — проверка implement/converge.

Это агентный процесс: инструкции читаются агентом, официальные скрипты выполняют свои шаги, содержание документов и код пишет агент. Не использовались несуществующие здесь `opencode run --command` и команда единого автопайплайна. Анализ GPT‑5 сохранён [дословно](evidence/speckit-analyze-gpt5.md). Затем добавлены quickstart и T009, убраны неизмеренные показатели. Чек-лист качества требований закрыт до реализации; T001–T009 закрыты после тестов. Отчёт [converge](evidence/continuation/speckit-converge.json) — сверка Codex по инструкции, а не результат отдельного бинарного анализатора. Hooks расширений не были зарегистрированы.

## Где находится текущий результат

Фреймворки перенесены в `practices/practice_05/frameworks/`; код — в существующую практику 4. Сырые логи сохраняют исходные `/tmp`-пути, их не переписывали. [integration.json](evidence/integration.json) содержит хеши перенесённого кода; [integrated](evidence/integrated/) — проверки из основной папки.

Команды shell запускались из корня репозитория; необходимые рабочие папки инструментам задавались дочерними subprocess. Пример повторной проверки перенесённых документов из корня:

```sh
python3 - <<'PYTHON'
import os, subprocess
from pathlib import Path
f = Path('practices/practice_05/frameworks').resolve()
env = dict(os.environ, OPENSPEC_TELEMETRY='0', SPECIFY_INIT_DIR=str(f),
           SPECIFY_FEATURE='001-name-deadline-move',
           SPECIFY_FEATURE_DIRECTORY=str(f / 'specs/001-name-deadline-move'))
subprocess.run(['npx', '-y', '@fission-ai/openspec@1.14.1', 'validate', '--all', '--json'], cwd=f, env=env, check=True)
subprocess.run(['bash', '.specify/scripts/bash/check-prerequisites.sh', '--json', '--require-tasks', '--include-tasks'], cwd=f, env=env, check=True)
PYTHON
```

Нужна сеть для npx при отсутствии пакета в кеше. Проверки приложения и запуск демо описаны в [verification](../verification.md) и [DEMO](../DEMO.md). Секреты и личные базы не копировались. HEAD сохранён, staging/commit/push не выполнялись. Первая попытка в `../deadline-change/` остаётся исторической, не текущим источником процесса.
