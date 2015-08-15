# coding=utf-8
import collections
import math
import random
import pyglet
from pyglet.graphics import gl
from pyglet.window import key

import tutorial


def general_text(text, **kwargs):
  kwargs.setdefault('anchor_x', 'center')
  kwargs.setdefault('anchor_y', 'center')
  kwargs.setdefault('color', (0, 0, 0, 255))
  label = pyglet.text.Label(
    text,
    **kwargs)
  label.think = lambda dt: None
  return label

def label(text, **kwargs):
  kwargs.setdefault('font_name', 'Montserrat')
  kwargs.setdefault('font_size', 36)
  kwargs.setdefault('bold', True)
  return general_text(text, **kwargs)

def story(text, **kwargs):
  kwargs.setdefault('font_name', 'Cardo')
  kwargs.setdefault('font_size', 18)
  return general_text(text, **kwargs)

def sprite(f, **kwargs):
  image = pyglet.resource.image('images/' + f)
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
    self.idling = sprite('player-idling.png')
    self.movingleft = sprite('player-left.png')
    self.movingright = sprite('player-right.png')
    self.movingup = sprite('player-up.png')
    self.movingdown = sprite('player-down.png')
    self.lifting = sprite('player-lifting.png')
    self.hurting = sprite('player-lifting.png')
    self.flyingsprite = sprite('player-lifting.png')

    self.sprite = self.idling
    self.i = i
    self.j = j
    self.oi = i
    self.oj = j
    self.phase = 0
    self.stack = []
    self.immunity = 0
    self.flying = False
    self.move(0, 0)
    self.think(0)

  def draw(self):
    self.sprite.draw()

  steptime = 0.15
  def think(self, dt):
    if self.phase > 0:
      if self.flying:
        self.phase -= 1.5 * dt # Faster.
      else:
        self.phase -= dt
      if self.phase <= 0:
        self.phase = 0
        self.oi = self.i
        self.oj = self.j
        self.sprite = self.idling

    if self.phase == 0:
      if game.keys[key.SPACE]:
        self.lastspacetime = game.time
        if not self.flying:
          self.sprite = self.lifting
          if game.files['Disk Doctor'].complete:
            c = [o for o in game.allgrid(self.i, self.j) if isinstance(o, Corruption)]
            if c:
              c = c[0]
              c.sprite.x = toX(c.i) + random.randint(-2, 2)
              c.sprite.y = toY(c.j) + random.randint(-2, 2)
              if c != self.patient:
                self.patient = c
                self.repairsound = game.playsound('repair')
                c.health = 0
              c.health += dt
              if c.health >= 1.2:
                game.objs.remove(c)
                self.patient = None
          if game.keys[key.UP]:
            self.lift(0, -1)
            self.lastnospacetime = 0
          elif game.keys[key.DOWN]:
            self.lift(0, 1)
            self.lastnospacetime = 0
          elif game.keys[key.LEFT]:
            self.lift(-1, 0)
            self.lastnospacetime = 0
          elif game.keys[key.RIGHT]:
            self.lift(1, 0)
            self.lastnospacetime = 0

      else:
        self.patient = None
        if hasattr(self, 'repairsound'):
          self.repairsound.pause()
          del self.repairsound
        if game.files['Flight Simulator'].complete and self.lastnospacetime < self.lastspacetime and game.time - self.lastnospacetime < 0.2:
          # Short tap. Start/stop flying.
          if not self.flying:
            self.flying = game.time
            game.playsound('flight')
          else:
            b = game.grid(self.i, self.j)
            if b == 'free' or getattr(b, 'walkable', False):
              game.playsound('flight')
              self.flying = False
        self.lastnospacetime = game.time
        self.sprite = self.flyingsprite if self.flying else self.idling
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
    if not self.flying:
      p = 1 - (p - 1) * (p - 1) # Ease.
    self.sprite.x = toX(p * self.oi + (1 - p) * self.i)
    self.sprite.y = toY(p * self.oj + (1 - p) * self.j)
    if self.flying:
      self.sprite.y += int(math.sin((game.time - self.flying) * 10) * 6) + 6

  def move(self, di, dj):
    if di or dj:
      game.tutorial.addhappened('moved')
    b = game.grid(self.i + di, self.j + dj)
    if b == 'free' or getattr(b, 'walkable', False) or game.files['Extended Partition'].complete and b == 'wall' or self.flying and b != 'wall':
      self.i += di
      self.j += dj
      self.z = -self.j + 10

      # Check if we ended up next to a block:
      for ddi, ddj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        if isinstance(game.grid(self.i + ddi, self.j + ddj), Block):
          game.tutorial.addhappened('next_to_block')
    elif game.files['Sokoban'].complete and isinstance(b, Block) and game.grid(self.i + 2 * di, self.j + 2 * dj) == 'free':
      game.playsound('push')
      b.i += di
      b.j += dj
      game.checkchange()
      b.checkcomplete()
      self.i += di
      self.j += dj
      self.z = -self.j + 10
    else:
      # Bounce back.
      self.oi += di * 0.2
      self.oj += dj * 0.2
      game.playsound('bounce')
    self.phase = self.steptime

  def lift(self, di, dj):
    game.tutorial.addhappened('lifted')
    i = self.i + di
    j = self.j + dj
    b = game.grid(i, j)
    if b == 'free' and self.stack:
      b = self.stack.pop()
      game.tutorial.addhappened('dropped')
      b.dropped(i, j)
      if game.vibrant and not self.stack:
        game.tutorial.addhappened('victory')
      if game.files['Fast Tracker'].complete and b.file:
        game.playsound(b.file.name + '/' + str(b.index))
      else:
        game.playsound('drop')
    elif isinstance(b, Block):
      if b.vibrant:
        if self.stack:
          self.say('My hands are full!')
          game.playsound('fail')
        else:
          b.taken(self.stack[-1] if self.stack else self)
          self.stack.append(b)
          game.playsound('win')
          game.objs.remove(game.tutorial)
          game.objs.remove(game.tutorial_text)
          game.add(ScoreScreen())
      elif len(self.stack) < 2 or game.files['Drive Space'].complete:
        b.taken(self.stack[-1] if self.stack else self)
        self.stack.append(b)
        if game.files['Fast Tracker'].complete and b.file:
          game.playsound(b.file.name + '/' + str(b.index))
        else:
          game.playsound('pickup')
      else:
        self.say('My hands are full!')
        game.playsound('fail')
    elif not self.stack:
      return
    elif isinstance(b, Corruption):
      self.say('Bad sector.')
      game.playsound('fail')
    elif isinstance(b, Virus) and game.files['Anti Virus'].complete:
      self.say('Squish.')
      game.playsound('squish')
      game.objs.remove(b)
      b = self.stack.pop()
      b.dropped(i, j)
    self.phase = self.steptime

  def hurt(self):
    if game.time < self.immunity:
      return # Still immune.
    game.playsound('hurt')
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


class ScoreScreen(object):
  def __init__(self):
    self.t0 = game.time
    if game.time < game.ttl:
      labels = [
        'LEVEL {} COMPLETE'.format(game.level),
        '',
        'Time remaining:',
        'Longest free area:',
        'Files assembled:',
      ]
      points = [0, 0, int(game.ttl - game.time), game.longest_length, 0]
      completed = [f for f in game.files.values() if f.complete]
      if not completed:
        labels.append('    none')
        points.append(0)
      else:
        for f in completed:
          labels.append('    {}:'.format(f.name))
          points.append(f.count * 10)
      labels += [
        'TOTAL:',
        '',
        'Press SPACE to proceed',
      ]
      total = sum(points)
      game.points += total
      points += [total, 0, 0]
    elif game.level == 1:
      labels = [
        'LEVEL {} COMPLETE'.format(game.level),
        '',
        'Press SPACE to proceed',
        ]
      points = [0] * len(labels)
    else:
      labels = [
        'LEVEL {} COMPLETE'.format(game.level),
        '',
        'Out of time. No points awarded.',
        '',
        'Press SPACE to proceed or R to try again.',
        ]
      points = [0] * len(labels)
    self.labels = []
    y = 250
    for l, p in zip(labels, points):
      y -= 30
      if l:
        l = label(l, anchor_x = 'left', anchor_y = 'baseline', font_size = 20)
        l.x = -250
        l.y = y
        self.labels.append(l)
      if p:
        l = label(str(p), anchor_x = 'right', anchor_y = 'baseline', font_size = 25)
        l.x = 250
        l.y = y
        self.labels.append(l)
    self.primed = False

  def draw(self):
    t = 5.0 * (game.time - self.t0)
    for i, l in enumerate(self.labels):
      i *= 2
      if i + 1 < t:
        l.draw()
      elif i < t and (t - i) % 0.5 < 0.2:
        l.draw()

  def think(self, dt):
    if not game.keys[key.SPACE]:
      self.primed = True
    if self.primed and game.keys[key.SPACE]:
      game.objs = []
      game.add(Cutscene(game.level + 1))


class Corruption(object):
  walkable = True

  def __init__(self, i, j):
    rnd = random.randrange(5)
    self.sprite = sprite('corruption-{}.png'.format(rnd), batch = game.layers['corruption'])
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
    if self.primed and not isinstance(game.grid(self.i, self.j), Block):
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
      game.playsound('corruption')
      game.checkchange()
      self.primed = False


class Block(object):
  def __init__(self, i, j, file, index, t0):
    self.inside = sprite('block-inside.png', batch = game.layers['blocks-inside'])
    self.sprite = self.inside
    self.outside = sprite('block-{}.png'.format(index), batch = game.layers['blocks-outside'])
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
    self.flying = True
    self.carrier = carrier
    self.inside.batch = None
    self.outside.batch = None
    self.scale(0.8)
    if self.file:
      self.file.complete = False
    game.checkchange()

  def dropped(self, i, j):
    self.flying = False
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
      game.tutorial.addhappened('completed')
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
    self.sprite = sprite('virus.png')
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
    self.note = None

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
      if self.note in game.objs:
        game.objs.remove(self.note)
      self.note = game.add(Note(zero.i, zero.j, self.name, self.text))
      game.playsound('complete')
    else:
      self.note.delete()
      game.playsound('uncomplete')


class Note(object):
  def __init__(self, i, j, text1, text2):
    self.bi = i
    self.bj = j
    self.position, self.x, self.y = self.pickposition()
    self.x = int(self.x)
    self.y = int(self.y)
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
        o = (opt - i) % files
      if o in taken:
        continue
      phi = 2 * math.pi * o / files
      return o, math.cos(phi) * abs(toX(14)), math.sin(phi) * abs(toY(13))

  def delete(self):
    self.ttl = game.time + 0.5

  def think(self, dt):
    if self.ttl and game.time >= self.ttl and self in game.objs:
      game.objs.remove(self)


class Cutscene(object):
  def __init__(self, level):
    self.level = level
    if level > last_level + 1: # Plus epilogue.
      self.image = None
      self.sound = None
    else:
      self.image = sprite('story/{}.jpg'.format(level))
      w = float(self.image.width)
      h = float(self.image.height)
      ratio = max(game.window.width / w, game.window.height / h)
      w = int(w * ratio)
      h = int(h * ratio)
      self.image.scale = ratio
      try:
        self.sound = pyglet.resource.media('sounds/story{}.ogg'.format(level)).play()
      except:
        self.sound = None
    self.primed = False

  def draw(self):
    if self.image:
      self.image.draw()

  def think(self, dt):
    if not game.keys[key.SPACE]:
      self.primed = True
    if self.sound and not self.sound.playing or self.primed and game.keys[key.SPACE] or self.image is None:
      game.objs.remove(self)
      game.level = self.level
      levels[min(last_level, self.level)].make()


class Level(object):
  def __init__(self, level_number, files, max_length, corruption, viruses, time_limit):
    self.level_number = level_number
    self.files = files
    self.max_length = max_length
    self.corruption = corruption
    self.viruses = viruses
    self.time_limit = time_limit

  def make(self):
    game.makelevel(self.level_number, self.files, self.max_length, self.corruption, self.viruses, self.time_limit)
    game.tutorial_text = game.add(story('', x=-380, y=240, font_size=14, anchor_x='left', anchor_y='top', multiline=True, width=180))


levels = {
  1: Level(1, 1, 2, 0, 0, 0),
  2: Level(2, 3, 10, 1, 0, 100),
  3: Level(3, 4, 10, 2, 1, 100),
  4: Level(4, 5, 10, 4, 1, 100),
  5: Level(5, 6, 10, 6, 2, 200),
  6: Level(6, 7, 10, 10, 4, 300),
}
first_level = min(levels.keys())
last_level = max(levels.keys())


class Timer(object):
  digits = 5
  def __init__(self):
    self.digits = [label('', x = 350 - 12 * i, y = 280, font_size = 16) for i in range(Timer.digits)]
    self.sublabel = story('Zero points if completed. R to restart.', x = 350, y = 240, font_size = 14, anchor_x = 'right')
    self.beeps = min(game.ttl - game.time, 10)

  def draw(self):
    if game.level == 1:
      return # Hide timer on first level.
    for l in self.digits:
      l.draw()
    if game.time >= game.ttl:
      self.sublabel.draw()

  def think(self, dt):
    if game.time < game.ttl:
      text = ' ' * Timer.digits + '{:.1f}'.format(game.ttl - game.time)
      for c, l in zip(reversed(text), self.digits):
        l.text = c
      if game.ttl - game.time < self.beeps:
        game.playsound('beep')
        self.beeps -= 1
    else:
      self.digits[0].anchor_x = 'right'
      self.digits[0].text = 'OUT OF TIME'
      for l in self.digits[1:]:
        l.text = ''
    if game.keys[key.R]:
      levels[game.level].make()


class Game(object):
  def __init__(self):
    self.objs = []
    self.points = 0
    soundnames = 'pickup drop hurt flight corruption reveal win complete uncomplete bounce fail repair beep squish push'.split()
    for f in self.allfiles():
      for i in range(10):
        soundnames.append(f.name + '/' + str(i))
    self.sounds = {}
    for n in soundnames:
      try:
        self.sounds[n] = pyglet.resource.media('sounds/{}.ogg'.format(n), streaming = False)
      except:
        # We primarily expect a pyglet.media.riff.WAVEFormatException
        # here if avbin isn't installed (and thus we can't load .ogg
        # files), but really, whatever goes wrong, just ignore it and
        # keep going without that sound.
        self.sounds[n] = None
    pyglet.resource.add_font('fonts/Montserrat-Bold.ttf')
    pyglet.resource.add_font('fonts/Cardo-Regular.ttf')

  def playsound(self, sound):
    if self.sounds[sound]:
      return self.sounds[sound].play()
    else:
      class FakeSound(object):
        def pause(self):
          pass
      return FakeSound()

  def add(self, o):
    self.objs.append(o)
    return o

  def allgrid(self, i, j):
    matches = []
    for o in self.objs:
      if hasattr(o, 'j') and not getattr(o, 'flying', False) and o.i == i and o.j == j:
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

  def set_tutorial_text(self, text):
    self.tutorial_text.text = text

  def run(self):
    self.time = 0
    window = pyglet.window.Window(caption = 'Fragmented Space', width = 800, height = 600)
    self.window = window
    self.layers = collections.defaultdict(pyglet.graphics.Batch)
    self.keys = key.KeyStateHandler()
    self.fullscreen = False
    window.set_icon(pyglet.resource.image('images/player-lifting.png'))
    self.add(Cutscene(first_level))
#    self.add(label('Fragmented Space', x = 0, y = 250))
#    self.add(story('A game of my life on a platter', x = 0, y = 190))
    gl.glClearColor(255, 255, 255, 255)
    gl.glEnable(gl.GL_LINE_SMOOTH);
    gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST);
    @window.event
    def on_draw():
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

  def allfiles(self):
    return [
      File('Fast Tracker', 'Blocks make music.'),
      File('Sokoban', 'Walk into blocks to push them.'),
      File('Drive Space', 'Carry any number of blocks.'),
      File('Anti Virus', 'Drop a block on a virus to kill it.'),
      File('Disk Doctor', 'Hold SPACE to repair bad sectors.'),
      File('Extended Partition', 'Move outside the partition.'),
      File('Flight Simulator', 'Tap SPACE to lift off or land.'),
    ]

  def makelevel(self, level_number, file_count, max_length, corruption, virus, time_limit):
    self.level_number = level_number
    self.ttl = self.time + time_limit
    self.tutorial = tutorial.Tutorial(self, level_number)
    self.objs = [self.tutorial]
    self.add(Timer())
    self.player = self.add(Player(0, 0))
    def hx(x):
      return x / 0x100 / 0x100 % 0x100, x / 0x100 % 0x100, x % 0x100
    files = self.allfiles()
    self.files = dict((f.name, f) for f in files)
    colors = [
      hx(0x5599ff), # blue
      hx(0xff2a2a), # red
      hx(0xaaff55), # green
      hx(0xffff00), # yellow
      hx(0xafdde9), # teal
      hx(0xeeaaff), # purple
      hx(0xffaa22), # orange
      hx(0xff2ad4), # magenta
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
    blocks = [o for o in self.objs if isinstance(o, Block) and not getattr(o, 'flying', False) and not o.vibrant]
    taken = set(o.i + 10 * o.j for o in blocks)
    start = 0
    longest = 0
    last = -1
    taken.add(100) # Sentinel block at the end.
    for p in range(101):
      if p in taken:
        span = p - last - 1
        if span > longest:
          longest = span
          start = last + 1
        last = p
    needed = (100 - len(blocks)) * 3 / 4
    self.tutorial.setlongest(longest)
    if longest >= needed and not self.vibrant:
      p = start + longest / 2
      b = self.add(Block(p % 10, p / 10, None, 0, game.time))
      b.vibrant = True
      self.tutorial.addhappened('pre_victory')
      self.vibrant = b
      self.playsound('reveal')
    elif longest < needed and self.vibrant:
      self.objs.remove(self.vibrant)
      self.vibrant = False

    corruption = [o for o in self.objs if isinstance(o, Corruption)]
    corruption = set(o.i + 10 * o.j for o in corruption)
    self.longest_length = longest
    self.longest = []
    for p in range(start, start + longest):
      if p in corruption:
        continue
      s = sprite('longest-{}.png'.format(self.hundred[p]))
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
