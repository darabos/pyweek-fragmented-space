Fragmented Space
================

[![Join the chat at https://gitter.im/darabos/pyweek-fragmented-space](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/darabos/pyweek-fragmented-space?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

A team entry in PyWeek #20  <http://www.pyweek.org/20/>

  - Code:
      Alexander Malmberg and Daniel Darabos
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
The level you've reached and the score you've collected are automatically
saved in a file called "save". Delete this to restart.

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

If there are no more cutscenes between levels, you have beaten the game and
are now in infinite play mode. Press ESC to quit the game.



LICENSE
-------

This game is released under the GPL (version 3).
