# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import shutil
import os

paths = [ '/bin', '/usr/bin', '/usr/local/bin', '/opt/homebrew/bin' ]

def findFfmpeg():
  path = shutil.which('ffmpeg')
  if not path:
    for p in paths:
      p_ = os.path.join(p, 'ffmpeg')
      if os.path.exists(p_):
        os.environ['PATH'] += f':{p}'
        break
