import cast
import z0_prologue
from world import W
W.set_start('shore1', 7, 9, 'up')
W.credits_text = "LOWTIDE\n\nA story about listening.\n\nThank you for playing."
# TEMP stub until zone 1 exists
from lib import *
W.mapdef('coral_square', 'shore', ["#"*16]+["#"+"."*14+"#"]*10+["#"*16], 'shore', ents=[], script=":enter\nnarr: stub reached\nend")
