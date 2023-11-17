# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml
from model.Context import Context

def readContext(filename):
  with open(filename, 'rt') as file:
    data = yaml.safe_load(file)
  return Context(**data)
