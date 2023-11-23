# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
from concurrent_operation import ConcurrentOperation
from model.PipelineResult import PipelineResult, PipelineResultType

class Pipeline:
  def __init__(self, operations):
    self.operations = []

    prev_slot_result = None
    prev_slot_fence = None
    for operation in reversed(operations):
      concurrent_operation = ConcurrentOperation(operation)
      if prev_slot_result != None:
        concurrent_operation.events.result += prev_slot_result
      if prev_slot_fence != None:
        concurrent_operation.events.fence += prev_slot_fence
      prev_slot_result = concurrent_operation.queueResult
      prev_slot_fence = concurrent_operation.queueFence
      self.operations.insert(0, concurrent_operation)

  def __enter__(self):
    for operation in self.operations:
      operation.__enter__()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    for operation in self.operations:
      operation.__exit__(exc_type, exc_value, traceback)

  def __call__(self, item):
    self.operations[0].queueResult(item)
