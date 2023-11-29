# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from pipeline_events import PipelineEvents

class Aggregator:
  def __init__(self):
    self.events = PipelineEvents()
    self.buffer = ''
    self.final = []

  def onResult(self, result):
    self.buffer = result
    self.events.result(self.makeText())

  def onFence(self):
    self.final.append(self.buffer)
    self.buffer = ''
    self.events.fence()

  def makeText(self):
    return '\n\n'.join(self.final + [self.buffer])

  def onClearBuffer(self):
    self.final = []
    self.buffer = ''
    self.events.result('')
    self.events.clear_buffer()
