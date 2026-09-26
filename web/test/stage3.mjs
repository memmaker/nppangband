// Stage 3: Enter command menu, inventory/equipment screens with item action menus.
import { realErrors, serve, open, screen, sleep, keys, type, waitText, wipeDbs } from './lib.mjs';
const shot = (n) => new URL(`../shots/${n}.png`, import.meta.url).pathname;
const srv = await serve();
let fail = 0;
const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fail++; };
const invText = async (page) => (await screen(page, 1));
const count = (s) => { const m = /(\d+) Rations of Food/.exec(s); return m ? +m[1] : (/a Ration of Food/.test(s) ? 1 : 0); };
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

	// Enter: command menu, groups
	await keys(page, ['Enter'], 300);
	let s = await waitText(page, /Action commands/);
	ok(/Use magic\/Pray[\s\S]*Use item[\s\S]*Manage items[\s\S]*Information[\s\S]*Utility/.test(s), 'Enter opens the command menu (all groups)');
	await page.screenshot({ path: shot('s3-menu') });
	await keys(page, ['2', 'Enter'], 300);
	s = await waitText(page, /Explore the level/);
	ok(/Rest for a while[\s\S]*Go down staircase/.test(s), 'Action commands list incl. Explore (H)');
	await page.screenshot({ path: shot('s3-menu-action') });
	const lines = s.split('\n'); const want = lines.findIndex((l) => /Explore the level/.test(l)); const first = lines.findIndex((l) => /Search for traps/.test(l));
	await keys(page, Array(Math.max(0, want - first)).fill('2').concat(['Enter']), 150);
	await sleep(800);
	s = await screen(page);
	ok(!/Explore the level/.test(s), 'menu command runs and the menu closes: ' + s.split('\n')[0].trim());
	await keys(page, ['Escape', 'Escape'], 200);

	// Inventory screen
	const food0 = count(await invText(page));
	await keys(page, ['i'], 400);
	s = await waitText(page, /\(Inventory\)/);
	ok(/> ?a\) /.test(s), 'inventory screen with cursor on a)');
	await page.screenshot({ path: shot('s3-inven') });
	await keys(page, ['a'], 400);
	s = await waitText(page, /E\) Eat/);
	ok(/I\) Examine/.test(s) && /d\) Drop/.test(s), 'item menu for food: Eat, Drop, Examine');
	await page.screenshot({ path: shot('s3-itemmenu') });
	await keys(page, ['E'], 800);
	await keys(page, ['Escape'], 300);
	const food1 = count(await invText(page));
	ok(food1 === food0 - 1, `Eat from the item menu: rations ${food0} -> ${food1}`);

	await keys(page, ['i', '2', '8', 'Enter'], 300);
	s = await waitText(page, /\) Examine/);
	ok(true, 'Enter on the cursor opens the item menu');
	await keys(page, ['Escape', 'Escape'], 300);

	// Equipment: take off the body armour via the menu key
	await keys(page, ['e'], 400);
	s = await waitText(page, /\(Equipment\)/);
	await page.screenshot({ path: shot('s3-equip') });
	const eqLine = s.split('\n').find((l) => /On body/.test(l)) || '';
	const lab = (/([a-z])\) On body/.exec(eqLine) || [])[1];
	const body = (/On body\s*: (?:an? )?([A-Z][a-z]+)/.exec(eqLine) || [])[1] || 'Mail';
	ok(!!lab, 'equipment lists body armour at ' + lab + ' | ' + eqLine.trim());
	await keys(page, [lab || 'f'], 400);
	s = await waitText(page, /t\) Take off/);
	ok(!/w\) Wear/.test(s), 'equipment item menu: Take off, no Wear');
	await keys(page, ['t'], 900);
	await keys(page, ['Escape'], 300);
	ok(new RegExp(body).test(await invText(page)), body + ' moved to the pack');
	await page.screenshot({ path: shot('s3-after') });

	await keys(page, ['i', '/'], 400);
	await waitText(page, /\(Equipment\)/);
	ok(true, "'/' switches inventory -> equipment");
	await keys(page, ['Escape'], 300);
	const crashed = await page.evaluate(() => /crashed/.test(document.getElementById('status').textContent));
	ok(!crashed, 'no crash');
	ok(realErrors(errors).length === 0, 'no console errors ' + JSON.stringify(realErrors(errors)));
	console.log('wiped', (await wipeDbs(page)).length, 'dbs');
	await browser.close();
} finally { srv.kill(); }
process.exit(fail ? 1 : 0);
