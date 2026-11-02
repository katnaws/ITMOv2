UI спецификация (after v2) — ревьюер diff с предварительным превью

Endpoint и контракт (согласовано)
- GET /api/provider → { provider: 'VseLLM', model: string, configured: boolean }
- POST /api/preview { diff: string } → { redacted: string, redactions_count: integer ≥ 0 }
- POST /api/reviews { diff: string } → { summary: string, risks: Array<{ file?: string, line?: number, evidence?: string, risk: string }>, checks: Array<string> }
- Ошибки: 422 UNPROCESSABLE_CONTENT, 413 CONTENT_TOO_LARGE, 502 LLM_UPSTREAM_ERROR, 503 PROVIDER_NOT_CONFIGURED
- Лимит: 20000 Unicode code points; клиент блокирует >20000, сервер возвращает 413

Видимая функциональность
1) Ввод diff
   - Textarea «Вставьте unified diff (git diff/PR patch)»; счётчик символов (Unicode), мягкое предупреждение «Текст не похож на unified diff. Его всё равно можно отправить.»
   - Кнопки: «Проверить и скрыть секреты», «Загрузить пример», «Очистить»
   - «Загрузить пример» вставляет содержательный Python‑diff с: делением на ноль, SQL в f‑string, фиктивным секретом — чтобы реальное ревью выдавало понятные находки.
2) Предпросмотр
   - После успешного POST /api/preview показывается «Очищенный diff» (безопасный текст), «Количество замен: N [REDACTED]»
   - Кнопки: «Отправить очищенный на ревью», «Изменить исходный diff»
   - Любое редактирование исходного diff скрывает предпросмотр и отключает отправку очищенного.
3) Результат ревью
   - Показ summary/risks/checks. Исходный diff/секреты не показываются. Уведомление: очистка может пропустить неизвестные типы секретов.

Состояния/индикаторы
- Idle → PreviewLoading/PreviewReady → ReviewLoading → Success/Error
- Видимые индикаторы загрузки; кнопки на время запросов disabled; дедупликация запросов
- Управление гонками: AbortController и request version для инвалидации запоздалых ответов после редактирования/сброса

Доступность и безопасность
- Русский UI, label/aria, aria‑live для статусов и ошибок; видимый фокус
- Безопасный рендеринг (textContent), никаких innerHTML для данных
- Не хранить сырой diff/ключи локально; не логировать сырой ввод или ответы
- Отображение статуса провайдера (GET /api/provider): provider/model/configured; без обещаний доступности даже при наличии ключа

Клиентская валидация
- Пустота/пробелы → disabled и подсказка
- Unicode лимит 20000 код‑поинтов → немедленное сообщение и disable
- «Похож на diff» → мягкое предупреждение, отправка разрешена

Ограничения/не делаем
- Не показывать список обнаруженных секретов отдельно
- Не отправлять исходный diff во внешние сервисы
- Не использовать production mock и не показывать баннеры «заглушка»
