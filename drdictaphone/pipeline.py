# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
from mreventloop import EventLoop, connect, setEventLoop, emits, forwards, supports_event_loop
from drdictaphone.pipeline_events import PipelineEvents

@supports_event_loop('event_loop')
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

  def __enter__(self):
    for event_loop in self.event_loops:
      event_loop.__enter__()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    for event_loop in self.event_loops:
      event_loop.__exit__(exc_type, exc_value, traceback)
