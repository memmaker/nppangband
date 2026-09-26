// Stage 1: character creation, random keys, save (Ctrl-X), reload, restore.
import { realErrors, serve, open, screen, sleep, keys, type, waitText, wipeDbs } from './lib.mjs';
const shot = (n) => new URL(`../shots/${n}.png`, import.meta.url).pathname;
const seed = +(process.argv[2] || 1), N = +(process.argv[3] || 400);
let r = seed; const rnd = (n) => { r = (r * 1103515245 + 12345) & 0x7fffffff; return r % n; };
const srv = await serve();
let fail = 0;
const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fail++; };
try {
	let { browser, context, page, errors } = await open();
	await wipeDbs(page); await page.reload();
	await page.waitForFunction(() => window.__shadowReady && window.__screen(0).join('').includes('Press any key'), null, { timeout: 30000 });
	await type(page, ' '); await waitText(page, /Female/);
	await type(page, 'aaaa'); await waitText(page, /Enter' to accept/);
	await type(page, '\r'); await waitText(page, /Enter a name/);
	await type(page, 'Tester\r'); await waitText(page, /to continue\]/);
	await type(page, ' ');
	const town = await waitText(page, /Warrior[\s\S]*Town/);
	ok(/Rookie/.test(town), 'birth: Human Warrior in town');
	await page.screenshot({ path: shot('s1-town') });

	// Random keys: letters, digits, Escape, Enter (no Ctrl keys, no Q suicide, no S/~/@ menus that eat keys)
	const K = 'abcdefghijklmnoprtuvwxyzBCDEFGIJKLMNOPRTUVWXYZ123456789,.;:<>[]{}()+-/|\\'.split('').concat(Array(20).fill('Escape'), Array(8).fill('Enter'));
	for (let i = 0; i < N; i++) {
		await keys(page, [K[rnd(K.length)]], 15);
		if (i % 50 === 49) await keys(page, Array(4).fill('Escape'), 15);
	}
	await keys(page, Array(8).fill('Escape'), 60);
	const crashed = await page.evaluate(() => /crashed/.test(document.getElementById('status').textContent));
	ok(!crashed, `${N} random keys (seed ${seed}), no crash`);
	await page.screenshot({ path: shot('s1-random') });

	// Save + quit
	await keys(page, [{ key: 'x', ctrlKey: true }], 300);
	await waitText(page, /Press Return/);
	for (let i = 0; i < 6 && await page.evaluate(() => document.getElementById('overlay').hidden); i++) await keys(page, ['Escape'], 700);
	await page.waitForFunction(() => !document.getElementById('overlay').hidden, null, { timeout: 15000 });
	ok(true, 'Ctrl-X: "has ended" overlay');
	await sleep(1500);
	const saves = await page.evaluate(() => Module.FS.readdir('/nppangband/lib/save'));
	ok(saves.includes('0.PLAYER') || saves.some((s) => /PLAYER|Tester/.test(s)), 'savefile written: ' + saves.join(' '));

	// Reload: the character comes back
	await page.reload();
	await page.waitForFunction(() => window.__shadowReady && window.__screen(0).join('').includes('Press any key'), null, { timeout: 30000 });
	await type(page, ' ');
	await waitText(page, /LEVEL/);
	await type(page, 'C');
	const sheet = await waitText(page, /Name\s+Tester/);
	ok(/Warrior/.test(sheet), 'reload: Tester restored');
	await page.screenshot({ path: shot('s1-restored') });
	await keys(page, ['Escape']);
	ok(realErrors(errors).length === 0, 'no console errors ' + JSON.stringify(realErrors(errors)));
	console.log('wiped', (await wipeDbs(page)).length, 'dbs');
	await browser.close();
} finally { srv.kill(); }
process.exit(fail ? 1 : 0);
