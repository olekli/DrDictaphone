# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml
from model.Context import Context

def readContext(filename):
  with open(filename, 'rt') as file:
    data = yaml.safe_load(file)
  if 'tools' in data and data['tools']:
    tools_filename = data['tools']
    with open(data['tools'], 'rt') as file:
      data['tools'] = yaml.safe_load(file)
  else:
    data['tools'] = None
  return Context(**data)
