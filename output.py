# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from events import Events
import os

class Output:
  def __init__(self, filename = None):
    self.filename = filename
    self.events = Events(('final_result', 'temporary_result', 'fence'))
    self.last_final_pos = 0
    with open(self.filename, 'rt') as file:
      file.seek(0, os.SEEK_END)
      self.last_final_pos = file.tell()

  def onResult(self, result):
    if self.filename:
      with open(self.filename, 'r+t') as file:
        file.seek(self.last_final_pos)
        file.truncate()
        file.write(f'\n{result}\n')
    self.events.temporary_result(result)

  def onFence(self):
    with open(self.filename, 'rt') as file:
      file.seek(0, os.SEEK_END)
      self.last_final_pos = file.tell()
    self.events.fence()
