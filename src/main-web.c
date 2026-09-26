/* File: main-web.c */

/*
 * Browser (Emscripten/WASM) front end for NPPAngband.
 *
 * Adapted from the Zangband web port (itself from TinyAngband).  All
 * drawing is done by JavaScript on one <canvas> per term (see
 * web/nppangband.js).  Blocking input uses Asyncify: when the game waits
 * for a key we sleep in emscripten_sleep(), which yields to the browser.
 *
 * The module registers itself as "web"; lib/pref/pref.prf loads the X11
 * keysym macros (pref-x11.prf) for it, since special keys are sent in the
 * X11 keysym macro format.  font-x11.prf is not loaded: it maps walls and
 * floors to glyphs of the X11 font that a web font does not have.
 */

#include "angband.h"
#include "main.h"

#ifdef USE_WEB

#include <emscripten.h>

#define WEB_TERMS 8		/* terms 1-7: see web_window_flags[] */

static term web_term[WEB_TERMS];

/* Pending "save now" request from the page (tab hidden / closing) */
static int web_want_save = 0;

/* Last time we yielded to the browser */
static double web_last_yield = 0;

static void web_switch_graphics(int on);


/* ---- JavaScript side (implemented in web/nppangband.js) ---- */

EM_JS(void, js_text, (int t, int x, int y, int n, int a, const char *s), {
	Module.qb.text(t, x, y, n, a, s);
});

EM_JS(void, js_wipe, (int t, int x, int y, int n), {
	Module.qb.wipe(t, x, y, n);
});

EM_JS(void, js_clear, (int t), {
	Module.qb.clear(t);
});

EM_JS(void, js_curs, (int t, int x, int y, int w), {
	Module.qb.curs(t, x, y, w);
});

/* big: the tile covers this cell and the next (use_bigtile, 255/0xFF pad) */
EM_JS(void, js_pict, (int t, int x, int y, int n, const byte *ap, const char *cp,
                      const byte *tap, const char *tcp, int big), {
	Module.qb.pict(t, x, y, n, ap, cp, tap, tcp, big);
});

/* Tiles (1) or text (0) as the page's Tiles button says; -1: no change */
EM_JS(int, js_tiles_wanted, (void), {
	return Module.qb.tilesWanted();
});

EM_JS(int, js_tiles_switch, (void), {
	return Module.qb.tilesSwitch();
});

EM_JS(void, js_fresh, (int t), {
	Module.qb.fresh(t);
});

EM_JS(void, js_bell, (void), {
	Module.qb.bell();
});

EM_JS(void, js_sound, (const char *name), {
	Module.qb.sound(UTF8ToString(name));
});

EM_JS(void, js_depth, (int depth), {
	Module.qb.depth(depth);
});

EM_JS(void, js_color, (int i, int r, int g, int b), {
	Module.qb.color(i, r, g, b);
});

EM_JS(int, js_term_cols, (int t), {
	return Module.qb.termCols(t);
});

EM_JS(int, js_term_rows, (int t), {
	return Module.qb.termRows(t);
});

/* Layout changes after a browser resize */
EM_JS(int, js_layout_pending, (int t), {
	return Module.qb.layoutPending(t);
});

EM_JS(int, js_pending_cols, (int t), {
	return Module.qb.pendingCols(t);
});

EM_JS(int, js_pending_rows, (int t), {
	return Module.qb.pendingRows(t);
});

EM_JS(void, js_apply_layout, (int t, int cols, int rows), {
	Module.qb.applyLayout(t, cols, rows);
});

/* Next queued input: -1 none, else key */
EM_JS(int, js_next_event, (int at_cmd), {
	return Module.qb.nextEvent(at_cmd);
});

EM_JS(void, js_quit, (const char *msg, int dead), {
	Module.qb.quit(msg ? UTF8ToString(msg) : "", dead);
});

EM_JS(void, js_plog, (const char *msg), {
	Module.qb.plog(UTF8ToString(msg));
});

EM_JS(void, js_sync, (void), {
	Module.qb.sync();
});


/* Persist the save directories (called after every save) */
void web_sync_files(void)
{
	js_sync();
}


/* Called from JS when the page is about to be hidden or closed */
EMSCRIPTEN_KEEPALIVE void web_request_save(void)
{
	web_want_save = 1;
}


/* The game waits for a command (not inside a prompt or menu) */
static bool web_at_cmd(void)
{
	return (inkey_flag && character_generated);
}


/*
 * Resize the terms to the layout the page computed after a browser resize.
 * Term_resize() runs the resize hooks, which redraw the contents.  The main
 * window changes its size only at the command prompt; a cell-size change
 * alone applies at once.
 */
static void web_apply_layout(void)
{
	int i;
	term *old = Term;
	bool at_prompt = web_at_cmd();
	bool main_changed = FALSE, sub_changed = FALSE;

	for (i = 0; i < WEB_TERMS; i++)
	{
		term *t = &web_term[i];
		int cols, rows;

		if (!js_layout_pending(i)) continue;

		cols = js_pending_cols(i);
		rows = js_pending_rows(i);
		if (cols < 1) cols = 1;
		if (rows < 1) rows = 1;

		if (!i)
		{
			if (cols < 80) cols = 80;
			if (rows < 24) rows = 24;

			if (((cols != t->wid) || (rows != t->hgt)) && !at_prompt) continue;
		}

		/* New canvas size and cell size (the canvas starts blank) */
		js_apply_layout(i, cols, rows);

		Term_activate(t);
		if ((cols == t->wid) && (rows == t->hgt)) Term_redraw();
		else
		{
			Term_resize(cols, rows);
			if (i) sub_changed = TRUE;
			else main_changed = TRUE;
		}
	}

	Term_activate(old);

	/* No resize hooks in this z-term: redraw as main-sdl.c does */
	if (character_dungeon)
	{
		if (main_changed) do_cmd_redraw();
		else if (sub_changed)
		{
			p_ptr->window |= (PW_INVEN | PW_EQUIP | PW_PLAYER_0 | PW_MESSAGE |
			                  PW_MONSTER | PW_OBJECT | PW_MONLIST | PW_ITEMLIST);
			if (at_prompt) handle_stuff();
		}
	}
}


/* Move queued browser input into the main term's key queue */
static int web_pump(void)
{
	int k, got = 0;
	term *old = Term;

	web_apply_layout();

	Term_activate(&web_term[0]);

	while ((k = js_next_event(web_at_cmd())) >= 0)
	{
		Term_keypress(k);
		got = 1;
	}

	/* Tiles <-> text: only while waiting for a command */
	if (web_at_cmd() && !got)
	{
		int on = js_tiles_switch();

		if ((on >= 0) && (on != (use_graphics != GRAPHICS_NONE)))
		{
			web_switch_graphics(on);
			got = 1;
		}
	}

	/* Safe autosave: only while waiting for a command */
	if (web_want_save && web_at_cmd() && !p_ptr->is_dead && !got &&
	    (Term->key_head == Term->key_tail))
	{
		web_want_save = 0;
		Term_keypress(KTRL('S'));
		got = 1;
	}

	Term_activate(old);
	return got;
}

static void web_yield(int ms)
{
	emscripten_sleep(ms);
	web_last_yield = emscripten_get_now();
}

static errr web_check_events(int wait)
{
	if (web_pump()) return (0);

	if (!wait)
	{
		/* Let the browser paint now and then during long actions */
		if (emscripten_get_now() - web_last_yield > 50) web_yield(0);
		return (web_pump() ? 0 : 1);
	}

	while (1)
	{
		web_yield(10);
		if (web_pump()) return (0);
	}
}

static void web_react(void)
{
	int i;

	for (i = 0; i < 16; i++)
		js_color(i, angband_color_table[i][1], angband_color_table[i][2],
		         angband_color_table[i][3]);
}

static int web_idx(void)
{
	return (int)(Term - web_term);
}

static errr Term_xtra_web(int n, int v)
{
	switch (n)
	{
		case TERM_XTRA_NOISE: js_bell(); return (0);
		case TERM_XTRA_CLEAR: js_clear(web_idx()); return (0);
		case TERM_XTRA_FRESH:
			js_fresh(web_idx());

			/* The page's Sound button is the only switch (off by default) */
			if (character_generated) op_ptr->opt[OPT_use_sound] = TRUE;

			/* The page plays town music at depth 0 */
			js_depth(character_generated ? p_ptr->depth : -1);
			return (0);
		case TERM_XTRA_BORED: return (web_check_events(0));
		case TERM_XTRA_EVENT: return (web_check_events(v));
		case TERM_XTRA_FLUSH:
			while (js_next_event(0) >= 0) ;
			return (0);
		case TERM_XTRA_DELAY:
			js_fresh(web_idx());
			if (v > 0) web_yield(v);
			return (0);
		case TERM_XTRA_REACT: web_react(); return (0);
	}

	return (1);
}

static errr Term_curs_web(int x, int y)
{
	js_curs(web_idx(), x, y, 1);
	return (0);
}

static errr Term_bigcurs_web(int x, int y)
{
	js_curs(web_idx(), x, y, 2);
	return (0);
}

static errr Term_wipe_web(int x, int y, int n)
{
	js_wipe(web_idx(), x, y, n);
	return (0);
}

static errr Term_text_web(int x, int y, int n, byte a, cptr s)
{
	js_text(web_idx(), x, y, n, a, s);
	return (0);
}

static errr Term_pict_web(int x, int y, int n, const byte *ap, const char *cp,
                          const byte *tap, const char *tcp)
{
	js_pict(web_idx(), x, y, n, ap, cp, tap, tcp, use_bigtile ? 1 : 0);
	return (0);
}


/* Sound events: names from angband_sound_name[] (sound.cfg in the preload) */
static void web_sound(int v)
{
	if ((v > 0) && (v < MSG_MAX) && angband_sound_name[v][0])
		js_sound(angband_sound_name[v]);
}


/* Tiles in big-tile mode, or text */
static void web_graphics(int on)
{
	if (on)
	{
		/* Shockbolt tiles (graf-shb.prf via graf.prf), square in big-tile mode */
		use_graphics = arg_graphics = GRAPHICS_SHOCKBOLT;
		ANGBAND_GRAF = "shb";
		use_transparency = TRUE;
		use_bigtile = TRUE;
	}
	else
	{
		use_graphics = arg_graphics = GRAPHICS_NONE;
		use_transparency = FALSE;
		use_bigtile = FALSE;
	}
}

/* The page's Tiles button, applied at the command prompt */
static void web_switch_graphics(int on)
{
	web_graphics(on);
	reset_visuals(TRUE);
	do_cmd_redraw();
}


static void hook_plog(cptr str)
{
	if (str) js_plog(str);
}

static void hook_quit(cptr str)
{
	int i;

	for (i = 0; i < WEB_TERMS; i++) (void)term_nuke(&web_term[i]);

	/* After death the tombstone and scores already waited for a key */
	js_sync();
	js_quit(str, p_ptr->is_dead);
}


const char help_web[] = "Browser front end";

/*
 * What each sub-window shows (TERMS in web/nppangband.js).  Set for new
 * characters by web_new_character(); a savefile brings its own flags.
 */
static u32b web_window_flags[WEB_TERMS] =
{
	0,
	PW_INVEN,					/* 1 Inventory */
	PW_MESSAGE,					/* 2 Messages */
	PW_MONLIST,					/* 3 Visible */
	PW_MONSTER | PW_OBJECT,		/* 4 Recall */
	PW_EQUIP,					/* 5 Equipment */
	PW_PLAYER_0,				/* 6 Character */
	PW_ITEMLIST					/* 7 Objects */
};

/* New character (dungeon.c play_game()): the web window layout */
void web_new_character(void)
{
	u32b flags[ANGBAND_TERM_MAX];
	int i;

	for (i = 0; i < ANGBAND_TERM_MAX; i++)
		flags[i] = (i < WEB_TERMS) ? web_window_flags[i] : 0L;

	subwindows_set_flags(flags, ANGBAND_TERM_MAX);
}

errr init_web(int argc, char **argv)
{
	int i;

	(void)argc;
	(void)argv;

	/* RVIP defaults for new characters: no -more- stops, centred map */
	options[OPT_auto_more].normal = TRUE;
	options[OPT_center_player].normal = TRUE;

	web_react();

	/* Tiles unless the page says text */
	web_graphics(js_tiles_wanted());

	for (i = 0; i < WEB_TERMS; i++)
	{
		term *t = &web_term[i];
		int cols = js_term_cols(i), rows = js_term_rows(i);

		if (!i)
		{
			if (cols < 80) cols = 80;
			if (rows < 24) rows = 24;
		}

		term_init(t, cols, rows, (i == 0) ? 1024 : 16);

		t->soft_cursor = TRUE;
		t->attr_blank = TERM_WHITE;
		t->char_blank = ' ';

		t->xtra_hook = Term_xtra_web;
		t->curs_hook = Term_curs_web;
		t->bigcurs_hook = Term_bigcurs_web;
		t->wipe_hook = Term_wipe_web;
		t->text_hook = Term_text_web;
		t->pict_hook = Term_pict_web;
		t->higher_pict = TRUE;

		Term_activate(t);
		angband_term[i] = t;
	}

	Term_activate(&web_term[0]);

	web_last_yield = emscripten_get_now();

	sound_hook = web_sound;
	quit_aux = hook_quit;
	plog_aux = hook_plog;

	return (0);
}

#endif /* USE_WEB */
