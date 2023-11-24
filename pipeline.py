# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
from concurrent_operation import ConcurrentOperation
from model.PipelineResult import PipelineResult, PipelineResultType

class Pipeline:
  def __init__(self, operations, display):
    self.operations = []
    self.display = display

    prev_slot_result = None
    prev_slot_fence = None
    for operation in reversed(operations):
      concurrent_operation = ConcurrentOperation(operation, self.display)
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
      if self.display:
        self.display.total_cost += operation.total_cost

  def __call__(self, item):
    self.operations[0].queueResult(item)

  def __getitem__(self, operation_name):
    for operation in self.operations:
      if operation.operation.__class__.__name__ == operation_name:
        return operation.operation
    return None
