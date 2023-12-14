# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
from mreventloop import connect, emits, forwards, has_event_loop_thread
from drdictaphone.pipeline_events import PipelineEvents

@has_event_loop_thread('event_loop')
@forwards([ 'onStartRec', 'onStopRec', 'onPauseMic', 'onUnpauseMic', 'onClearBuffer' ])
@emits('events', PipelineEvents)
class Pipeline:
  def __init__(self, operations):
    self.operations = []

    prev_op = self
    for operation in [op for op in operations if op]:
      self.operations.append(operation)
      connect(prev_op, None, self.operations[-1], None)
      prev_op = self.operations[-1]

  def __enter__(self):
    self.event_loop.__enter__()
    for event_loop in [ operation.event_loop for operation in self.operations ]:
      event_loop.__enter__()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    for event_loop in [ operation.event_loop for operation in self.operations ]:
      event_loop.__exit__(exc_type, exc_value, traceback)
    return self.event_loop.__exit__(exc_type, exc_value, traceback)
