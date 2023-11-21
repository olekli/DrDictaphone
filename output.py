# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from events import Events

class Output:
  def __init__(self, filename = None):
    self.filename = filename
    self.events = Events(('result'))

  def __call__(self, result):
    if self.filename:
      with open(self.filename, 'at') as file:
        file.write(f'\n{result}\n')
    else:
      print(f'\n{result}\n')
    self.events.result(result)
