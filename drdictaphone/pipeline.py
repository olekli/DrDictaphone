# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
from mreventloop import EventLoop, connect, setEventLoop, emits, forwards, has_event_loop
from drdictaphone.pipeline_events import PipelineEvents

@has_event_loop('event_loop')
@forwards([ 'onStartRec', 'onStopRec', 'onPauseMic', 'onUnpauseMic', 'onClearBuffer' ])
@emits('events', PipelineEvents)
class Pipeline:
  def __init__(self, operations):
    self.operations = []
    self.event_loops = []

    prev_op = self
    for operation in [op for op in operations if op]:
      self.event_loops.append(EventLoop())
      self.operations.append(operation)
      setEventLoop(self.operations[-1], self.event_loops[-1])
      connect(prev_op, None, self.operations[-1], None)
      prev_op = self.operations[-1]

  async def __aenter__(self):
    for event_loop in self.event_loops:
      await event_loop.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    for event_loop in self.event_loops:
      await event_loop.__aexit__(exc_type, exc_value, traceback)
