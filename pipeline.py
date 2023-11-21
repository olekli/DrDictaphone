# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import functools

class Pipeline:
  def __init__(self, operations):
    self.operations = operations

    prev_slot = None
    for operation in reversed(self.operations):
      if prev_slot != None:
        operation.events.result += prev_slot
      prev_slot = operation.__call__

  def __call__(self, item):
    self.operations[0](item)
