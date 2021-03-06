Fragmented Space
================

A team entry in PyWeek #20  <http://www.pyweek.org/20/>

  - Code and story:
      Alexander Malmberg and Daniel Darabos
  - Music and narration:
      Alexander Malmberg
  - Sounds, graphics, guitar, and photos:
      Daniel Darabos
  - Fonts:
      Montserrat by Julieta Ulanovsky (not a member of the team)
      Licensed under the SIL Open Font License

      Cardo by David Perry (not a member of the team)
      Licensed under the SIL Open Font License



DEPENDENCIES
------------

This game uses Python and Pyglet.

  - Python:     http://www.python.org/
  - Pyglet:     http://www.pyglet.org/



RUNNING THE GAME
----------------

Find the Mac and Windows executables at http://pyweek.org/e/fragmentedspace/

Or get the source from https://github.com/darabos/pyweek-fragmented-space/ and run:

  - python run_game.py



HOW TO PLAY THE GAME
--------------------

Move with the arrow keys. Use SPACE to interact. Press R to restart the level.
Press F to toggle full-screen mode. The level you've reached and the score
you've collected are automatically saved in a file called "save".

Your goal is to defragment a hard drive. The longest run of free space is
marked. You can pass the level if this is at least 75% of the total free
space. But this alone will award you a meager score. Most of your score comes
from defragmenting files. When the blocks of a file are contiguous and in the
correct order, the file is defragmented. At this point you gain an ability.
Each color represents a different, useful ability. The points are tallied at
the end of the level. If you ran out of time, you gain no points.

SPACE is used to pick up and drop blocks. Hold space and press the arrow key
in the direction of the block to pick it up. Do the same in the direction of
an empty spot to drop a block you are carrying. SPACE is also used with
abilities. The ability description will tell you how.

There are two hazards lurking on the surface of the hard drive. Viruses run
around randomly and bump into you, causing you to drop everything in your
hands. You cannot write to (put down blocks on) bad sectors. Reading (picking
up) from bad sectors works, but it causes the neighboring sectors to go bad as
well.

If there are no more cutscenes between levels, you have beaten the game and
are now in infinite play mode. Press ESC to quit the game.

If you decide to restart the game at this point, you will find a new item in
the main menu: "New game +". This mode will put up much more of a challenge!
(It's also accessible by setting "max_level" to 100 in the save file.)



LICENSE
-------

This game is released under the GPL (version 3).
