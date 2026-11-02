// Run with NODE_PATH pointing to a temporary Playwright installation.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { chromium } = require('playwright');
const base = process.env.BASE_URL || 'http://127.0.0.1:8765';
const checks = [];
const shift = (day, amount) => {
  const d = new Date(day + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + amount);
  return d.toISOString().slice(0, 10);
};

(async () => {
  const browser = await chromium.launch({headless: true, channel: 'chrome'});
  try {
    const context = await browser.newContext();
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(String(error)));
    await page.goto(base + '/?mode=demo');
    await page.getByRole('button', {name: /^Перенести срок:/}).first().waitFor();
    const getState = async () => (await page.request.get(base + '/api/state?mode=demo')).json();
    const initial = await getState();
    const task = initial.tasks.find(t => t.status !== 'done');
    const done = initial.tasks.find(t => t.status === 'done');
    const row = target => page.locator('.task-row').filter({has: page.getByRole('button', {name: 'Перенести срок: ' + target.title, exact: true})});
    const open = async target => {
      await page.getByRole('button', {name: 'Перенести срок: ' + target.title, exact: true}).click();
      await page.getByRole('dialog', {name: 'Перенос дедлайна'}).waitFor();
    };
    const input = page.locator('dialog input[name="deadline"]');
    const save = page.getByRole('dialog').getByRole('button', {name: 'Сохранить', exact: true});
    await open(task);
    assert.equal(await input.inputValue(), task.deadline);
    assert.equal(await input.evaluate(el => document.activeElement === el), true);
    assert.equal(await save.isDisabled(), true);
    assert.equal(await page.getByRole('button', {name: 'Мои задания', exact: true}).isDisabled(), true);
    await input.fill('');
    assert.equal(await save.isDisabled(), true);
    await page.getByRole('button', {name: 'Отмена', exact: true}).click();
    assert.equal((await getState()).tasks.find(t => t.id === task.id).deadline, task.deadline);
    checks.push('Modal focus, unchanged/empty save disabled, mode lock and cancel without writes');

    async function move(target, date) {
      await open(target);
      await input.fill(date);
      assert.equal(await save.isEnabled(), true);
      const response = page.waitForResponse(r => r.url().includes('/api/tools/update_task_deadline') && r.request().method() === 'POST');
      await save.click();
      assert.equal((await response).status(), 200);
      await page.getByRole('dialog', {name: 'Перенос дедлайна'}).waitFor({state: 'detached'});
      await page.locator('.toast').filter({hasText: 'Дедлайн перенесён'}).waitFor();
      const state = await getState();
      const changed = state.tasks.find(t => t.id === target.id);
      assert.equal(changed.deadline, date);
      for (const key of ['id','title','course','status','created_at']) assert.equal(changed[key], target[key]);
      assert.equal(state.history.some(e => e.tool === 'update_task_deadline' && e.arguments.task_id === target.id), true);
      return changed;
    }
    const today = initial.dashboard.as_of;
    const future = shift(today, 5);
    await move(task, future);
    await page.reload();
    await page.getByRole('button', {name: 'Перенести срок: ' + task.title, exact: true}).waitFor();
    assert.equal((await getState()).tasks.find(t => t.id === task.id).deadline, future);
    assert.equal(await row(task).locator('.task-date').count(), 1);
    checks.push('Real HTTP 200, unchanged metadata, MCP history and persistence after page reload');
    const current = await move(task, today);
    assert.equal(current.days_left, 0); assert.equal(current.overdue, false);
    assert.equal(await row(task).locator('.task-date.late').count(), 0);
    const past = await move(task, shift(today, -2));
    assert.equal(past.overdue, true);
    assert.equal(await row(task).locator('.task-date.late').count(), 1);
    const completed = await move(done, shift(today, -3));
    assert.equal(completed.overdue, false);
    assert.equal(await row(done).locator('.task-date.late').count(), 0);
    checks.push('Same task ID: today is not overdue, past active is overdue, past completed remains done');

    const isolated = await browser.newContext();
    const errorPage = await isolated.newPage();
    await errorPage.goto(base + '/?mode=demo');
    await errorPage.getByRole('button', {name: 'Перенести срок: ' + task.title, exact: true}).click();
    const errorInput = errorPage.locator('dialog input[name="deadline"]');
    await errorInput.fill(future);
    await errorPage.route('**/api/tools/update_task_deadline*', route => route.fulfill({status:502, contentType:'application/json', body:JSON.stringify({error:'MCP unavailable: simulated'})}));
    await errorPage.getByRole('button', {name:'Сохранить',exact:true}).click();
    await errorPage.getByRole('alert').filter({hasText:'Сервис недоступен. Попробуйте ещё раз.'}).waitFor();
    assert.equal(await errorInput.inputValue(), future);
    assert.equal(await errorPage.getByRole('button', {name:'Сохранить',exact:true}).isEnabled(), true);
    await errorPage.unroute('**/api/tools/update_task_deadline*');
    const retried = errorPage.waitForResponse(r => r.url().includes('/api/tools/update_task_deadline') && r.request().method()==='POST');
    await errorPage.getByRole('button', {name:'Сохранить',exact:true}).click();
    assert.equal((await retried).status(), 200);
    await errorPage.getByRole('dialog').waitFor({state:'detached'});
    checks.push('SIMULATED 502 in isolated context: localized error, retained date, real successful retry');
    await isolated.close();
    assert.deepEqual(errors, []);
    if (process.env.SCREENSHOT_DIR) {
      fs.mkdirSync(process.env.SCREENSHOT_DIR,{recursive:true});
      await open(task);
      await page.screenshot({path:process.env.SCREENSHOT_DIR+'/modal.png',fullPage:false});
      await page.getByRole('button',{name:'Отмена',exact:true}).click();
      await page.screenshot({path:process.env.SCREENSHOT_DIR+'/dashboard.png',fullPage:false});
    }
    console.log(JSON.stringify({ok:true,base,checks,consoleErrors:errors},null,2));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode=1; });
