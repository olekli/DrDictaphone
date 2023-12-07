# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from mreventloop import emits, slot, supports_event_loop
from drdictaphone.pipeline_events import PipelineEvents

@supports_event_loop('event_loop')
@emits('events', PipelineEvents)
class Output:
  def __init__(self, filename = None):
    self.filename = filename
    self.last_final_pos = 0
    with open(self.filename, 'a'):
      pass
    with open(self.filename, 'rt') as file:
      file.seek(0, os.SEEK_END)
      self.last_final_pos = file.tell()

  @slot
  def onResult(self, result):
    if self.filename:
      with open(self.filename, 'r+t') as file:
        file.seek(self.last_final_pos)
        file.truncate()
        file.write(f'\n{result}\n')
    self.events.result(result)

  @slot
  def onFence(self):
    with open(self.filename, 'rt') as file:
      file.seek(0, os.SEEK_END)
      self.last_final_pos = file.tell()
    self.events.fence()
