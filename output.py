# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

class Output:
  def __init__(self, filename = None):
    self.filename = filename

  def makeText(self, content):
    return '\n\n'.join(content)

  def __call__(self, content):
    if self.filename:
      with open(self.filename, 'wt') as file:
        file.write(self.makeText(content))
    else:
      print(self.makeText(content))
