// Stage 4: Shockbolt tiles in the map (canvas pixels), text <-> tiles toggle.
import { realErrors, serve, open, screen, sleep, keys, type, waitText, wipeDbs } from './lib.mjs';
const shot = (n) => new URL(`../shots/${n}.png`, import.meta.url).pathname;
const srv = await serve();
let fail = 0;
const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fail++; };
// Colour variety of the map canvas: tiles have many distinct colours, text few
const variety = (page) => page.evaluate(() => {
	const cv = document.querySelector('#t-main canvas'), c = cv.getContext('2d');
	const d = c.getImageData(0, 0, cv.width, cv.height).data, set = new Set();
	for (let i = 0; i < d.length; i += 4 * 7) set.add((d[i] >> 3) << 10 | (d[i + 1] >> 3) << 5 | (d[i + 2] >> 3));
	return set.size;
});
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
	await sleep(800);
	const p0 = await page.evaluate(() => window.__picts || 0);
	const v0 = await variety(page);
	ok(p0 > 200, `town drawn with pict() cells: ${p0}`);
	ok(v0 > 150, `map canvas colour variety (tiles): ${v0}`);
	await page.screenshot({ path: shot('s4-town') });
	await type(page, '>');
	await waitText(page, /50'|L1/, 0, 30000);
	await sleep(800);
	await page.screenshot({ path: shot('s4-dungeon') });
	ok(await variety(page) > 100, 'dungeon level 1 in tiles');
	// Tiles off -> text at the next prompt
	await page.click('#btn-tiles'); await keys(page, ['Escape'], 800);
	const pt = await page.evaluate(() => window.__picts || 0);
	await keys(page, [{ key: 'r', ctrlKey: true }], 800);
	const pt2 = await page.evaluate(() => window.__picts || 0);
	await page.screenshot({ path: shot('s4-text') });
	ok(pt2 === pt && /\.@|@\.|#@|@#/.test(await screen(page)), `Tiles: off -> text (no pict() on ^R redraw)`);
	await page.click('#btn-tiles'); await keys(page, ['Escape'], 800);
	await keys(page, [{ key: 'r', ctrlKey: true }], 800);
	const pb = await page.evaluate(() => window.__picts || 0);
	ok(pb > pt2, `Tiles: on again (${pb - pt2} pict cells on ^R redraw)`);
	const crashed = await page.evaluate(() => /crashed/.test(document.getElementById('status').textContent));
	ok(!crashed, 'no crash');
	ok(realErrors(errors).length === 0, 'no console errors ' + JSON.stringify(realErrors(errors)));
	console.log('wiped', (await wipeDbs(page)).length, 'dbs');
	await browser.close();
} finally { srv.kill(); }
process.exit(fail ? 1 : 0);
