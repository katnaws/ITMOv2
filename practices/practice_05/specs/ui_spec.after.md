UI спецификация (after) — сервис «Diff Secret Redactor» (согласовано с контрактом)

Endpoint и контракт (согласовано)
- POST /api/reviews
- Request JSON: { "diff": string } (Content-Type: application/json)
- Лимит: 20000 символов (Unicode code points). При превышении сервер вернет 413 CONTENT_TOO_LARGE; UI блокирует отправку при >20000.
- Success 200 JSON:
  {
    "summary": string,
    "risks": Array<{ file?: string, line?: number, evidence?: string, risk: string }>, // ≤3
    "checks": Array<string>
  }
- Errors JSON (единый формат): { "error": { "code": string, "message": string } }
  - 422: UNPROCESSABLE_CONTENT
  - 413: CONTENT_TOO_LARGE
  - 502: LLM_UPSTREAM_ERROR

Видимая функциональность
- Текстовое поле “Diff input” (textarea):
  - Подсказка: «Вставьте unified diff (git diff/PR patch). Сырые секреты будут скрыты перед ревью».
  - Счетчик символов (Unicode) и лимит 20000. При превышении: ошибка, кнопка disabled.
  - Label связан с полем; aria-describedby для подсказок и ошибок.
- Кнопка “Review”:
  - Disabled при пустом поле, при превышении лимита, при Loading.
- Индикатор загрузки: текст «Загрузка…» (aria-live=polite).
- Блок «Результат ревью»:
  - Success: показывает summary, до 3 risks (file/line/evidence/risk), список checks (строки). Исходный diff не отображается.
  - Error: сообщения для 422/413/502 без серверных деталей.
- Ссылка «Очистить» с подтверждением; очищает textarea и состояние UI. Исходный diff нигде не сохраняется.

Доступность и UX
- Фокусируемость, видимый фокус; корректные label/aria; aria-live для ошибок/статусов.
- Мягкая проверка «похож на diff»: предупреждение и возможность отправки. Окончательное решение — за сервером (422 при необходимости).

Клиентская валидация
- Обязательность: diff не пустой.
- Лимит: ≤20000 символов (Unicode). >20000 → ошибка и disable.
- Формат: базовые эвристики (diff --git, +++/---, @@) → предупреждение при отсутствии.

Безопасность клиента
- Не сохранять сырые данные в localStorage/session/IDB; не логировать diff/ответ в консоль.
- Не вставлять HTML из ответа; безопасный текстовый рендеринг.
- Явно различаем: ввод пользователя остается только в textarea и виден пользователю, но не «эхо»-выводится в блок результатов, не логируется и не сохраняется.

Состояния UI
- Idle → Valid → Loading → Success/Error.
- Error mapping:
  - UNPROCESSABLE_CONTENT (422): «Невалидный diff. Проверьте формат.»
  - CONTENT_TOO_LARGE (413): «Лимит 20000 символов превышен.»
  - LLM_UPSTREAM_ERROR (502): «Сервис ревью временно недоступен. Повторите позже.»

Наблюдаемость результата
- Заглушка детерминированна; UI демонстрирует стабильный результат (summary/risks/checks) и явно видимую очистку формы.
