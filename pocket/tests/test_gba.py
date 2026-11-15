#!/usr/bin/env python3
"""End-to-end test of the Butano GBA ROM inside mGBA (headless under Xvfb), driven through mGBA's GDB stub + xdotool.
   xvfb-run -a python3 pocket/tests/test_gba.py [path/to/captco_pocket.gba]
Needs: mgba (mgba-sdl), xdotool, arm-none-eabi-nm."""
import os, re, shutil, socket, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROM = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, "..", "gba", "captco_pocket.gba")
ELF = ROM.rsplit(".", 1)[0] + ".elf"
MGBA = shutil.which("mgba") or "/usr/games/mgba"
checks = fails = 0

def check(cond, msg):
    global checks, fails
    checks += 1
    if not cond:
        fails += 1
        print("  FAIL:", msg)

def symbols():
    out = subprocess.run(["arm-none-eabi-nm", "-C", ELF], capture_output=True, text=True).stdout
    syms = {}
    for line in out.splitlines():
        m = re.match(r"([0-9a-f]+) [bBdD] \(anonymous namespace\)::(\w+)$", line.strip())
        if m:
            syms[m.group(2)] = int(m.group(1), 16)
    return syms

class Gdb:
    def __init__(self, port=2345):
        for _ in range(100):
            try:
                self.s = socket.create_connection(("127.0.0.1", port), timeout=5)
                break
            except OSError:
                time.sleep(0.2)
        else:
            raise RuntimeError("cannot connect to mGBA GDB stub")
        self.running = False
    def _send(self, payload: bytes):
        cs = sum(payload) & 255
        self.s.sendall(b"$" + payload + b"#" + (b"%02x" % cs))
    def _recv(self, timeout=5):
        self.s.settimeout(timeout)
        buf = b""
        while True:
            c = self.s.recv(1)
            if not c:
                raise RuntimeError("gdb closed")
            if c == b"$":
                buf = b""
                while True:
                    c = self.s.recv(1)
                    if c == b"#":
                        self.s.recv(2)
                        self.s.sendall(b"+")
                        return buf
                    buf += c
    def cont(self):
        if not self.running:
            self._send(b"c")
            self.running = True
    def halt(self):
        if self.running:
            self.s.sendall(b"\x03")
            while True:
                p = self._recv()
                if p[:1] in (b"T", b"S"):
                    break
            self.running = False
    def read(self, addr, n):
        was = self.running
        self.halt()
        self._send(b"m%x,%x" % (addr, n))
        r = self._recv()
        if was: self.cont()
        return bytes.fromhex(r.decode())
    def write(self, addr, data: bytes):
        was = self.running
        self.halt()
        self._send(b"M%x,%x:" % (addr, len(data)) + data.hex().encode())
        self._recv()
        if was: self.cont()

class Emu:
    def __init__(self, rom, sav_dir):
        self.rom = os.path.join(sav_dir, "t.gba")
        shutil.copy(rom, self.rom)
        env = dict(os.environ, SDL_AUDIODRIVER="dummy", LIBGL_ALWAYS_SOFTWARE="1")
        self.p = subprocess.Popen([MGBA, "-2", "-g", self.rom], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.gdb = Gdb()
        self.gdb.cont()
        self.sym = symbols()
        time.sleep(2.0)
    def key(self, name, hold=0.12, wait=0.25):
        subprocess.run(["xdotool", "keydown", name]); time.sleep(hold); subprocess.run(["xdotool", "keyup", name]); time.sleep(wait)
    def hold(self, name, secs):
        subprocess.run(["xdotool", "keydown", name]); time.sleep(secs); subprocess.run(["xdotool", "keyup", name])
    def geti(self, name):
        v = int.from_bytes(self.gdb.read(self.sym[name], 4), "little", signed=True); return v
    def getb(self, name): return self.gdb.read(self.sym[name], 1)[0]
    def seti(self, name, v): self.gdb.write(self.sym[name], int(v).to_bytes(4, "little", signed=True))
    def setb(self, name, v): self.gdb.write(self.sym[name], bytes([v & 255]))
    def shot(self, path):
        subprocess.run(["import", "-window", "root", path], stderr=subprocess.DEVNULL)
    def stop(self):
        try:
            self.gdb.halt()
        except Exception:
            pass
        time.sleep(0.3)
        self.p.terminate()
        try: self.p.wait(timeout=5)
        except Exception: self.p.kill()
        time.sleep(0.5)

def teleport(e, tx, ty, **extra):
    e.gdb.halt()
    for k, v in (("px", tx * 8 * 16), ("py", (ty - 1) * 8 * 16), ("vy", 0), ("vx", 0), ("cam_x", max(0, tx * 8 - 120))):
        e.gdb.write(e.sym[k], int(v).to_bytes(4, "little", signed=True))
    for k, v in extra.items():
        e.gdb.write(e.sym[k], int(v).to_bytes(4, "little", signed=True))
    e.gdb.cont()

def ensure_playing(e):
    for _ in range(8):
        f = e.geti("frame_count"); time.sleep(0.3)
        # frame_count advances in every screen (text pages run frame()), so use player_dead/level state instead
        break

def cards(e, n):
    for _ in range(n):
        e.key("x", 0.12, 0.35)

def boss_fight(e, boss, arena0, n):
    teleport(e, arena0 + 4, 11)
    e.gdb.halt(); e.seti("hp", 3); e.seti("invuln", 250) ; e.gdb.cont()
    time.sleep(2.5)
    check(e.getb("arena_locked") == 1, "L%d: boss arena locks" % n)
    seen = set()
    t0 = time.time()
    while time.time() - t0 < 12:
        seen.add(e.geti("bstate"))
        e.gdb.halt(); e.seti("invuln", 250); e.seti("hp", 3); e.gdb.cont()
        time.sleep(0.25)
    check(len(seen) >= 3, "L%d: boss cycles through states %s" % (n, sorted(seen)))
    e.shot("/tmp/claude-0/shots/gba_boss%d.png" % n)
    for _ in range(16):
        e.gdb.halt()
        e.setb("bvuln", 1); e.seti("bflash", 0); e.seti("bstate", 4 if boss == 1 else 3)
        bx = e.geti("bx"); by = e.geti("by")
        e.setb("hat_state", 1) if False else e.seti("hat_state", 1)
        e.seti("hx", bx + 8); e.seti("hy", by + 8)
        e.gdb.cont()
        time.sleep(0.2)
    check(e.getb("bdead") == 1, "L%d: boss defeated" % n)
    time.sleep(3)
    check(e.getb("star_spawned") == 1, "L%d: boss drops the star" % n)

def run():
    tmp = tempfile.mkdtemp(prefix="captco_gba_")
    print("== %s" % os.path.basename(ROM))
    data = open(ROM, "rb").read()
    check(data[0xB2] == 0x96, "ROM header fixed (0x96 fixed value)")
    check(b"SRAM_V113" in data or b"FLASH1M_V103" in data or b"EEPROM_V124" in data, "ROM declares its save type (SRAM_V113 string)")
    check(len(data) <= 32 * 1024 * 1024, "ROM within GBA cart size")
    e = Emu(ROM, tmp)
    check(e.geti("save_reached") == 0, "fresh boot: no save")
    e.shot("/tmp/claude-0/shots/gba_t_title.png")
    e.key("Return", 0.15, 0.5)
    cards(e, 4)
    time.sleep(1.0)
    px0 = e.geti("px"); check(px0 == 3 * 8 * 16, "player starts at tile 3 (px=%d)" % px0)
    check(e.geti("hp") == 3, "starts with 3 HP")
    e.hold("Right", 1.5)
    time.sleep(0.3)
    check(e.geti("px") > px0 + 8 * 16, "moves right (px %d -> %d)" % (px0, e.geti("px")))
    # jump rises
    y0 = e.geti("py")
    subprocess.run(["xdotool", "keydown", "x"]); time.sleep(0.22)
    y1 = e.geti("py")
    subprocess.run(["xdotool", "keyup", "x"]); time.sleep(0.8)
    check(y1 < y0 - 8 * 16 // 2, "jump rises (py %d -> %d)" % (y0, y1))
    # hat throw
    e.key("z", 0.1, 0.05)
    hs = e.geti("hat_state")
    check(hs in (1, 2), "B throws Capt (hat_state=%d)" % hs)
    time.sleep(1.5)
    check(e.geti("hat_state") == 0, "Capt returns")
    e.shot("/tmp/claude-0/shots/gba_t_play.png")
    # level 1 star
    teleport(e, 114, 11)
    time.sleep(2.5)
    check(e.geti("save_stars") == 1 and e.geti("save_reached") == 1, "L1 star: progress saved (stars=%d reached=%d)" % (e.geti("save_stars"), e.geti("save_reached")))
    e.stop()
    sav = [f for f in os.listdir(tmp) if f.endswith(".sav")]
    check(bool(sav), "mGBA wrote battery save file")
    if sav:
        s = open(os.path.join(tmp, sav[0]), "rb").read()
        check(s[:4] == b"CPT1" and s[4] == 1, "SRAM holds save %s" % list(s[:6]))
    # reboot with the same save
    e = Emu(ROM, tmp) if False else None
    shutil.copy(ROM, os.path.join(tmp, "t.gba"))
    env = dict(os.environ, SDL_AUDIODRIVER="dummy", LIBGL_ALWAYS_SOFTWARE="1")
    e = Emu.__new__(Emu)
    e.rom = os.path.join(tmp, "t.gba")
    e.p = subprocess.Popen([MGBA, "-2", "-g", e.rom], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    e.gdb = Gdb(); e.gdb.cont(); e.sym = symbols(); time.sleep(2.5)
    check(e.geti("save_reached") == 1 and e.geti("save_stars") == 1, "save survives power cycle (reached=%d)" % e.geti("save_reached"))
    e.shot("/tmp/claude-0/shots/gba_t_continue.png")
    e.key("Return", 0.15, 0.6)         # CONTINUE
    cards(e, 1)
    time.sleep(1.0)
    check(e.geti("cur_level") == 1, "CONTINUE starts level 2 (cur_level=%d)" % e.geti("cur_level"))
    e.hold("Right", 3.0)
    time.sleep(0.3)
    # boss 1
    boss_fight(e, 1, 109, 2)
    teleport(e, 109 + 11, 12)
    time.sleep(2.5)
    check(e.geti("save_reached") == 2, "L2 complete: reached=%d" % e.geti("save_reached"))
    cards(e, 2)
    time.sleep(1.0)
    check(e.geti("cur_level") == 2, "advances to level 3 (cur_level=%d)" % e.geti("cur_level"))
    teleport(e, 122, 11)
    time.sleep(2.5)
    check(e.geti("save_reached") == 3, "L3 complete: reached=%d" % e.geti("save_reached"))
    cards(e, 2)
    time.sleep(1.0)
    check(e.geti("cur_level") == 3, "advances to level 4 (cur_level=%d)" % e.geti("cur_level"))
    boss_fight(e, 2, 117, 4)
    teleport(e, 117 + 11, 12)
    time.sleep(2.5)
    cards(e, 6)
    time.sleep(1.5)
    e.shot("/tmp/claude-0/shots/gba_t_end.png")
    check(e.geti("save_reached") == 0, "save reset after finishing the game (reached=%d)" % e.geti("save_reached"))
    e.stop()
    shutil.rmtree(tmp, ignore_errors=True)

run()
print("\n%d checks, %d failures" % (checks, fails))
sys.exit(1 if fails else 0)
