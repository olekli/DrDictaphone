# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from mreventloop import emits, slot, has_event_loop, forwards
from drdictaphone.pipeline_events import PipelineEvents, PipelineSlots

@has_event_loop('event_loop')
@forwards(PipelineSlots)
@emits('events', PipelineEvents)
class Aggregator:
  def __init__(self):
    self.buffer = ''
    self.final = []

  @slot
  def onResult(self, result):
    self.buffer = result
    self.events.result(self.makeText())

  @slot
  def onFence(self):
    self.final.append(self.buffer)
    self.buffer = ''
    self.events.fence()

  def makeText(self):
    return '\n\n'.join(self.final + [self.buffer])

  @slot
  def onClearBuffer(self):
    self.final = []
    self.buffer = ''
    self.events.result('')
    self.events.clear_buffer()
