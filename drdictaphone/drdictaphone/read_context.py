# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import yaml
from drdictaphone.model.context import Context

read_from_file = [ 'tools', 'gpt_model', 'options', 'instructions' ]

def readContext(filename):
  with open(filename, 'rt') as file:
    data = yaml.safe_load(file)
  for item in read_from_file:
    if item in data and data[item] and isinstance(data[item], str):
      sub_filename = data[item]
      with open(sub_filename, 'rt') as file:
        data[item] = yaml.safe_load(file)
  return Context(**data)
