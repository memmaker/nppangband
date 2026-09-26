// Stage 2: auto-explore (H) and walking to stairs (< / > away from stairs).
import { realErrors, serve, open, screen, sleep, keys, type, waitText, wipeDbs } from './lib.mjs';
const shot = (n) => new URL(`../shots/${n}.png`, import.meta.url).pathname;
const srv = await serve();
let fail = 0;
const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fail++; };
const depth = (p) => p.evaluate(() => Module.ccall ? null : null);
// Debug command ^A z: zap the monsters in sight (the test is about walking, not fighting)
async function zap(page) {
	await keys(page, ['Escape', { key: 'a', ctrlKey: true }], 200);
	for (let i = 0; i < 4; i++) {
		const top = (await screen(page)).split('\n')[0];
		if (/Are you sure/.test(top)) await keys(page, ['y'], 200);
		else if (/-more-/.test(top)) await keys(page, [' '], 150);
		else break;
	}
	await keys(page, ['z'], 300);
	await keys(page, ['Escape'], 100);
}
try {
	let { browser, page, errors } = await open();
	await wipeDbs(page); await page.reload();
	await page.waitForFunction(() => window.__shadowReady && window.__screen(0).join('').includes('Press any key'), null, { timeout: 30000 });
	await type(page, ' '); await waitText(page, /Female/);
	await type(page, 'aaaa'); await waitText(page, /Enter' to accept/);
	await type(page, '\r'); await waitText(page, /Enter a name/);
	await type(page, 'Tester\r'); await waitText(page, /to continue\]/);
	await type(page, ' ');
	await waitText(page, /Warrior[\s\S]*Town/);
	await sleep(500);
	// '>' in town: walk to the down staircase and take it
	await type(page, '>');
	let s = await waitText(page, /50 ft|Lev 1\b|L1\b/, 0, 30000).catch((e) => String(e));
	ok(/50 ft|Lev 1\b|L1\b/.test(s), "town '>': walked to the stairs and went down");
	await page.screenshot({ path: shot('s2-level1') });
	// Explore: many presses of H (stops on monsters/messages); Escape clears prompts
	let prev = '', moved = 0;
	for (let i = 0; i < 40; i++) {
		await keys(page, ['Escape', 'Escape', 'H'], 60);
		await sleep(700);
		const cur = await screen(page);
		if (cur !== prev) moved++;
		if (/monster nearby/.test(cur.split('\n')[0])) await zap(page);
		prev = cur;
		if (i === 10) await page.screenshot({ path: shot('s2-explore-a') });
	}
	await page.screenshot({ path: shot('s2-explore-b') });
	ok(moved > 10, `H changed the map ${moved}/40 times`);
	console.log((await screen(page)).split('\n').slice(0, 3).join('\n'));
	// '>' again: walk to a known (or explore for a) down staircase
	let before = await screen(page);
	for (let i = 0; i < 15 && !/100 ft|Lev 2\b|L2\b/.test(await screen(page)); i++) {
		await keys(page, ['Escape', 'Escape', '>'], 60); await sleep(1500);
		const t = (await screen(page)).split('\n')[0].trim(); console.log('>', t);
		if (/Jackal|monster|wakes|hits|bites|misses/.test(t)) await zap(page);
	}
	s = await screen(page);
	ok(/100 ft|Lev 2\b|L2\b/.test(s), "'>' on level 1: reached 100 ft");
	await page.screenshot({ path: shot('s2-level2') });
	for (let i = 0; i < 15 && !/ 50 ft|Lev 1\b|L1\b/.test(await screen(page)); i++) {
		await keys(page, ['Escape', 'Escape', '<'], 60); await sleep(1500);
		const t = (await screen(page)).split('\n')[0].trim(); console.log('<', t);
		if (/monster|wakes|hits|bites|misses/.test(t)) await zap(page);
	}
	s = await screen(page);
	ok(/ 50 ft|Lev 1\b|L1\b/.test(s), "'<' on level 2: back up to 50 ft");
	const crashed = await page.evaluate(() => /crashed/.test(document.getElementById('status').textContent));
	ok(!crashed, 'no crash');
	console.log(s);
	ok(realErrors(errors).length === 0, 'no console errors ' + JSON.stringify(realErrors(errors)));
	console.log('wiped', (await wipeDbs(page)).length, 'dbs');
	await browser.close();
} finally { srv.kill(); }
process.exit(fail ? 1 : 0);
