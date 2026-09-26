// node step.mjs "<keys>" ... : each arg is typed, then the screen printed. ~ = Escape, \n = Enter
import { serve, open, screen, sleep, type, wipeDbs } from './lib.mjs';
const srv = await serve();
try {
	const { browser, page, errors } = await open();
	await sleep(1500);
	for (const a of process.argv.slice(2)) {
		await type(page, a.replace(/~/g, '\x1b').replace(/\\n/g, '\r'), 60);
		await sleep(800);
		console.log('==== after', JSON.stringify(a));
		console.log((await screen(page)).split('\n').filter((l) => l.trim()).join('\n'));
	}
	await page.screenshot({ path: new URL('../shots/step.png', import.meta.url).pathname });
	if (!process.env.KEEP) console.log('wiped', await wipeDbs(page));
	console.log('errors:', errors.filter((e) => !/404/.test(e)));
	await browser.close();
} finally { srv.kill(); }
