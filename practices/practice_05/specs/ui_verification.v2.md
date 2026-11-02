UI verification v2 — фактические DOM-проверки и результат

Окружение
- Адрес: http://127.0.0.1:8000/
- Код UI обновлён по v2: только server-side preview, безопасный DOM, Abort/версии запросов, подсветка [REDACTED], пример diff. node --check — OK.
- Инструменты: из-за недоступности tools.browser в Code Mode, проверки выполнены реальным headless Playwright как временная зависимость в /tmp.

Фактические DOM-результаты (Playwright)
- initial: ready=complete; counter=0/20000; warn=""; previewDisabled=true
- whitespace: counter=3/20000; previewDisabled=true; warn=""
- emoji: counter=1/20000; previewDisabled=false; warn="Текст не похож на unified diff. Его всё равно можно отправить."
- 20000: counter=20000/20000; previewDisabled=false; warn="Текст не похож на unified diff. Его всё равно можно отправить."
- 20001: counter=20001/20000; previewDisabled=true; warn="Текст не похож на unified diff. Его всё равно можно отправить."; error="Лимит 20000 символов превышен"
- sample: length=310; previewDisabled=false

Live provider и реальный preview
- /api/provider: { provider: "VseLLM", model: "openai/gpt-5", configured: true }
- Реальный preview по sample: previewVisible=true; redactionsCountText="1"; hasMarkElements=true (подсветка [REDACTED] в DOM)
- Наблюдение запроса /api/reviews (без route): тело diff == preview, не содержит sk-DEMOONLY123 (зафиксировано булевым признаком без вывода содержимого)
- Реальное review: resultVisible=true; errorVisible=false; summary содержит осмысленный разбор divide/SQL/секретов (ответ сервера — на английском в текущей версии)

Simulated transport (в отдельном контексте для гонок)
- pending preview + редактирование: previewHidden=true; redactedEmpty=true; busyCleared=true
- reset во время pending: counter="0 / 20000"; disabled=true
- fake 502 review: errorText="Сервис ревью временно недоступен. Повторите позже."; reviewBtnEnabled=true

Скриншоты
- Предпросмотр: /tmp/practice05-ui-check/ui-v2-preview.png
- Результат ревью: /tmp/practice05-ui-check/ui-v2-review.png

Замечания и безопасность
- Подсветка [REDACTED] выполнена через безопасные узлы <mark> и textContent; HTML из данных не вставляется.
- Исходный diff не отправляется во внешние сервисы; для review отправляется только очищенный.
- Нет локальных хранилищ/логов сырых данных.
