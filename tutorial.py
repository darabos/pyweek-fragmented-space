from run_game import story

class Trigger(object):
  def __init__(self, time=None, bools=None, longest=None, files=None):
    self.time = time
    self.bools = bools or ()
    self.longest = longest
    self.files = files or ()

  def check(self, time, happened, longest, completed_files):
    if self.time is not None and time >= self.time:
      return True
    for b in self.bools:
      if b in happened:
        return True
    for f in self.files:
      if f in completed_files:
        return True
    if self.longest is not None and longest >= self.longest:
      return True
    return False


class State(object):
  def __init__(self, exit, progression, cycle=False, clear_happened=None):
    self.exit = exit
    self.progression = progression
    self.cycle = cycle
    if clear_happened:
      self.clear_happened = set(clear_happened)
    else:
      self.clear_happened = set()

  def reset(self, tutorial):
    self.base_time = 0.0
    self.ofs = 0
    self.active_state = self.progression[self.ofs]
    for b in self.clear_happened:
      tutorial.happened.remove(b)
    if isinstance(self.active_state, State):
      self.active_state.reset(tutorial)

  def advance(self, tutorial, dt, happened, longest, completed_files):
    advanced = False
    self.base_time += dt
    while (isinstance(self.active_state, State)
           and self.ofs + 1 < len(self.progression)
           and self.active_state.exit.check(
             self.base_time, happened, longest, completed_files)):
      advanced = True
      self.ofs += 1
      self.active_state = self.progression[self.ofs]
      if isinstance(self.active_state, State):
        self.active_state.reset(tutorial)
    if isinstance(self.active_state, State):
      advanced = advanced or self.active_state.advance(
        tutorial, dt, happened, longest, completed_files)
    return advanced

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
          ["... and hold space and press the arrow key towards the block to read it."]),
    State(Trigger(bools=['dropped']),
          ["Mighty impressive. Now hold space and an arrow key again to write it back."]),
    State(
      Trigger(bools=['pre_victory']),
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
              "This is almost enough for Bob's data, just a bit more."]),
     ]),
    State(Trigger(bools=['victory']),
          [State(Trigger(bools=['dropped']),
                 ["Got it! Just need to write this block somewhere..."]),
           State(Trigger(bools=['pre_victory']),
                 ["Gah! And I was so close!"],
                 clear_happened=['pre_victory'])],
          clear_happened=['dropped']),
    State(Trigger(),
          ["What's this? There's some hidden data here! Better read it!"]),
  ]
)


level2 = State(
  Trigger(),
  [
    State(Trigger(bools=['completed']),
          [State(Trigger(time=4.0), ["This disk is a mess. If I defrag one of the files, maybe it has a program that I can use."]),
           State(Trigger(time=8.0), ["I just need to put the blocks for one of the files next to each other, in order."]),
           State(Trigger(time=8.0), ["The block with the star must be the first block of the file."]),
           State(Trigger(time=8.0), ["Star, then make the light/dark boundary line up."]),
           State(Trigger(time=8.0), ["I can read two blocks at the same time to speed things up."]),
          ], cycle=True),
    State(Trigger(files=['Sokoban', 'Drive Space']),
          [
            State(Trigger(time=15.0),
                  ["Meh, that isn't very useful. Maybe one of the other files has something better."]),
            "Or I can ignore them and just clear up free space."
          ]),
    State(Trigger(bools=['victory']),
          ["This will come in handy! Better get back to defragging free space now."]),
    State(Trigger(),
          ["I knew it! More hidden data! Let's read it!"]),
    ]
  )


dummy = State(Trigger(), [""])

levels = {
  1: level1,
  2: level2,
  }


class Tutorial(object):
  def __init__(self, game, level_number):
    self.happened = set()
    self.game = game
    self.base_time = 0.0
    self.longest = 0
    self.active_state = levels.get(level_number, dummy)
    self.active_state.reset(self)
    self.label = game.add(story('', x=-380, y=240, font_size=14, anchor_x='left', anchor_y='top', multiline=True, width=180))
    self.first = True


  def addhappened(self, event):
    self.happened.add(event)

  def setlongest(self, longest):
    self.longest = longest

  def think(self, dt):
    completed_files = set()
    for name, f in self.game.files.iteritems():
      if f.complete:
        completed_files.add(name)
    if self.active_state.advance(
        self, dt, self.happened, self.longest, completed_files) or self.first:
      self.label.text = self.active_state.text()
    self.first = False

  def draw(self):
    self.label.draw()
