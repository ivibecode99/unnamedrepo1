"""Walkthrough routes for each ending. Coordinates are tile coords (16px) in the map the player is currently in."""
L = lambda i: ('L', i); R_ = ('R',); A_ = ('A',)
def ph(n, *a): return ('say', n)
def build(ending):
    s = []
    kill_skiff = ending == 'neutral'
    fight = ending == 'fight'
    true = ending == 'true'
    # ---- prologue
    s += [ph('prologue'), ('exit', 6, 11), ('fight', 7, 5, [L(1), L(2), R_])]
    s += [('exit', 7, 1), ('exit', 15, 6)]
    # ---- zone 1 reef
    s += [ph('reef1'), ('talk', 5, 10)]
    if true: s += [('talk', 14, 1)]
    s += [('walk', 11, 6), ('exit', 15, 6)]
    s += [ph('reef2'), ('push', 5, 4, 3, 5), ('push', 5, 7, 3, 5), ('exit', 7, 0)]
    s += [ph('reef3'), ('talk', 8, 3, [0]), ('talk', 12, 3, [0]), ('talk', 4, 3, [0]), ('exit', 7, 0)]
    s += [ph('ruffle'), ('fight', 7, 7, [A_] if fight else [L(1), L(2), L(3)]), ('exit', 7, 0)]
    # ---- zone 2 hull
    s += [ph('hull'), ('talk', 13, 6, [1]), ('exit', 15, 6)]
    s += [('talk', 14, 2), ('exit', 15, 6)]
    s += [('talk', 5, 9, [1]), ('exit', 15, 6)]
    s += [ph('brig'), ('fight', 7, 6, [A_] if (kill_skiff or fight) else [L(1), L(2), L(3)]), ('exit', 7, 11)]
    s += [ph('brass'), ('fight', 7, 7, [A_] if fight else [L(1), L(2), L(3)]), ('exit', 7, 0)]
    # ---- zone 3 salt
    s += [ph('salt'), ('talk', 8, 8)]
    if true: s += [('talk', 11, 5, [0])]
    s += [('exit', 15, 6)]
    s += [('push', 4, 3, 0, 2), ('push', 3, 5, 3, 0)] if False else []
    s += [ph('ruins1'), ('push', 4, 3, 0, 2), ('push', 4, 5, 3, 7), ('push', 11, 5, 1, 1), ('push', 6, 7, 3, 6), ('push', 12, 7, 0, 1), ('exit', 15, 6)]
    s += [ph('ruins2'), ('talk', 10, 8, [0]), ('talk', 4, 8, [0]), ('talk', 7, 8, [0]), ('exit', 15, 6)]
    s += [ph('choir'), ('fight', 3, 6, [A_] if fight else [L(1), L(2), L(3)]), ('exit', 15, 6)]
    # ---- zone 4 depths
    s += [('exit', 15, 6), ph('glimmer'), ('exit', 15, 6), ('exit', 15, 6)]
    s += [ph('depths2'), ('push', 5, 4, 3, 5), ('push', 5, 8, 3, 5)]
    if true: s += [('talk', 2, 1)]
    s += [('exit', 15, 6)]
    s += [ph('depths3'), ('fight', 9, 6, [A_] if fight else [L(1), L(2), L(3)]), ('exit', 15, 6)]
    s += [ph('lumen'), ('fight', 3, 6, [A_] if fight else [L(1), L(2), L(3)]), ('exit', 15, 6)]
    # ---- zone 5 archive
    s += [ph('archive'), ('exit', 15, 6)]
    if true: s += [('talk', 14, 2)]
    s += [('exit', 15, 6)]
    if true: s += [('talk', 2, 9), ('talk', 13, 9), ('exit', 0, 6), ('exit', 0, 6), ('talk', 4, 3), ('exit', 15, 6), ('exit', 15, 6)]
    s += [('talk', 7, 3, [0]), ('talk', 11, 3, [0]), ('talk', 3, 3, [0]), ('exit', 15, 6)]
    s += [ph('quill'), ('fight', 3, 6, [A_] if fight else [L(1), L(2), L(3)]), ('exit', 15, 6)]
    # ---- finale
    s += [ph('light'), ('exit', 7, 0)]
    s += [('push', 8, 5, 1, 1), ('push', 8, 4, 3, 4), ('push', 8, 8, 1, 1), ('push', 8, 7, 2, 4), ('exit', 7, 0)]
    s += [('walk', 7, 7), ('walk', 7, 5), ('walk', 7, 3), ('exit', 7, 0)]
    marrow = [A_] if fight else ([L(1), L(4)] if true else [L(1), L(2), L(3)])
    s += [ph('marrow'), ('fight', 7, 7, marrow)]
    return s
