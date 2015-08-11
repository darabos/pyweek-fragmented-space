# coding=utf-8
import pyglet
from pyglet.window import key

def label(text, **kwargs):
  pyglet.resource.add_font('fonts/Montserrat-Bold.ttf')
  kwargs.setdefault('font_name', 'Montserrat')
  kwargs.setdefault('font_size', 36)
  kwargs.setdefault('anchor_x', 'center')
  kwargs.setdefault('anchor_y', 'center')
  label = pyglet.text.Label(
    text,
    color=(0, 0, 0, 255),
    **kwargs)
  label.think = lambda dt: None
  return label

def story(text, **kwargs):
  pyglet.resource.add_font('fonts/Cardo-Regular.ttf')
  kwargs.setdefault('font_name', 'Cardo')
  kwargs.setdefault('font_size', 18)
  return label(text, **kwargs)

def sprite(f):
  image = pyglet.resource.image(f)
  sprite = pyglet.sprite.Sprite(image)
  sprite.think = lambda dt: None
  image.anchor_x = image.width / 2
  image.anchor_y = image.height / 2
  return sprite

def toX(i):
  return (i - 4.5) * 30
def toY(j):
  return (j - 4.5) * 30

class Player(object):
  idling = sprite('images/player-idling.png')
  movingleft = sprite('images/player-left.png')
  movingright = sprite('images/player-right.png')
  movingup = sprite('images/player-up.png')
  movingdown = sprite('images/player-down.png')
  lifting = sprite('images/player-lifting.png')

  def __init__(self):
    self.sprite = self.idling
    self.i = 0
    self.j = 0
    self.oi = 0
    self.oj = 0
    self.phase = 0
    self.stack = []
    self.move(0, 0)

  def draw(self):
    self.sprite.draw()

  steptime = 0.15
  def think(self, dt):
    if self.phase > 0:
      self.phase -= dt
      if self.phase <= 0:
        self.phase = 0
        self.oi = self.i
        self.oj = self.j
        self.sprite = self.idling
    if self.phase == 0:
      if game.keys[key.SPACE]:
        self.sprite = self.lifting
        if game.keys[key.UP]:
          self.lift(0, 1)
        elif game.keys[key.DOWN]:
          self.lift(0, -1)
        elif game.keys[key.LEFT]:
          self.lift(-1, 0)
        elif game.keys[key.RIGHT]:
          self.lift(1, 0)
      else:
        self.sprite = self.idling
        if game.keys[key.UP]:
          self.sprite = self.movingup
          self.move(0, 1)
        elif game.keys[key.DOWN]:
          self.sprite = self.movingdown
          self.move(0, -1)
        elif game.keys[key.LEFT]:
          self.sprite = self.movingleft
          self.move(-1, 0)
        elif game.keys[key.RIGHT]:
          self.sprite = self.movingright
          self.move(1, 0)

    p = self.phase / self.steptime
    p = 1 - (p - 1) * (p - 1) # Ease.
    self.sprite.x = toX(p * self.oi + (1 - p) * self.i)
    self.sprite.y = toY(p * self.oj + (1 - p) * self.j)

  def move(self, di, dj):
    b = game.grid(self.i + di, self.j + dj)
    if b == 'free' or getattr(b, 'walkable', False):
      self.i += di
      self.j += dj
      self.z = -self.j + 10
    else:
      # Bounce back.
      self.oi += di * 0.2
      self.oj += dj * 0.2
    self.phase = self.steptime

  def lift(self, di, dj):
    i = self.i + di
    j = self.j + dj
    b = game.grid(i, j)
    if b == 'free' and self.stack:
      b = self.stack.pop()
      b.dropped(i, j)
    elif isinstance(b, Block):
      b.taken(self.stack[-1] if self.stack else self)
      self.stack.append(b)
    self.phase = self.steptime


class Corruption(object):
  walkable = True

  def __init__(self, i, j):
    self.sprite = sprite('images/block.png')
    self.sprite.color = (0, 0, 0)
    self.sprite.scale = 1.2
    self.i = i
    self.j = j
    self.sprite.x = toX(i)
    self.sprite.y = toY(j)
    self.z = -j - 0.1
    self.primed = False

  def draw(self):
    self.sprite.draw()

  def think(self, dt):
    if not self.primed and game.grid(self.i, self.j) != self:
      self.primed = True
    if self.primed and game.grid(self.i, self.j) == self:
      neighbors = [
        (self.i + 1, self.j),
        (self.i - 1, self.j),
        (self.i, self.j + 1),
        (self.i, self.j - 1),
        ]
      cs = [(c.i, c.j) for c in game.objs if isinstance(c, Corruption)]
      for (i, j) in set(neighbors) - set(cs):
        if 0 <= i < 10 and 0 <= j < 10:
          game.add(Corruption(i, j))
      self.primed = False


class Block(object):
  def __init__(self, i, j):
    self.sprite = sprite('images/block.png')
    self.i = i
    self.j = j
    self.sprite.x = toX(i)
    self.sprite.y = toY(j)
    self.z = -j
    self.carrier = None
    self.vx = 0
    self.vy = 0

  def draw(self):
    self.sprite.draw()

  def taken(self, carrier):
    del self.j # Remove from grid.
    self.carrier = carrier

  def dropped(self, i, j):
    self.i = i
    self.j = j
    self.carrier = None
    self.z = -self.j

  def think(self, dt):
    if self.carrier:
      dx = int(self.carrier.sprite.x - self.sprite.x)
      dy = int(self.carrier.sprite.y - self.sprite.y + 10)
      self.sprite.scale = 0.8
      self.z = self.carrier.z + 0.1
    else:
      dx = int(toX(self.i) - self.sprite.x)
      dy = int(toY(self.j) - self.sprite.y)
      self.sprite.scale = 1
    # TODO: make dt-dependent
    self.vx *= 0.6
    self.vy *= 0.6
    self.vx += 0.3 * dx
    self.vy += 0.3 * dy
    self.sprite.x += self.vx
    self.sprite.y += self.vy


class Game(object):
  def __init__(self):
    self.objs = []

  def add(self, o):
    self.objs.append(o)
    return o

  def grid(self, i, j):
    if 0 <= i < 10 and 0 <= j < 10:
      for o in self.objs:
        if hasattr(o, 'j') and isinstance(o, Block) and o.i == i and o.j == j:
          return o # Return block if present.
      for o in self.objs:
        if hasattr(o, 'j') and o.i == i and o.j == j:
          return o # Look at non-blocks as second preference.
      return 'free'
    else:
      return 'wall'

  def run(self):
    window = pyglet.window.Window(caption = 'Fragmented Space', width = 800, height = 600)
    self.keys = key.KeyStateHandler()
    self.fullscreen = False
    self.player = self.add(Player())
    window.set_icon(self.player.sprite.image)
    self.add(Block(4, 4))
    self.add(Corruption(4, 4))
    self.add(Block(5, 5))
    self.add(Block(6, 6))
    self.add(Block(7, 7))
    self.add(label('Fragmented Space', x = 0, y = 250))
    self.add(story('A game of my life on a platter', x = 0, y = 190))
    pyglet.gl.glClearColor(255, 255, 255, 255)
    @window.event
    def on_draw():
      window.clear()
      pyglet.gl.glLoadIdentity()
      pyglet.gl.glTranslatef(window.width / 2, window.height / 2, 0)
      self.objs.sort(key=lambda o: o.z if hasattr(o, 'z') else 100)
      for o in self.objs:
        o.draw()
    @window.event
    def on_key_release(symbol, modifiers):
      if symbol == key.F:
        self.fullscreen = not self.fullscreen
        window.set_fullscreen(self.fullscreen)
    def update(dt):
      for o in self.objs[:]:
        o.think(dt)
    pyglet.clock.schedule_interval(update, 1.0 / 70)
    window.push_handlers(self.keys)
    pyglet.app.run()

if __name__ == '__main__':
  game = Game()
  game.run()
