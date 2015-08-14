# coding=utf-8
import collections
import math
import random
import pyglet
from pyglet.graphics import gl
from pyglet.window import key

def label(text, **kwargs):
  pyglet.resource.add_font('fonts/Montserrat-Bold.ttf')
  kwargs.setdefault('font_name', 'Montserrat')
  kwargs.setdefault('font_size', 36)
  kwargs.setdefault('anchor_x', 'center')
  kwargs.setdefault('anchor_y', 'center')
  kwargs.setdefault('color', (0, 0, 0, 255))
  label = pyglet.text.Label(
    text,
    **kwargs)
  label.think = lambda dt: None
  return label

def story(text, **kwargs):
  pyglet.resource.add_font('fonts/Cardo-Regular.ttf')
  kwargs.setdefault('font_name', 'Cardo')
  kwargs.setdefault('font_size', 18)
  return label(text, **kwargs)

def sprite(f, **kwargs):
  image = pyglet.resource.image(f)
  sprite = pyglet.sprite.Sprite(image, **kwargs)
  sprite.think = lambda dt: None
  image.anchor_x = image.width / 2
  image.anchor_y = image.height / 2
  return sprite

def toX(i):
  return (i - 4.5) * 30

def toY(j):
  return (4.5 - j) * 30

class Player(object):
  walkable = True

  def __init__(self, i, j):
    self.idling = sprite('images/player-idling.png')
    self.movingleft = sprite('images/player-left.png')
    self.movingright = sprite('images/player-right.png')
    self.movingup = sprite('images/player-up.png')
    self.movingdown = sprite('images/player-down.png')
    self.lifting = sprite('images/player-lifting.png')
    self.hurting = sprite('images/player-lifting.png')

    self.sprite = self.idling
    self.i = i
    self.j = j
    self.oi = i
    self.oj = j
    self.phase = 0
    self.stack = []
    self.move(0, 0)
    self.think(0)
    self.immunity = 0

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
          self.lift(0, -1)
        elif game.keys[key.DOWN]:
          self.lift(0, 1)
        elif game.keys[key.LEFT]:
          self.lift(-1, 0)
        elif game.keys[key.RIGHT]:
          self.lift(1, 0)
      else:
        self.sprite = self.idling
        if game.keys[key.UP]:
          self.sprite = self.movingup
          self.move(0, -1)
        elif game.keys[key.DOWN]:
          self.sprite = self.movingdown
          self.move(0, 1)
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
      if b.vibrant:
        if self.stack:
          self.say('My hands are full!')
        else:
          b.taken(self.stack[-1] if self.stack else self)
          self.stack.append(b)
          print 'Level done!'
      elif len(self.stack) < 2 or game.files['Drive Space'].complete:
        b.taken(self.stack[-1] if self.stack else self)
        self.stack.append(b)
      else:
        self.say('My hands are full!')
    elif not self.stack:
      return
    elif isinstance(b, Corruption):
      self.say('Bad sector.')
    elif isinstance(b, Virus) and game.files['Anti Virus'].complete:
      self.say('Squish.')
      game.objs.remove(b)
      b = self.stack.pop()
      b.dropped(i, j)
    self.phase = self.steptime

  def hurt(self):
    if game.time < self.immunity:
      return # Still immune.
    self.say(random.choice(['Ah', 'Ouch', 'Oops', 'Eep']))
    self.sprite = self.hurting
    places = []
    for i in range(10):
      for j in range(10):
        b = game.grid(i, j)
        if b == 'free' or isinstance(b, Corruption):
          d = math.sqrt((i - self.i) * (i - self.i) + (j - self.j) * (j - self.j))
          places.append((d, i, j))
    places.sort()
    for (b, (d, i, j)) in zip(self.stack, places):
      b.dropped(i, j)
    self.stack = []
    self.oi = self.i
    self.oj = self.j
    self.sprite.x = toX(self.i)
    self.sprite.y = toY(self.j)
    self.phase = self.steptime * 2
    self.immunity = self.steptime * 4 + game.time

  def say(self, msg):
    game.add(Tip(msg, x = self.sprite.x, y = self.sprite.y + 20))


class Tip(object):
  def __init__(self, msg, ttl = 2, **kwargs):
    kwargs.setdefault('font_size', 10)
    self.label = label(msg, **kwargs)
    self.y0 = self.label.y
    self.t0 = game.time
    self.ttl = ttl

  def draw(self):
    self.label.draw()

  def think(self, dt):
    self.label.y = int(self.y0 + 300 * (game.time - self.t0) ** 4)
    if self.t0 + self.ttl < game.time:
      game.objs.remove(self)


class Corruption(object):
  walkable = True

  def __init__(self, i, j):
    rnd = random.randrange(5)
    self.sprite = sprite('images/corruption-{}.png'.format(rnd), batch = game.layers['corruption'])
    self.i = i
    self.j = j
    self.sprite.x = toX(i)
    self.sprite.y = toY(j)
    self.z = -j - 0.1
    self.primed = False
    self.t0 = game.time

  def draw(self):
    pass

  def think(self, dt):
    if game.time < self.t0 + 0.3:
      self.sprite.opacity = 0 if game.time % 0.1 < 0.05 else 255
    elif self.sprite.opacity != 255:
      self.sprite.opacity = 255
    if not self.primed and isinstance(game.grid(self.i, self.j), Block):
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
      game.checkchange()
      self.primed = False


class Block(object):
  def __init__(self, i, j, file, index, t0):
    self.inside = sprite('images/block-inside.png', batch = game.layers['blocks-inside'])
    self.sprite = self.inside
    self.outside = sprite('images/block-{}.png'.format(index), batch = game.layers['blocks-outside'])
    if file:
      self.inside.color = file.color
    self.file = file
    self.index = index
    self.i = i
    self.j = j
    self.t0 = t0 # Time to start appearing.
    self.inside.x = toX(i)
    self.inside.y = toY(j)
    self.outside.x = toX(i)
    self.outside.y = toY(j)
    self.z = -j
    self.carrier = None
    self.vx = 0
    self.vy = 0
    if game.time <= self.t0:
      self.scale(0)
    self.think(0)
    self.vibrant = False

  def scale(self, s):
    self.inside.scale = s
    self.outside.scale = s

  def draw(self):
    if self.vibrant:
      self.inside.color = random.randrange(128, 256), random.randrange(128, 256), random.randrange(128, 256)
    if self.carrier:
      self.inside.draw()
      self.outside.draw()

  def taken(self, carrier):
    del self.j # Remove from grid.
    self.carrier = carrier
    self.inside.batch = None
    self.outside.batch = None
    self.scale(0.8)
    if self.file:
      self.file.complete = False
    game.checkchange()

  def dropped(self, i, j):
    self.i = i
    self.j = j
    self.carrier = None
    self.z = -self.j
    self.inside.batch = game.layers['blocks-inside']
    self.outside.batch = game.layers['blocks-outside']
    self.scale(1)
    game.checkchange()
    self.checkcomplete()

  def checkcomplete(self):
    if not self.file:
      return
    p = 10 * self.j + self.i - self.index
    i, j = p % 10, p / 10
    for a in range(self.file.count):
      b = game.grid(i, j)
      if isinstance(b, Block) and b.file is self.file and b.index == a:
        i += 1
        if i == 10:
          i = 0
          j += 1
      else:
        self.file.complete = False
        break
    else:
      self.file.complete = True

  def think(self, dt):
    if self.carrier:
      dx = int(self.carrier.sprite.x - self.sprite.x)
      dy = int(self.carrier.sprite.y - self.sprite.y + 10)
      self.z = self.carrier.z + 0.1
    else:
      dx = int(toX(self.i) - self.sprite.x)
      dy = int(toY(self.j) - self.sprite.y)
    # TODO: make dt-dependent
    self.vx *= 0.6
    self.vy *= 0.6
    self.vx += 0.3 * dx
    self.vy += 0.3 * dy
    self.inside.x += self.vx
    self.inside.y += self.vy
    self.outside.x += self.vx
    self.outside.y += self.vy
    poptime = 0.3
    if self.t0 < game.time < self.t0 + poptime:
      self.scale((game.time - self.t0) / poptime)
    elif self.t0 < game.time < self.t0 + poptime + dt:
      self.scale(1)



class Virus(object):
  walkable = True

  def __init__(self, i, j):
    self.sprite = sprite('images/virus.png')
    self.i = i
    self.j = j
    self.oi = i
    self.oj = j
    self.phase = 0
    self.move(0, 0)

  def draw(self):
    self.sprite.draw()

  steptime = 0.25
  def think(self, dt):
    if self.phase > 0:
      self.phase -= dt
      if self.phase <= 0:
        self.phase = 0
        self.oi = self.i
        self.oj = self.j
        for b in game.allgrid(self.i, self.j):
          if isinstance(b, Player):
            b.hurt()
    if self.phase == 0:
      dirs = [d for d in [(0, 1), (0, -1), (-1, 0), (1, 0)] if self.canmove(*d)]
      if dirs:
        d = random.choice(dirs)
        self.move(*d)
      self.phase = self.steptime

    p = self.phase / self.steptime
    self.sprite.x = toX(p * self.oi + (1 - p) * self.i)
    self.sprite.y = toY(p * self.oj + (1 - p) * self.j)
    p = p * 2 - 1
    self.sprite.y += 10 * (1 - p * p)

  def canmove(self, di, dj):
    b = game.grid(self.i + di, self.j + dj)
    return b == 'free' or getattr(b, 'walkable', False)

  def move(self, di, dj):
    self.i += di
    self.j += dj
    self.z = -self.j + 10


class File(object):
  def __init__(self, name, text):
    self.name = name
    self.text = text
    self.color = None # Set later.
    self.count = 0 # Set later.
    self._complete = False

  @property
  def complete(self):
    return self._complete

  @complete.setter
  def complete(self, value):
    if value == self._complete:
      return
    self._complete = value
    if value:
      zero = [o for o in game.objs if isinstance(o, Block) and o.index == 0 and o.file is self][0]
      self.note = game.add(Note(zero.i, zero.j, self.name, self.text))
    else:
      self.note.delete()


class Note(object):
  def __init__(self, i, j, text1, text2):
    self.bi = i
    self.bj = j
    self.position, self.x, self.y = self.pickposition()
    self.opacity = 191
    self.text1 = label(text1, x = self.x, y = self.y + 16, font_size = 16, color = (0, 0, 0, self.opacity))
    self.text2 = story(text2, x = self.x, y = self.y - 12, font_size = 10, color = (0, 0, 0, self.opacity))
    self.t0 = game.time
    self.ttl = 0

  def draw(self):
    bx, by = toX(self.bi), toY(self.bj)
    lx, ly = self.x, self.y
    flat = math.copysign(self.text1.content_width / 2, lx - bx)
    coords = int(bx), int(by), int(lx - flat), int(ly), int(lx + flat), int(ly)
    gl.glEnable(gl.GL_BLEND);
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA);
    gl.glLineWidth(1)
    vs = len(coords) / 2
    t = game.time - self.t0
    if self.ttl and self.ttl - game.time < 1:
      t = self.ttl - game.time
    op = int(min(1, t) * self.opacity)
    pyglet.graphics.draw(vs, gl.GL_LINE_STRIP, ('v2i', coords), ('c4B', (0, 0, 0, 0) + (0, 0, 0, op) * (vs - 1)))
    if t > 0.5 or t > 0.25 and t % 0.05 < 0.02:
      self.text1.draw()
      self.text2.draw()

  def pickposition(self):
    notes = [n for n in game.objs if isinstance(n, Note)]
    taken = set(n.position for n in notes)
    phi = math.atan2(toY(self.bj), toX(self.bi)) % (math.pi * 2)
    files = len(game.files)
    opt = int(files * phi / math.pi / 2)
    for i in range(files):
      o = opt + i
      if o in taken:
        o = opt - i
      if o in taken:
        continue
      phi = 2 * math.pi * o / files
      return o, math.cos(phi) * abs(toX(14)), math.sin(phi) * abs(toY(13))

  def delete(self):
    self.ttl = game.time + 0.5

  def think(self, dt):
    if self.ttl and game.time >= self.ttl:
      game.objs.remove(self)


class Game(object):
  def __init__(self):
    self.objs = []

  def add(self, o):
    self.objs.append(o)
    return o

  def allgrid(self, i, j):
    matches = []
    for o in self.objs:
      if hasattr(o, 'j') and o.i == i and o.j == j:
        matches.append(o)
    return matches

  def grid(self, i, j):
    if 0 <= i < 10 and 0 <= j < 10:
      matches = self.allgrid(i, j)
      if not matches:
        return 'free'
      order = [Block]
      matches.sort(key = lambda o: order.index(o.__class__) if o.__class__ in order else -1)
      return matches[-1]
    else:
      return 'wall'

  def run(self):
    self.time = 0
    window = pyglet.window.Window(caption = 'Fragmented Space', width = 800, height = 600)
    self.layers = collections.defaultdict(pyglet.graphics.Batch)
    self.keys = key.KeyStateHandler()
    self.fullscreen = False
    window.set_icon(pyglet.resource.image('images/player-lifting.png'))
    self.makelevel(4, 6, 4, 1)
#    self.add(label('Fragmented Space', x = 0, y = 250))
#    self.add(story('A game of my life on a platter', x = 0, y = 190))
    self.timeremaining = self.add(story('100', x = -350, y = 280, font_size = 12, anchor_x = 'left'))
    self.t0 = self.time
    gl.glClearColor(255, 255, 255, 255)
    gl.glEnable(gl.GL_LINE_SMOOTH);
    gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST);
    @window.event
    def on_draw():
      self.timeremaining.text = '{:.1f}'.format(100 + self.t0 - self.time)
      window.clear()
      gl.glLoadIdentity()
      gl.glTranslatef(window.width / 2, window.height / 2, 0)
      for l in ['corruption', 'longest', 'blocks-inside', 'blocks-outside']:
        self.layers[l].draw()
      self.objs.sort(key=lambda o: o.z if hasattr(o, 'z') else 100)
      for o in self.objs:
        o.draw()
    @window.event
    def on_key_release(symbol, modifiers):
      if symbol == key.F:
        self.fullscreen = not self.fullscreen
        window.set_fullscreen(self.fullscreen)
    def update(dt):
      self.time += dt
      for o in self.objs[:]:
        o.think(dt)
    pyglet.clock.schedule_interval(update, 1.0 / 70)
    window.push_handlers(self.keys)
    pyglet.app.run()

  def makelevel(self, file_count, max_length, corruption, virus):
    self.objs = []
    self.player = self.add(Player(0, 0))
    def hx(x):
      return x / 0x100 / 0x100 % 0x100, x / 0x100 % 0x100, x % 0x100
    files = [
      File('Drive Space', 'Carry any number of blocks.'), # Done.
      File('Anti Virus', 'Drop a block on a virus to kill it.'), # Done.
      File('Disk Doctor', 'Stand on bad sectors to fix them.'),
      File('Fast Tracker', 'Blocks make music.'),
      File('Partition Extender', 'Move outside the partition.'),
      File('Sokoban', 'Walk into blocks to push them.'),
      File('Flight Simulator', 'Tap SPACE to lift off or land.'),
    ]
    self.files = dict((f.name, f) for f in files)
    colors = [
      hx(0x5599ff), # blue
      hx(0xff2a2a), # red
      hx(0xaaff55), # green
      hx(0xffff00), # yellow
      hx(0xafdde9), # teal
      hx(0xff2ad4), # purple
      hx(0xffaa22), # orange
      hx(0xeeaaff), # magenta
      hx(0xfff6d5), # light grey
      hx(0x99aa77), # dark grey
      ]
    lengths = [random.randint(2, max_length) for f in files]
    for f, c, l in zip(files, colors, lengths):
      f.color = c
      f.count = l
    files = files[:file_count]
    for f in files:
      for a in range(f.count):
        i, j = random.randrange(10), random.randrange(10)
        while self.grid(i, j) != 'free':
          i, j = random.randrange(10), random.randrange(10)
        self.add(Block(i, j, f, a, game.time + j * 0.03))
    for a in range(virus):
      i, j = random.randrange(10), random.randrange(10)
      while self.grid(i, j) != 'free':
        i, j = random.randrange(10), random.randrange(10)
      self.add(Virus(i, j))
    for a in range(corruption):
      i, j = random.randrange(10), random.randrange(10)
      while any(isinstance(obj, Corruption) for obj in self.allgrid(i, j)):
        i, j = random.randrange(10), random.randrange(10)
      self.add(Corruption(i, j))
    self.vibrant = False
    self.checkchange()

  hundred = [random.randrange(7) for i in range(100)]
  def checkchange(self):
    blocks = [o for o in self.objs if isinstance(o, Block) and hasattr(o, 'j') and not o.vibrant]
    taken = set(o.i + 10 * o.j for o in blocks)
    start = 0
    longest = 0
    last = -1
    for p in range(100):
      if p in taken:
        span = p - last - 1
        if span > longest:
          longest = span
          start = last + 1
        last = p
    needed = (100 - len(blocks)) / 2
    if longest >= needed and not self.vibrant:
      p = start + longest / 2
      b = self.add(Block(p % 10, p / 10, None, 0, game.time))
      b.vibrant = True
      self.vibrant = b
    elif longest < needed and self.vibrant:
      self.objs.remove(self.vibrant)
      self.vibrant = False

    corruption = [o for o in self.objs if isinstance(o, Corruption)]
    corruption = set(o.i + 10 * o.j for o in corruption)
    self.longest = []
    for p in range(start, start + longest):
      if p in corruption:
        continue
      s = sprite('images/longest-{}.png'.format(self.hundred[p]))
      s.x = toX(p % 10)
      s.y = toY(p / 10)
      s.batch = self.layers['longest']
      if self.vibrant:
        s.color = 0, 255, 0
      else:
        s.color = 0, 0, 0
      s.opacity = 40
      self.longest.append(s)

if __name__ == '__main__':
  game = Game()
  game.run()
