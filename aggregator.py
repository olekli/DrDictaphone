# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from pipeline_events import PipelineEvents

class Aggregator:
  def __init__(self):
    self.events = PipelineEvents()
    self.content = [None]

  def onResult(self, result):
    self.content[-1] = result
    self.events.result(self.makeText())

  def onFence(self):
    self.content.append(None)
    self.events.fence()

  def makeText(self):
    return ' '.join([line for line in self.content if line is not None])
