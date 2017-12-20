#!/usr/bin/python3

import sys
from pathlib import Path
import ozopython

if (len(sys.argv) != 2):
  sys.stderr.write("needs 1 argument - source file (without the .ozopy extension)\n")
  quit()

src = sys.argv[1] + ".ozopy"

if (Path(src).exists()):
  ozopython.run(src)
else:
  sys.stderr.write("file "+src+" not found\n")
