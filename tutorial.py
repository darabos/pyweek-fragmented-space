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
      if b in tutorial.happened:
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
      self.base_time = 0.0
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
    State(Trigger(bools=['moved']),
          ["Let's move around a bit, find a good place to write this block."],
          clear_happened=['moved']),
    State(Trigger(bools=['dropped']),
          ["Mighty impressive. Now hold space and an arrow key again to write it back."]),
    State(
      Trigger(bools=['pre_victory']),
      [State(Trigger(time=4.0),
             ["Ok, the basics work. To defrag I need to make a large consecutive area of free space."]),
       State(Trigger(time=4.0),
             ["Consecutive, left-to-right, top-down, like lines of text in a book."]),
       State(Trigger(longest=40),
             [State(Trigger(time=12.0), ["I should move the data blocks away from the center of the drive."]),
              State(Trigger(time=4.0), ["Is that car following me? Better take a detour."])],
             cycle=True),
       State(Trigger(longest=60),
             [State(Trigger(time=6.0), ["This isn't looking too bad. Just need a bit more space."]),
              State(Trigger(time=12.0), ["Defragging a drive while doing 200kph through a city isn't easy. Good thing I used to be an F1 driver."])],
             cycle=True),
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
          clear_happened=['dropped'],
          cycle=True),
    State(Trigger(),
          [
            State(Trigger(time=8.0),
                  ["That's enough space for Bob's data... Wait, there's a hidden block here! Better read it!"]),
            State(Trigger(time=10.0),
                  ["I observed the blinking block of data for some time before approaching it. You can never be too careful in my line of work."]),
            State(Trigger(time=10.0),
                  ["It was still just sitting there. Silent. Blinking. A less cautious person might've read it by now, but I wasn't taking any chances."]),
            State(Trigger(time=10.0),
                  ["The more I stared at it, the more the blinking seemed to contain a pattern. Something ominous. Something sinister."]),
            State(Trigger(time=10.0),
                  ["Maybe it was the whiskey, or not having had anything but coffee since breakfast, but this block was giving me a bad feeling."]),
            State(Trigger(time=10.0),
                  ["A feeling like everything is gonna go wrong. Like something is creeping up on me. Like nothing is what it seems."]),
            State(Trigger(time=10.0),
                  ["(The whiskey was the breakfast. That probably didn't help.)"]),
            State(Trigger(time=10.0),
                  ["Still, I knew that if I wanted to get to the bottom of this, get at the cold, hard truth, I would have to read that block."]),
            State(Trigger(time=10.0),
                  ["'Cause no matter how you dress it up, all shiny and blinky and with a star on it, the truth is an ugly thing."]),
            State(Trigger(time=10.0),
                  ["And at the end of the day, someone has to scrape off the blinky exterior, look truth in the eye and tell it what's what."]),
            State(Trigger(time=10.0),
                  ["Just a shame it had to be me."]),
            State(Trigger(),
                  ["(Read the blinking block to advance.)"]),
          ]
        ),
  ]
)


level2 = State(
  Trigger(),
  [
    State(Trigger(bools=['completed']),
          [State(Trigger(time=4.0), ["This disk is a mess. If I defrag one of the files, maybe it has a program that I can use."]),
           State(Trigger(time=6.0), ["I just need to put the blocks for one of the files next to each other, in order."]),
           State(Trigger(time=6.0), ["The block with the star must be the first block of the file."]),
           State(Trigger(time=6.0), ["Star first, then make the light/dark boundary line up."]),
           State(Trigger(time=6.0), ["I can read two blocks at the same time to speed things up."]),
          ], cycle=True),
    State(Trigger(files=['Sokoban', 'Drive Space']),
          [
            State(Trigger(time=10.0),
                  ["Meh, that isn't very useful. Maybe one of the other files has something better."]),
            "Or I can ignore them and just clear up free space."
          ]),
    State(Trigger(bools=['pre_victory']),
          [State(Trigger(time=5.0),
                 ["This will come in handy! Better get back to defragging free space now."]),
           State(Trigger(time=5.0),
                 ["This was easier before my hands were covered in blood!"]),
           State(Trigger(),
                 ["Good thing I used to be a neurosurgeon."]),
         ]),
    State(Trigger(bools=['victory']),
          ["I knew it! More hidden data!"]),
    State(Trigger(),
          ["This might be the clue I need to find the scum who killed Bob!"]),
    ]
  )


level3 = State(
  Trigger(),
  [
    State(Trigger(bools=['corruption', 'pre_victory'], files=['Disk Doctor']),
          [State(Trigger(time=5.0), ["The disk had bad sectors, but it was my only remaining lead."]),
           State(Trigger(), ["Just have to step carefully around the bad sectors. I can probably read them once, but after that, who knows?"]),
          ]),
    State(Trigger(bools=['pre_victory'], files=['Disk Doctor']),
          [
            State(Trigger(time=6.0),
                  ["I was able to read the block, but the strain on the drive damaged nearby sectors. This is bad."]),
            State(Trigger(time=6.0),
                  ["Maybe one of the files here has a drive repair program."]),
          ]),
    State(Trigger(bools=['pre_victory']),
          ["Once I had found the Disk Doctor program, bad sectors weren't nearly as big a threat."]),
    State(Trigger(),
          ["Bingo! They thought they had covered their tracks, but as an expert cryptoanalyst, I knew better!"]),
    ]
  )


level4 = State(
  Trigger(),
  [
    State(Trigger(bools=['virus'], files=['Anti Virus']),
          [State(Trigger(), ["The alien drive contained a weird virus. In all my years as a virologist, I had never seen anything like it."]),
          ]),
    State(Trigger(bools=['pre_victory'], files=['Anti Virus']),
          [
            State(Trigger(bools=['virus']),
                  ["Lightning reflexes from my year of training with ninjas saved me from the worst when the virus hit me, but I had to unbuffer all the blocks."],
                  clear_happened=['virus']),
            State(Trigger(bools=['virus']),
                  ["Another close encounter with the alien menace. I have to avoid these or I won't get anywhere with this."],
                  clear_happened=['virus']),
            State(Trigger(bools=['virus']),
                  ["The virus kept hounding me, despite my best attempts at evading it. It must have a fiendishly clever AI controlling it."],
                  clear_happened=['virus']),
            State(Trigger(bools=['virus']),
                  ["If the aliens have viruses, they must have anti-viruses. It's got to be in one of these files."]),
            State(Trigger(),
                  ["You really can get used to anything. Still would be nice to find an anti-virus program."]),
          ]),
    State(Trigger(bools=['pre_victory']),
          ["The anti-virus program was clunky, but it still felt good to know part of this drive was on my side."]),
    State(Trigger(),
          ["More hidden data! Years doing xenolingustic research finally pay off!"]),
    ]
  )


dummy = State(Trigger(), [""])

levels = {
  1: level1,
  2: level2,
  3: level3,
  4: level4,
 }


class Tutorial(object):
  def __init__(self, game, level_number):
    self.happened = set()
    self.game = game
    self.base_time = 0.0
    self.longest = 0
    self.active_state = levels.get(level_number, dummy)
    self.active_state.reset(self)
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
      self.game.set_tutorial_text(self.active_state.text())
    self.first = False

  def draw(self):
    pass
