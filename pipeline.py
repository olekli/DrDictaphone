# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import functools

class Pipeline:
  def __init__(self, operations):
    self.operations = operations
    self.content = []

    prev_slot = self.onResult
    for operation in reversed(self.operations):
      operation.events.result += prev_slot
      prev_slot = functools.partial(operation.__call__, self.content)

  def onResult(self, result):
    self.content.append(result)

  def __call__(self, audio_segment):
    self.operations[0](self.content, audio_segment)
