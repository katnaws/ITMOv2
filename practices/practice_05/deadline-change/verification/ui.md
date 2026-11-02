# UI verification — deadline change (demo, headless Playwright)

Context
- React build + Python bridge started via: `python3 practices/practice_04/dashboard/server.py --port 8765`
- Demo URL: http://127.0.0.1:8765/?mode=demo
- PID and log: see /tmp/practice05-studyspace/dashboard-8765.log
- Screenshots: /tmp/practice05-studyspace/modal.png, /tmp/practice05-studyspace/success.png

Real browser checks (headless, deterministic by task ID)
- Tooling: Playwright 1.41.2 under /tmp/practice05-ui-check; used Chrome channel.
- Script location: /tmp/practice05-studyspace/ui-check-final.js
- Selection: picked specific active (todo/in_progress) and done tasks via GET /api/state?mode=demo; targeted rows using aria-label "Перенести срок: <title>" and validated updates by task ID after each action.
- Output:

```
{
  "demoUrl": "http://127.0.0.1:8765/?mode=demo",
  "assertions": {
    "disabledInit": true,
    "modesLocked": true,
    "sameVal": true,
    "emptyDisabled": true,
    "enabledAfterChange": true,
    "toast1": "Дедлайн перенесён",
    "futureOk": true,
    "todayOk": true,
    "pastOk": true,
    "doneOk": true,
    "simulated": {
      "errText": "Сервис недоступен. Попробуйте ещё раз.",
      "preserved": true,
      "retryEnabled": true
    }
  }
}
```

Observed DOM/behaviors
- Modal opens; focus on `input[type=date]`.
- Initial Save disabled (same-date). Empty input disables Save. Cancel preserves original date.
- Mode buttons locked while modal open.
- Future change: real POST 200; toast shows; history updated; GET/state confirms exact deadline change; title/course/status/created_at unchanged.
- Today on active task: days_left===0, overdue===false; row not marked late (verified by GET/state for the same task ID).
- Past on active: days_left<0, overdue===true; same row marked late (verified by GET/state).
- Past on done: overdue===false; status remains done.
- SIMULATED errors in separate context using page.route:
  - 502 bridge: inline error is in Russian; date preserved; retry enabled. After unroute, retry succeeds with toast.

Limitations
- We used system Chrome channel; embedded Chromium path was not available; tests are still headless and deterministic.

URLs and artifacts
- Demo URL: http://127.0.0.1:8765/?mode=demo
- Server PID: 78694; Log: /tmp/practice05-studyspace/dashboard-8765.log
- Screenshots: /tmp/practice05-studyspace/modal.png, /tmp/practice05-studyspace/success.png
