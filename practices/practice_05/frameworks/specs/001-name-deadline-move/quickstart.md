# UI validation

Build the existing dashboard, start the Python bridge with temporary databases,
then run frameworks/tests/browser.cjs with BASE_URL and NODE_PATH for Playwright.
Check one stable task by ID: cancel, empty/unchanged save, future date and reload,
today and past boundaries, completed status, MCP history, isolated simulated 502
and successful retry after removing the interception. Never edit personal tasks.
