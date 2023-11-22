# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
from concurrent_operation import ConcurrentOperation
from model.PipelineResult import PipelineResult, PipelineResultType

class Pipeline:
  def __init__(self, operations):
    self.operations = []

    prev_slot_final = None
    prev_slot_temporary = None
    prev_slot_fence = None
    for operation in reversed(operations):
      concurrent_operation = ConcurrentOperation(operation)
      if prev_slot_final != None:
        operation.events.final_result += prev_slot_final
      if prev_slot_temporary != None:
        operation.events.temporary_result += prev_slot_temporary
      if prev_slot_fence != None:
        operation.events.fence += prev_slot_fence
      prev_slot_final = concurrent_operation.queueFinalResult
      prev_slot_temporary = concurrent_operation.queueTemporaryResult
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
    self.operations[0].queueFinalResult(item)
