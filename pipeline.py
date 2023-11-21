# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
from concurrent_operation import ConcurrentOperation

class Pipeline:
  def __init__(self, operations):
    self.operations = []

    prev_slot = None
    for operation in reversed(operations):
      concurrent_operation = ConcurrentOperation(operation)
      if prev_slot != None:
        operation.events.result += prev_slot
      prev_slot = concurrent_operation.__call__
      self.operations.insert(0, concurrent_operation)

  def __enter__(self):
    for operation in self.operations:
      operation.__enter__()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    for operation in self.operations:
      operation.__exit__(exc_type, exc_value, traceback)
    return True

  def __call__(self, item):
    self.operations[0](item)
