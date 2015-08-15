class Tutorial(object):
  def __init__(self, game, level_number):
    self.game = game
    self.level_number = level_number
    self.base_time = 0.0

  def think(self, dt):
    self.base_time += dt
    if self.base_time > 0:
      self.game.set_tutorial_text(
        'Some help here would be nice.\n\nYeah, definitely.')
