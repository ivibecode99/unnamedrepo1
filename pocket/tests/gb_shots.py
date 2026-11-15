import sys
from pyboy import PyBoy
rom, out = sys.argv[1], sys.argv[2]
pb = PyBoy(rom, window="null", sound_emulated=False)
def tick(n=1):
    for _ in range(n): pb.tick()
def press(b, hold=4, wait=6):
    pb.button_press(b); tick(hold); pb.button_release(b); tick(wait)
tick(120)
pb.screen.image.save(out + "_title.png")
press("start", 4, 30)
for i in range(4):      # story pages
    press("a", 4, 20)
pb.screen.image.save(out + "_levelcard.png")
press("a", 4, 60)
pb.screen.image.save(out + "_play0.png")
# run right and jump around
pb.button_press("right")
for i in range(6):
    tick(40); press("a", 12, 0)
pb.button_release("right")
pb.screen.image.save(out + "_play1.png")
print("ok")
pb.stop()
