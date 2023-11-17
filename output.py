# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

class Output:
  def __init__(self, filename = None):
    self.filename = filename

  def __call__(self, content):
    if self.filename:
      with open(self.filename, 'at') as file:
        file.write(f'\n{content}\n')
    else:
      print(f'\n{content}\n')
