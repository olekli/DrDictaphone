# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import functools
from mreventloop import connect, emits, forwards, has_event_loop
from drdictaphone.pipeline_events import PipelineEvents, PipelineSlots

@has_event_loop('event_loop')
@forwards(PipelineSlots)
@emits('events', PipelineEvents)
class Pipeline:
  def __init__(self, operations):
    self.operations = []

    prev_op = self
    for operation in [op for op in operations if op]:
      self.operations.append(operation)
      connect(prev_op, self.operations[-1])
      prev_op = self.operations[-1]

  async def __aenter__(self):
    await self.event_loop.__aenter__()
    for event_loop in [ operation.event_loop for operation in self.operations ]:
      await event_loop.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    for event_loop in [ operation.event_loop for operation in self.operations ]:
      await event_loop.__aexit__(exc_type, exc_value, traceback)
    return await self.event_loop.__aexit__(exc_type, exc_value, traceback)
