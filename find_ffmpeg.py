# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import shutil
import os

paths = [ '/bin', '/usr/bin', '/usr/local/bin' ]

def findFfmpeg():
  path = shutil.which('ffmpeg')
  if not path:
    for p in paths:
      p_ = os.path.join(p, 'ffmpeg')
      if os.path.exists(p_):
        os.environ['PATH'] += f':{p}'
        break
