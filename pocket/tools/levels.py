#!/usr/bin/env python3
"""Pocket Edition level generator. Deterministic (seeded) and jump-feasible by construction.
Physics budget (see gb/src/main.c): max jump height ~3.4 tiles, max flat-jump reach ~6 tiles.
We only ever generate gaps <= 3 tiles and steps <= 2 tiles."""
import random
import art

H = 18
GY = 14           # ground surface row

THEMES = {
    "forest": {"top": "grass", "fill": "dirt", "plat": "brick", "deco": ["trunk_tree", "hill"], "hazard": "spike"},
    "desert": {"top": "sand", "fill": "sandfill", "plat": "brick", "deco": ["cactus"], "hazard": "spike"},
    "city":   {"top": "bld", "fill": "cityfill", "plat": "metal", "deco": ["cloud"], "hazard": "spike"},
    "castle": {"top": "metal", "fill": "wall", "plat": "metal", "deco": ["gear", "note"], "hazard": "lava"},
}

LEVELS = [
    {"id": 1, "name": "FERNWHISTLE FOREST", "theme": "forest", "w": 120, "seed": 11, "boss": 0, "music": 0},
    {"id": 2, "name": "SIZZLE SANDS",       "theme": "desert", "w": 132, "seed": 22, "boss": 1, "music": 1},
    {"id": 3, "name": "TINKERTOWN",         "theme": "city",   "w": 128, "seed": 33, "boss": 0, "music": 2},
    {"id": 4, "name": "GRUMBLEBELT BOX",    "theme": "castle", "w": 140, "seed": 44, "boss": 2, "music": 3},
]

ARENA_W = 22

class Level:
    def __init__(self, spec):
        self.spec = spec
        self.w = spec["w"]
        self.g = [["sky"] * H for _ in range(self.w)]       # g[x][y]
        self.enemies = []                                    # (type, x_tile, y_tile)
        self.rng = random.Random(spec["seed"])
        self.th = THEMES[spec["theme"]]
        self.start_x = 3
        self.arena = (0, 0)
        self.goal = (0, 0)
        self.coins = 0

    def col_ground(self, x, gy):
        th = self.th
        for y in range(H):
            if y == gy:
                self.g[x][y] = th["top"]
            elif y > gy:
                self.g[x][y] = th["fill"]
            else:
                self.g[x][y] = "sky"

    def pit(self, x):
        for y in range(H):
            self.g[x][y] = "sky"

    def put(self, x, y, name):
        if 0 <= x < self.w and 0 <= y < H:
            self.g[x][y] = name

    def build(self):
        rng, w, th = self.rng, self.w, self.th
        boss = self.spec["boss"]
        play_end = w - (ARENA_W + 6 if boss else 12)
        gy = GY
        gys = [GY] * w
        x = 0
        # start run
        while x < 10:
            self.col_ground(x, gy); gys[x] = gy; x += 1
        last_flat = 10
        while x < play_end:
            kind = rng.choice(["flat", "gap", "step", "plat", "spike", "enemy", "enemy", "enemy", "coins", "coins"])
            if last_flat < 4 and kind in ("gap", "step", "spike"):
                kind = "flat"
            if kind == "gap" and x + 8 < play_end:
                gl = rng.randint(2, 3)
                for i in range(gl):
                    self.pit(x + i); gys[x + i] = -1
                # coins above the gap (arc)
                for i in range(gl):
                    self.put(x + i, gy - 3 - (1 if 0 < i < gl - 1 else 0), "coin")
                x += gl
                for i in range(4):
                    self.col_ground(x, gy); gys[x] = gy; x += 1
                last_flat = 4
            elif kind == "step":
                ng = gy + rng.choice([-2, -1, 1, 2])
                ng = max(10, min(15, ng))
                for i in range(rng.randint(4, 6)):
                    self.col_ground(x, ng); gys[x] = ng; x += 1
                gy = ng
                last_flat = 4
            elif kind == "plat":
                n = rng.randint(3, 5)
                h = rng.randint(3, 4)
                for i in range(n):
                    self.col_ground(x + i, gy); gys[x + i] = gy
                    self.put(x + i, gy - h, th["plat"])
                    self.put(x + i, gy - h - 1, "coin")
                x += n
                for i in range(2):
                    self.col_ground(x, gy); gys[x] = gy; x += 1
                last_flat += n + 2
            elif kind == "spike":
                n = rng.randint(1, 2)
                for i in range(2):
                    self.col_ground(x, gy); gys[x] = gy; x += 1
                for i in range(n):
                    self.col_ground(x, gy); gys[x] = gy
                    self.put(x, gy - 1, th["hazard"]); x += 1
                for i in range(2):
                    self.col_ground(x, gy); gys[x] = gy; x += 1
                last_flat = 2
            elif kind == "enemy":
                n = rng.randint(6, 8)
                for i in range(n):
                    self.col_ground(x + i, gy); gys[x + i] = gy
                et = 1 if (rng.random() < 0.25 and self.spec["id"] > 1) else 0
                self.enemies.append((et, x + n // 2, gy - 1 if et == 0 else gy - 4))
                x += n
                last_flat += n
            elif kind == "coins":
                n = rng.randint(5, 8)
                for i in range(n):
                    self.col_ground(x + i, gy); gys[x + i] = gy
                    self.put(x + i, gy - 1, "coin")
                x += n
                last_flat += n
            else:
                n = rng.randint(4, 7)
                for i in range(n):
                    self.col_ground(x + i, gy); gys[x + i] = gy
                    if rng.random() < 0.5:
                        self.put(x + i, gy - 2, "coin")
                x += n
                last_flat += n
            if kind not in ("gap", "step", "spike"):
                pass
        # make sure there are plenty of enemies: one on every long flat stretch not already populated
        have = [e[1] for e in self.enemies]
        for ex in range(14, play_end - 6, 9):
            g0 = gys[ex]
            if g0 <= 0 or any(abs(h - ex) < 7 for h in have):
                continue
            if all(gys[ex + k] == g0 for k in range(-2, 3)) and all(self.g[ex + k][g0 - 1] == "sky" for k in range(-2, 3)):
                et = 1 if (rng.random() < 0.3 and self.spec["id"] > 1) else 0
                self.enemies.append((et, ex, g0 - 1 if et == 0 else g0 - 4))
                have.append(ex)
        # reset to default ground for the finale
        gy = GY
        # lead-in ramp back to default height (steps of 1)
        while gys[x - 1] != GY and x < w - 4:
            ng = gys[x - 1] + (1 if gys[x - 1] < GY else -1)
            for i in range(3):
                self.col_ground(x, ng); gys[x] = ng; x += 1
        if boss:
            ax0 = x + 3
            while x < ax0:
                self.col_ground(x, GY); gys[x] = GY; x += 1
            self.arena = (x, x + ARENA_W)
            while x < w:
                self.col_ground(x, GY); gys[x] = GY; x += 1
            # arena walls (solid pillars) at the edges, hidden until needed (barrier tile at runtime)
        else:
            while x < w:
                self.col_ground(x, GY); gys[x] = GY; x += 1
            # goal: raised platform + star
            gx = w - 6
            for i in range(-1, 3):
                self.put(gx + i, GY - 2, th["plat"])
            self.put(gx, GY - 3, "star")
            self.goal = (gx, GY - 3)
        # world edge walls
        for y in range(H):
            self.put(0, y, "wall" if y < GY else self.g[0][y])
            self.put(w - 1, y, "wall")
        # decoration (background, non-solid): only on sky above ground
        for _ in range(w // 6):
            dx = rng.randint(4, w - 4)
            if gys[dx] > 0 and self.g[dx][gys[dx] - 1] == "sky":
                d = rng.choice(th["deco"])
                g0 = gys[dx]
                if d == "trunk_tree":
                    self.put(dx, g0 - 1, "trunk"); self.put(dx, g0 - 2, "trunk")
                    self.put(dx, g0 - 3, "leaf"); self.put(dx - 1, g0 - 3, "leaf"); self.put(dx + 1, g0 - 3, "leaf")
                elif d == "cactus":
                    self.put(dx, g0 - 1, "cactus")
                elif d == "cloud":
                    self.put(dx, rng.randint(1, 4), "cloud")
                elif d == "hill":
                    self.put(dx, g0 - 1, "hill")
                else:
                    self.put(dx, g0 - 1, d)
        for _ in range(w // 8):   # clouds / stars in the sky for every theme
            self.put(rng.randint(3, w - 3), rng.randint(1, 5), "cloud" if self.spec["theme"] != "castle" else "note")
        # ensure player start area is clear
        for sx in range(1, 6):
            for y in range(0, GY):
                if self.g[sx][y] not in ("sky",):
                    self.g[sx][y] = "sky"
        self.coins = sum(row.count("coin") for row in self.g)
        # no deco that sits inside the arena spawn
        return self

    def ascii(self):
        key = {"sky": ".", "grass": "G", "dirt": "D", "brick": "B", "lava": "~", "coin": "o", "star": "*", "trunk": "t", "leaf": "l", "cactus": "c",
               "sand": "S", "sandfill": "s", "bld": "K", "window": "w", "cloud": "-", "spike": "^", "wall": "#", "metal": "M", "note": "n",
               "gear": "g", "hill": "h", "heart": "v", "barrier": "|", "fill": "F", "cityfill": "k"}
        rows = []
        for y in range(H):
            rows.append("".join(key[self.g[x][y]] for x in range(self.w)))
        for et, ex, ey in self.enemies:
            r = list(rows[ey]); r[ex] = "e" if et == 0 else "f"; rows[ey] = "".join(r)
        return "\n".join(rows)

    def rle(self):
        out = []
        for x in range(self.w):
            y = 0
            while y < H:
                t = art.BG_INDEX[self.g[x][y]]
                n = 1
                while y + n < H and art.BG_INDEX[self.g[x][y + n]] == t and n < 255:
                    n += 1
                out += [n, t]
                y += n
        return out

def all_levels():
    return [Level(s).build() for s in LEVELS]

if __name__ == "__main__":
    for lv in all_levels():
        print(lv.spec["name"], lv.w, "coins", lv.coins, "enemies", len(lv.enemies), "arena", lv.arena, "rle", len(lv.rle()))
