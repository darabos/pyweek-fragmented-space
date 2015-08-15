class Trigger(object):
  def __init__(self, time=None, bools=None):
    self.time = time
    self.bools = bools or ()


level1 = [
  ("I think I remember how the car's Virtual Reality interface works.",
   ),
  ("I can use the arrow keys to move around.",
   Trigger(time=4.0)),
  ("Great, that works. Now let's move next to a data block.",
   Trigger(bools=['moved'])),
  ("... and hold space and press the arrow key towards the block to pick it up.",
   Trigger(bools=['next_to_block'])),
  ("Mighty impressive. Now space and an arrow key again to put it back down.",
   Trigger(bools=['lifted'])),
  ("Ok, the basics work. What do we need to do here...",
   Trigger(bools=['dropped'])),
  ("I wonder what's in this file. If I defrag the file I can find out.",
   Trigger(time=8.0, bools=['completed'])),
  ("All I need to do is put all the blocks for the file next to each other, and in the right order.",
   Trigger(time=8.0, bools=['completed'])),
  ]


class Tutorial(object):
  def __init__(self, game, level_number):
    self.game = game
    self.level_number = level_number
    self.base_time = 0.0
    self.data = level1
    self.ofs = 0
    self.happened = set()

  def addhappened(self, event):
    self.happened.add(event)

  def checktrigger(self, trigger):
    if trigger.time is not None:
      if self.base_time > trigger.time:
        return True
    for b in trigger.bools:
      if b in self.happened:
        return True
    return False

  def think(self, dt):
    self.base_time += dt
    while (self.ofs + 1 < len(self.data)
        and self.checktrigger(self.data[self.ofs + 1][1])):
      self.base_time = 0.0
      self.ofs += 1

    self.game.set_tutorial_text(self.data[self.ofs][0])

  def draw(self):
    pass
