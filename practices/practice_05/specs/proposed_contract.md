Предложение контракта для согласования с Командой UI — POST /api/reviews

Метод и URL
- POST /api/reviews

Заголовки
- Content-Type: application/json

Запрос
{
  "diff": string  // обязательно; максимальная длина 20000 символов
}

Успешный ответ (200 OK)
{
  "summary": string,
  "risks": [
    { "file"?: string, "line"?: number, "evidence"?: string, "risk": string }
  ],
  "checks": [ string ]
}
- Ограничение: в массиве risks не более 3 элементов.

Ошибки
- 422 Unprocessable Content
  {
    "error": { "code": "UNPROCESSABLE_CONTENT", "message": string }
  }
- 413 Content Too Large
  {
    "error": { "code": "CONTENT_TOO_LARGE", "message": string }
  }
- 502 Bad Gateway (эмуляция сбоя/таймаута LLM)
  {
    "error": { "code": "LLM_UPSTREAM_ERROR", "message": string }
  }

Правила безопасности и логирования
- До любых логов и формирования prompt выполняется редактирование секретов: замена секретных значений на "[REDACTED]".
- Сырые диффы и секреты не логируются и не возвращаются в ответе API.
- Заглушка LLM получает только редактированный diff.

Покрываемые типы секретов (неисчерпывающий список)
- PEM private key блоки (от BEGIN до END).
- Токены/ключи с типичными префиксами: sk-*, ghp_*, JWT‑подобные триплеты (header.payload.signature).
- Пары переменных: PASSWORD=..., SECRET=..., TOKEN=..., KEY=... (без учёта регистра ключа).
- AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY — значения заменяются.

Согласовать
- Нужны ли дополнительные поля в success (например, score/traceId)?
- Тексты сообщений ошибок — оставлять свободными/локализуемыми, UI ориентируется на error.code.
