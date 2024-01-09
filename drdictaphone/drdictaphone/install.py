# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import os
import sys
from drdictaphone_shared.config_path import getConfigPath, drdictaphonerc_path
from drdictaphone.config import initConfig

def install(target_path):
  user_path = getConfigPath()
  target_path = os.path.expanduser(target_path)

  with open(drdictaphonerc_path, 'w') as file:
    file.write(target_path)

  os.makedirs(target_path, exist_ok = True)

  script_content = f'#!/bin/sh\nsource {sys.prefix}/bin/activate && DRDICTAPHONE_PROD=True python -m drdictaphone.cli "$@" && deactivate'
  script_path = os.path.join(target_path, 'drdictaphone')

  with open(script_path, 'w') as file:
    file.write(script_content)

  os.chmod(script_path, os.stat(script_path).st_mode | 0o111)

  initConfig('frozen')
