# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from events import Events
import os

class Output:
  def __init__(self, filename = None):
    self.filename = filename
    self.events = Events(('final_result', 'temporary_result'))
    self.last_final_pos = 0
    with open(self.filename, 'rt') as file:
      file.seek(0, os.SEEK_END)
      self.last_final_pos = file.tell()

  def onFinalResult(self, result):
    if self.filename:
      with open(self.filename, 'r+t') as file:
        file.seek(self.last_final_pos)
        file.truncate()
        file.write(f'\n{result}\n')
        self.last_final_pos = file.tell()
    else:
      print(f'\n{result}\n')
    self.events.final_result(result)

  def onTemporaryResult(self, result):
    if self.filename:
      with open(self.filename, 'r+t') as file:
        file.seek(self.last_final_pos)
        file.truncate()
        file.write(f'\n{result}\n')
    self.events.temporary_result(result)
