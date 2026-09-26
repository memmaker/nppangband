// Stage 5: windows get the right content, prompt box covers row 0, game end (death -> new game).
import { realErrors, serve, open, screen, sleep, keys, type, waitText, wipeDbs } from './lib.mjs';
const shot = (n) => new URL(`../shots/${n}.png`, import.meta.url).pathname;
const srv = await serve();
let fail = 0;
const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fail++; };
async function birth(page) {
	await page.waitForFunction(() => window.__shadowReady && window.__screen(0).join('').includes('Press any key'), null, { timeout: 30000 });
	await type(page, ' '); await waitText(page, /Female/);
	await type(page, 'aaaa'); await waitText(page, /Enter' to accept/);
	await type(page, '\r'); await waitText(page, /Enter a name/);
	await type(page, 'Tester\r'); await waitText(page, /to continue\]/);
	await type(page, ' ');
	await waitText(page, /Warrior[\s\S]*Town/);
	await sleep(600);
}
try {
	let { browser, page, errors } = await open();
	await wipeDbs(page); await page.reload();
	await birth(page);
	// Window contents (term 1 Inventory, 2 Messages, 3 Visible, 5 Equipment, 6 Character)
	ok(/Rations of Food/.test(await screen(page, 1)), 'Inventory window: pack');
	await keys(page, ['R', '\r'], 300); await keys(page, ['Escape'], 300);
	await keys(page, [{ key: 'p', ctrlKey: true }, 'Escape'], 300);
	ok(/see|monster/i.test(await screen(page, 3)), 'Visible window: monster list');
	const wins = await page.evaluate(() => ['main', 'inv', 'msg', 'mon', 'rec', 'eqp', 'chr', 'obj'].filter((id) => document.getElementById('t-' + id)).length);
	ok(wins === 8, `8 windows in the page (${wins})`);
	const eq = await screen(page, 5), ch = await screen(page, 6);
	ok(/Sword|Dagger|Torch|Mail|Armour/.test(eq), 'Equipment term has the equipment');
	ok(/Tester/.test(ch), 'Character term has the sheet');
	// Prompt box: one cell row high over row 0
	await keys(page, ['i'], 500);
	const box = await page.evaluate(() => { const b = document.querySelector('#t-main .wm-topl'); const r = b.getBoundingClientRect(); return { hidden: b.hidden, h: r.height, w: r.width, t: b.textContent, ch: getComputedStyle(document.getElementById('t-main')).getPropertyValue('--cell-h') }; });
	ok(!box.hidden && Math.abs(box.h - parseFloat(box.ch)) < 2 && /Inventory/.test(box.t), `prompt box over row 0: ${JSON.stringify(box)}`);
	await page.screenshot({ path: shot('s5-prompt') });
	await keys(page, ['Escape'], 300);
	await page.screenshot({ path: shot('s5-windows') });

	// Death: Q (suicide) -> tombstone -> keys -> page reloads into a new birth
	await keys(page, ['Q'], 400);
	for (let i = 0; i < 4; i++) {
		const top = (await screen(page)).split('\n')[0];
		if (/retire|suicide\?/.test(top)) await keys(page, ['y'], 400);
		else if (/'@'/.test(top)) { await keys(page, ['@'], 800); break; }
		else await sleep(300);
	}
	await page.screenshot({ path: shot('s5-death') });
	const nav = page.waitForEvent('load', { timeout: 40000 }).then(() => true).catch(() => false);
	let reloaded = false;
	for (let i = 0; i < 40 && !reloaded; i++) {
		await keys(page, ['Escape', 'y', 'Enter'], 200).catch(() => {});
		reloaded = await Promise.race([nav, sleep(500).then(() => false)]);
	}
	ok(reloaded, 'death: tombstone/scores, then the page reloads');
	await page.waitForFunction(() => window.__shadowReady && /Press any key|Female/.test(window.__screen(0).join('')), null, { timeout: 30000 }).catch(() => {});
	const s = await screen(page);
	ok(/Press any key|Female|Choose/.test(s), 'new game starts after death');
	await page.screenshot({ path: shot('s5-newgame') });
	const crashed = await page.evaluate(() => /crashed/.test(document.getElementById('status').textContent));
	ok(!crashed, 'no crash');
	ok(realErrors(errors).length === 0, 'no console errors ' + JSON.stringify(realErrors(errors)));
	console.log('wiped', (await wipeDbs(page)).length, 'dbs');
	await browser.close();
} finally { srv.kill(); }
process.exit(fail ? 1 : 0);
