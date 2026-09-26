#!/usr/bin/env python3
"""Random-key driver for the native ASan build (web/asan.sh).

  python3 web/asan-keys.py SEED NEWKEYS RESTOREDKEYS [weights]

Runs the curses build in a pty (pyte screen), creates a character through
the birth menus, sends NEWKEYS random keys, saves with Ctrl-X, restarts on
the save and sends RESTOREDKEYS more.  ASan reports go to
$ASAN/asan.<pid>; the script prints them and exits 1 if any appeared.
Weights (optional): extra keys to favour, e.g. 'H<>' or '\\r' for menus."""
import os, pty, sys, time, random, select, signal, glob, pyte

ASAN = os.environ.get('ASAN', '/tmp/npp-asan')
RUN = f'{ASAN}/run'
COLS, ROWS = 100, 30
seed, nnew, nold = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
extra = sys.argv[4].encode().decode('unicode_escape') if len(sys.argv) > 4 else ''
rng = random.Random(seed)

# printable keys + a few controls; no ^C ^Z ^\ ^Y ^S ^Q (tty), no ^X (save+quit, done on purpose)
KEYS = [chr(c) for c in range(32, 127)] + ['\x1b'] * 12 + ['\r'] * 6 + list('12346789' * 6) + \
       ['\x01', '\x02', '\x04', '\x05', '\x06', '\x07', '\x08', '\x09', '\x0b', '\x0c', '\x0e', '\x10', '\x12', '\x14', '\x15', '\x16', '\x17']
KEYS += list(extra) * 10

def spawn():
    env = dict(os.environ, HOME=f'{ASAN}/home', TERM='xterm', LINES=str(ROWS), COLUMNS=str(COLS),
               ASAN_OPTIONS=f'log_path={ASAN}/asan:detect_leaks=0:abort_on_error=0')
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(RUN)
        os.execve('./nppangband', ['./nppangband', '-mgcu', f'-uT{seed}'], env)
    import fcntl, termios, struct
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack('HHHH', ROWS, COLS, 0, 0))
    return pid, fd

scr = pyte.Screen(COLS, ROWS); st = pyte.ByteStream(scr)

def pump(fd, t=0.02):
    end = time.time() + t
    while True:
        r, _, _ = select.select([fd], [], [], max(0, end - time.time()))
        if not r: return True
        try: d = os.read(fd, 65536)
        except OSError: return False
        if not d: return False
        st.feed(d)

def text(): return '\n'.join(scr.display)

def alive(pid):
    try: return os.waitpid(pid, os.WNOHANG) == (0, 0)
    except ChildProcessError: return False

def send(fd, s):
    try: os.write(fd, s.encode('latin-1'))
    except OSError: pass

def phase(n, new):
    pid, fd = spawn()
    deaths = 0
    t0 = time.time()
    births = 0
    for i in range(n + 4000):
        if not pump(fd, 0.01) or not alive(pid): break
        if time.time() - t0 > 600: break
        s = text()
        if births < 80 and ('Please select your character' in s or 'Point-based' in s or 'to continue]' in s or 'What is your name' in s \
           or 'Press any key' in s or 'Accept character' in s):
            births += 1
            send(fd, '\r' if births % 7 else ' ')
            continue
        if i >= n: break
        send(fd, rng.choice(KEYS))
    # save and quit
    for _ in range(6):
        send(fd, '\x1b'); pump(fd, 0.05)
    send(fd, '\x18'); pump(fd, 0.5)
    for _ in range(10):
        if not alive(pid): break
        send(fd, 'y\r\x1b'); pump(fd, 0.3)
    last = text()
    if alive(pid): os.kill(pid, signal.SIGKILL)
    try: os.waitpid(pid, 0)
    except ChildProcessError: pass
    if os.environ.get('SHOW'): print(last)
    return births

signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(TimeoutError()))
before = set(glob.glob(f'{ASAN}/asan.*'))
b1 = phase(nnew, True)
b2 = phase(nold, False)
new = sorted(set(glob.glob(f'{ASAN}/asan.*')) - before)
print(f'seed {seed}: {nnew}+{nold} keys, birth screens {b1}/{b2}, asan reports: {len(new)}')
for f in new:
    print(open(f).read()[:4000])
sys.exit(1 if new else 0)
