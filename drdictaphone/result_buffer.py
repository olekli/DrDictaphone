# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from mreventloop import emits, slot, has_event_loop
from drdictaphone.pipeline_events import PipelineEvents
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
@emits('events', PipelineEvents)
class ResultBuffer:
  def __init__(self):
    self.buffer = ''

  @slot
  def onResult(self, result):
    self.buffer = result

  @slot
  def onFence(self):
    if self.buffer:
      self.events.result(self.buffer)
      self.buffer = ''
    self.events.fence()
