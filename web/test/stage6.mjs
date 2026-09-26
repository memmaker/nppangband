// Stage 6: help page, sound (off by default, Dubtrain via the preloaded sound.cfg), music.
import { realErrors, serve, open, screen, sleep, keys, type, waitText, wipeDbs } from './lib.mjs';
const shot = (n) => new URL(`../shots/${n}.png`, import.meta.url).pathname;
const srv = await serve();
let fail = 0;
const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fail++; };
try {
	let { browser, page, errors } = await open();
	const reqs = [];
	page.on('request', (r) => reqs.push(r.url()));
	const resp = {};
	page.on('response', (r) => { resp[r.url().split('/').slice(-2).join('/')] = r.status(); });
	await wipeDbs(page); await page.reload();
	await page.waitForFunction(() => window.__shadowReady && window.__screen(0).join('').includes('Press any key'), null, { timeout: 30000 });
	const btn = async (id) => page.evaluate((id) => document.getElementById(id).textContent, id);
	ok(/off/.test(await btn('btn-sound')) && /off/.test(await btn('btn-music')), 'fresh load: Sound off, Music off');
	// Help
	await page.click('#btn-help'); await sleep(800);
	const help = await page.evaluate(() => document.getElementById('help-body').innerText);
	ok(/About the game[\s\S]*Keyboard controls[\s\S]*Credits[\s\S]*About this version/.test(help) && /Shockbolt/.test(help) && /Dubtrain/.test(help), 'Help shows the guide (sections, credits)');
	await page.screenshot({ path: shot('s6-help') });
	await keys(page, ['Escape'], 300);
	// Birth
	await type(page, ' '); await waitText(page, /Female/);
	await type(page, 'aaaa'); await waitText(page, /Enter' to accept/);
	await type(page, '\r'); await waitText(page, /Enter a name/);
	await type(page, 'Tester\r'); await waitText(page, /to continue\]/);
	await type(page, ' ');
	await waitText(page, /Warrior[\s\S]*Town/);
	await sleep(500);
	ok(!reqs.some((u) => /\/sound\//.test(u)), 'no sound files fetched while Sound is off');
	await page.click('#btn-sound'); await sleep(200);
	ok(/on/.test(await btn('btn-sound')), 'Sound: on');
	await keys(page, ['E', 'a'], 800); await keys(page, ['Escape'], 300);
	const snd = reqs.filter((u) => /\/sound\/.*\.mp3/.test(u));
	ok(snd.length > 0, 'eating fired a sound: ' + snd.map((u) => u.split('/').pop()).join(' '));
	ok(snd.every((u) => resp['sound/' + u.split('/').pop()] === 200 || resp['sound/' + u.split('/').pop()] === 206), 'sound files load (200)');
	ok(!reqs.some((u) => /\.cfg|\.prf/.test(u)), 'no .cfg/.prf fetched by the page');
	await page.click('#btn-music'); await sleep(1500);
	ok(reqs.some((u) => /music\/new_town\.ogg/.test(u)), 'Music on in town: new_town.ogg requested');
	// Reload keeps the buttons
	await page.reload();
	await page.waitForFunction(() => window.__shadowReady && window.__screen(0).join('').length > 0, null, { timeout: 30000 });
	await sleep(500);
	ok(/on/.test(await btn('btn-sound')) && /on/.test(await btn('btn-music')), 'reload: Sound/Music stay on');
	ok(realErrors(errors).filter((e) => !/play\(\)|NotAllowedError|autoplay/i.test(e)).length === 0, 'no console errors ' + JSON.stringify(realErrors(errors)));
	console.log('wiped', (await wipeDbs(page)).length, 'dbs');
	await browser.close();
} finally { srv.kill(); }
process.exit(fail ? 1 : 0);
