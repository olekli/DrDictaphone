# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
from event_loop import EventLoop, connect, associateWithEventLoop, forwardEvents
from pipeline_events import PipelineEvents

class Pipeline:
  def __init__(self, operations):
    self.events = PipelineEvents()
    self.operations = []
    self.event_loops = []

    forwardEvents(self, list(PipelineEvents.__events__))

    prev_op = self
    for operation in [op for op in operations if op]:
      self.event_loops.append(EventLoop())
      self.operations.append(operation)
      associateWithEventLoop(self.operations[-1], self.event_loops[-1])
      connect(prev_op, None, self.operations[-1], None)
      prev_op = self.operations[-1]

  def __enter__(self):
    for event_loop in self.event_loops:
      event_loop.__enter__()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    for event_loop in self.event_loops:
      event_loop.__exit__(exc_type, exc_value, traceback)
