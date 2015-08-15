class Trigger(object):
  def __init__(self, time=None, bools=None, longest=None):
    self.time = time
    self.bools = bools or ()
    self.longest = longest

  def check(self, time, happened, longest):
    if self.time is not None and time >= self.time:
      return True
    for b in self.bools:
      if b in happened:
        return True
    if self.longest is not None and longest >= self.longest:
      return True
    return False


class State(object):
  def __init__(self, exit, progression):
    self.exit = exit
    self.progression = progression

  def reset(self):
    self.base_time = 0.0
    self.ofs = 0
    self.active_state = self.progression[self.ofs]
    if isinstance(self.active_state, State):
      self.active_state.reset()

  def advance(self, dt, happened, longest):
    self.base_time += dt
    while (isinstance(self.active_state, State)
           and self.ofs + 1 < len(self.progression)
           and self.active_state.exit.check(self.base_time, happened, longest)):
      self.ofs += 1
      self.active_state = self.progression[self.ofs]
      if isinstance(self.active_state, State):
        self.active_state.reset()
    if isinstance(self.active_state, State):
      self.active_state.advance(dt, happened, longest)

  def text(self):
    if isinstance(self.active_state, State):
      return self.active_state.text()
    else:
      return self.active_state


level1 = State(
  Trigger(),
  [
    State(Trigger(bools=['moved']),
          [State(Trigger(time=4.0),
                 ["I think I remember how the car's Virtual Reality interface works."]),
           "I can use the arrow keys to move around."]),
    State(Trigger(bools=['next_to_block']),
          ["Great, that works. Let's move next to a data block."]),
    State(Trigger(bools=['lifted']),
          ["... and hold space and press the arrow key towards the block to pick it up."]),
    State(Trigger(bools=['dropped']),
          ["Mighty impressive. Now hold space and an arrow key again to put it back down."]),
    State(
      Trigger(bools=['victory']),
      [State(Trigger(time=4.0),
             ["Ok, the basics work. To defrag I need to make a large consecutive area of free space."]),
       State(Trigger(time=4.0),
             ["Consecutive, left-to-right, top-down, like lines of text in a book."]),
       State(Trigger(longest=40),
             [State(Trigger(time=8.0), ["I should move the data blocks away from the center of the drive."]),
              State(Trigger(time=4.0), ["Is that car following me? Better take a detour."])]),
       State(Trigger(longest=60),
             [State(Trigger(time=6.0), ["This isn't looking too bad. Just need a bit more space."]),
              "Defragging a drive while doing 200kph through a city isn't easy. Good thing I used to be an F1 driver."]),
       State(Trigger(longest=70),
             [State(Trigger(time=2.0), ["Almost there..."]),
              State(Trigger(time=4.0), ["Woah! Truck!"]),
              "This is almost enough for Bob's data, just a bit more."]),
     ]),
    State(Trigger(),
          ["That's enough space for Bob's data. Let's grab the vibrant block to leave the VR."]),
  ]
)


class Tutorial(object):
  def __init__(self, game, level_number):
    self.happened = set()
    self.game = game
    self.base_time = 0.0
    self.longest = 0
    self.active_state = level1
    self.active_state.reset()

  def addhappened(self, event):
    self.happened.add(event)

  def setlongest(self, longest):
    self.longest = longest

  def think(self, dt):
    self.active_state.advance(dt, self.happened, self.longest)
    self.game.set_tutorial_text(self.active_state.text())

  def draw(self):
    pass
