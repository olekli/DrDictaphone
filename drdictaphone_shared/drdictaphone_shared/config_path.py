# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys

drdictaphonerc_path = os.path.expanduser('~/.drdictaphonerc')

def getConfigPath():
  if not os.path.exists(drdictaphonerc_path):
    return None

  with open(drdictaphonerc_path, 'r') as file:
    cp = file.read().rstrip('\n')
    return os.path.expanduser(cp)
