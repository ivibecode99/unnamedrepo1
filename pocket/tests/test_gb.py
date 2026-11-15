#!/usr/bin/env python3
"""Headless emulator tests (PyBoy) for the Game Boy / Game Boy Color builds.
   python3 pocket/tests/test_gb.py [path/to/captco.gb] ...   (default: both ROMs in pocket/gb/build)"""
import io, os, sys, struct, tempfile, shutil
from pyboy import PyBoy

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "..", "gb", "build")
fails = 0
checks = 0

def check(cond, msg):
    global fails, checks
    checks += 1
    if not cond:
        fails += 1
        print("  FAIL:", msg)

def symbols(rom):
    syms = {}
    noi = rom.rsplit(".", 1)[0] + ".noi"
    for line in open(noi):
        p = line.split()
        if len(p) == 3 and p[0] == "DEF" and p[1].startswith("_"):
            syms[p[1][1:]] = int(p[2], 16)
    return syms

def make_save(reached, stars, coins):
    s = (0x5A + reached * 7 + stars * 13 + (coins & 255) + ((coins >> 8) & 255) * 3) & 255
    data = bytearray(8192)
    data[0:4] = b"CPT1"
    data[4] = reached; data[5] = stars; data[6] = coins & 255; data[7] = coins >> 8; data[8] = s
    return bytes(data)

class Game:
    def __init__(self, rom, save=None):
        self.rom = rom
        self.sym = symbols(rom)
        # PyBoy loads "<rom>.ram" next to the ROM: use a private temp copy so tests never touch build/
        self.tmp = tempfile.mkdtemp(prefix="captco_")
        self.tmp_rom = os.path.join(self.tmp, os.path.basename(rom))
        shutil.copy(rom, self.tmp_rom)
        if save is not None:
            open(self.tmp_rom + ".ram", "wb").write(save)
        self.pb = PyBoy(self.tmp_rom, window="null", sound_emulated=False)
        self.pending = {}
    def _flush(self):
        n = 0
        for addr, val in list(self.pending.items())[:16]:
            self.pb.memory[self.sym["dbg_addr"] + 2 * n] = addr & 255
            self.pb.memory[self.sym["dbg_addr"] + 2 * n + 1] = addr >> 8
            self.pb.memory[self.sym["dbg_val"] + n] = val
            n += 1
        self.pending = {}
        self.pb.memory[self.sym["dbg_n"]] = n
    def tick(self, n=1):
        for _ in range(n):
            if self.pending: self._flush()
            self.pb.tick()
    def press(self, b, hold=4, wait=6):
        self.pb.button_press(b); self.tick(hold); self.pb.button_release(b); self.tick(wait)
    def settle(self):
        """Queue the pending pokes into the ROM's test hook and wait until the game applied them."""
        self._flush()
        for _ in range(10):
            if self.pb.memory[self.sym["dbg_n"]] == 0: return
            self.tick(1)
    def u8(self, name): return self.pb.memory[self.sym[name]]
    def u16(self, name): return self.pb.memory[self.sym[name]] | (self.pb.memory[self.sym[name] + 1] << 8)
    def s16(self, name):
        v = self.u16(name)
        return v - 65536 if v >= 32768 else v
    def set16(self, name, v):
        v &= 0xFFFF
        self.pending[self.sym[name]] = v & 255
        self.pending[self.sym[name] + 1] = v >> 8
    def set8(self, name, v): self.pending[self.sym[name]] = v & 255
    def screen_nonblank(self):
        im = self.pb.screen.image.convert("L")
        return len(set(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())) > 1
    def start_playing(self, pages):
        """From the title: press START, then A through `pages` text pages."""
        self.tick(90)
        self.press("start", 4, 40)
        for _ in range(pages):
            self.press("a", 4, 25)
        self.tick(40)
    def stop(self, save=False):
        self.pb.stop(save=save)
    def saved_ram(self):
        self.pb.stop(save=True)
        return open(self.tmp_rom + ".ram", "rb").read()

def reboot(g, rom):
    """Power-cycle: stop the emulator (flushing battery SRAM to a file) and boot a fresh instance from it."""
    ram = g.saved_ram()
    g2 = Game(rom, ram)
    g2.tick(110)          # PyBoy's boot-ROM logo takes ~66 frames before the cartridge starts
    return g2

def ensure_playing(g):
    """If Pip died while running blindly the game shows OOPS/level cards: dismiss them until frames advance."""
    for _ in range(8):
        f = g.u16("frame_count")
        g.tick(8)
        if g.u16("frame_count") != f:
            return True
        g.press("a", 4, 30)
    return False

def cards(g, n=1):
    for _ in range(n):
        g.press("a", 4, 25)
    g.tick(40)

def finish_level_at(g, tx, ty):
    """Teleport Pip onto tile (tx, ty) (a star tile) and let the level-clear logic run."""
    ensure_playing(g)
    g.set16("px", tx * 8 * 16); g.set16("py", (ty - 1) * 8 * 16); g.set16("vy", 0); g.set16("vx", 0)
    g.set16("cam_x", max(0, tx * 8 - 120))
    g.settle()
    g.tick(350)

def beat_boss(g, boss, arena0, n):
    ensure_playing(g)
    g.set8("hp", 3); g.set8("invuln", 250)
    g.set16("px", (arena0 + 4) * 8 * 16); g.set16("py", 10 * 8 * 16); g.set16("vy", 0)
    g.set16("cam_x", arena0 * 8)
    g.settle()
    g.tick(200)
    check(g.u8("arena_locked") == 1, "L%d boss: arena locks when Pip enters" % n)
    check(g.u8("bactive") == 1, "L%d boss active" % n)
    seen = set()
    for i in range(900):
        g.tick(1)
        seen.add(g.u8("bstate"))
        if i % 60 == 0:
            g.set8("invuln", 250); g.set8("hp", 3)   # keep Pip alive so we can watch the boss cycle
    check(len(seen) >= 3, "L%d boss cycles through attack states %s" % (n, sorted(seen)))
    check(g.screen_nonblank(), "boss screen draws")
    for _ in range(14):
        g.set8("bvuln", 1); g.set8("bflash", 0)
        g.set8("bstate", 4 if boss == 1 else 3)
        g.set8("hat_state", 1)
        g.set16("hx", g.s16("bx") + 8); g.set16("hy", g.s16("by") + 8)
        g.settle()
        g.tick(3)
    check(g.u8("bdead") == 1, "L%d boss can be defeated (bhp=%d)" % (n, g.pb.memory[g.sym["bhp"]]))
    g.tick(400)
    check(g.u8("star_spawned") == 1, "L%d boss drops the star" % n)

def run_rom(rom):
    name = os.path.basename(rom)
    print("== %s" % name)
    size = os.path.getsize(rom)
    check(size in (32768, 65536), "ROM size is a valid power of two (%d)" % size)
    hdr = open(rom, "rb").read()
    check(hdr[0x147] == 0x1B, "cartridge type MBC5+RAM+BATTERY (0x1B), got 0x%02X" % hdr[0x147])
    check(hdr[0x149] in (1, 2, 3), "cartridge declares battery SRAM (code %d)" % hdr[0x149])
    if rom.endswith(".gbc"):
        check(hdr[0x143] in (0x80, 0xC0), "CGB flag set")
    g = Game(rom, b"\xff" * 8192)
    g.tick(150)
    check(g.screen_nonblank(), "title screen draws")
    g.press("start", 4, 40)
    for _ in range(4):
        g.press("a", 4, 25)
    g.tick(30)
    px0 = g.s16("px"); check(px0 == 3 * 8 * 16, "player starts at tile 3 (px=%d)" % px0)
    check(g.u8("hp") == 3, "starts with 3 HP")
    # movement
    g.pb.button_press("right"); g.tick(60); g.pb.button_release("right")
    check(g.s16("px") > px0 + 8 * 16, "moves right (px %d -> %d)" % (px0, g.s16("px")))
    g.tick(60)
    # jump
    y0 = g.s16("py")
    g.pb.button_press("a"); g.tick(10)
    y1 = g.s16("py")
    g.pb.button_release("a"); g.tick(90)
    check(y1 < y0 - 8, "jump rises (py %d -> %d)" % (y0, y1))
    check(g.u8("on_ground") == 1, "lands back on ground")
    # hat throw and return
    g.press("b", 3, 2)
    check(g.u8("hat_state") == 1, "B throws Capt (hat_state=%d)" % g.u8("hat_state"))
    g.tick(120)
    check(g.u8("hat_state") == 0, "Capt returns to Pip")
    # left world wall blocks
    g.pb.button_press("left"); g.tick(400); g.pb.button_release("left")
    check(g.s16("px") >= 8 * 16 - 16, "left world wall blocks (px=%d)" % g.s16("px"))
    # camera scrolls while running + jumping
    g.pb.button_press("right")
    for _ in range(12):
        g.tick(30); g.press("a", 12, 0)
    g.pb.button_release("right")
    check(g.s16("cam_x") > 0, "camera scrolls (cam_x=%d)" % g.s16("cam_x"))
    # ---------------- Level 1: grab the star
    finish_level_at(g, 114, 11)
    check(g.u8("save_stars") == 1 and g.u8("save_reached") == 1, "L1 star: progress saved (stars=%d reached=%d)" % (g.u8("save_stars"), g.u8("save_reached")))
    # power-cycle: SRAM must hold the save, CONTINUE must resume at level 2
    g = reboot(g, rom)
    check(g.u8("save_reached") == 1 and g.u8("save_stars") == 1, "save survives power cycle (reached=%d)" % g.u8("save_reached"))
    check(bytes(g.pb.memory[g.sym["dbg_raw"] + i] for i in range(4)) == b"CPT1", "SRAM magic present")
    g.press("start", 4, 40)         # CONTINUE is selected by default
    cards(g, 1)                      # level card
    check(g.u8("cur_level") == 1, "CONTINUE starts level 2 (cur_level=%d)" % g.u8("cur_level"))
    # run through the level for a while to exercise enemies/hazards
    f0 = g.u16("frame_count")
    g.pb.button_press("right")
    for _ in range(25):
        g.tick(25); g.press("a", 10, 0)
    g.pb.button_release("right")
    check(g.u16("frame_count") > f0 + 400, "L2 runs without hanging")
    # ---------------- Level 2 boss (beetle queen)
    beat_boss(g, 1, 109, 2)
    finish_level_at(g, 109 + 11, 12)
    check(g.u8("save_reached") == 2, "L2 complete: reached=%d" % g.u8("save_reached"))
    cards(g, 1)   # STAR GET card -> next level card
    cards(g, 1)
    check(g.u8("cur_level") == 2, "advances to level 3 (cur_level=%d)" % g.u8("cur_level"))
    # ---------------- Level 3
    f0 = g.u16("frame_count")
    g.pb.button_press("right")
    for _ in range(20):
        g.tick(25); g.press("a", 10, 0)
    g.pb.button_release("right")
    check(g.u16("frame_count") > f0 + 300, "L3 runs without hanging")
    finish_level_at(g, 122, 11)
    check(g.u8("save_reached") == 3, "L3 complete: reached=%d" % g.u8("save_reached"))
    g = reboot(g, rom)
    check(g.u8("save_reached") == 3, "save survives power cycle again")
    g.press("start", 4, 40); cards(g, 1)
    check(g.u8("cur_level") == 3, "CONTINUE starts level 4 (cur_level=%d)" % g.u8("cur_level"))
    # ---------------- Level 4 boss (Baron)
    beat_boss(g, 2, 117, 4)
    finish_level_at(g, 117 + 11, 12)
    g.tick(200)
    for _ in range(4):
        g.press("a", 4, 40)
    g.tick(100)
    check(g.screen_nonblank(), "ending screens show")
    # after the ending the save is reset and the title returns
    g = reboot(g, rom)
    check(g.u8("save_reached") == 0, "save reset after finishing the game (reached=%d)" % g.u8("save_reached"))
    g.stop()
    # ---------------- corrupt save is ignored
    bad = bytearray(make_save(2, 2, 5)); bad[8] ^= 0xFF
    g = Game(rom, bytes(bad)); g.tick(120)
    check(g.u8("save_reached") == 0, "corrupt save is ignored")
    good = Game(rom, make_save(2, 2, 5)); good.tick(120)
    check(good.u8("save_reached") == 2 and good.u16("save_coins") == 5, "valid synthetic save loads (reached=%d coins=%d)" % (good.u8("save_reached"), good.u16("save_coins")))
    g.stop(); good.stop()
    # ---------------- death restarts the level
    g = Game(rom, b"\xff" * 8192)
    g.tick(150); g.press("start", 4, 40)
    for _ in range(4): g.press("a", 4, 25)
    g.tick(30)
    g.set16("py", 160 * 16)          # fall into the void
    g.settle()
    g.tick(240)
    g.press("a", 4, 40)              # "OOPS" card
    g.press("a", 4, 40)              # level card
    g.tick(60)
    check(g.u8("hp") == 3 and g.u8("player_dead") == 0, "falling restarts the level with full HP")
    g.stop()

paths = sys.argv[1:] or [os.path.join(BUILD, "captco.gb"), os.path.join(BUILD, "captco.gbc")]
for p in paths:
    run_rom(p)
print("\n%d checks, %d failures" % (checks, fails))
sys.exit(1 if fails else 0)
