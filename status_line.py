# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

class StatusLine:
  mapping = {
    'Vad': 'VAD',
    'Transcriber': 'TRANS',
    'PostProcessor': 'POST',
    'Output': 'OUT'
  }

  def __init__(self):
    self.items = [ 'VAD', 'TRANS', 'POST', 'OUT' ]
    self.status = {
      'VAD': False,
      'TRANS': False,
      'POST': False,
      'OUT': False
    }

  def update(self, operation_name, new_status):
    if operation_name in StatusLine.mapping:
      self.status[StatusLine.mapping[operation_name]] = new_status
      self.printStatusLine()

  def printStatusLine(self):
    to_print = [ item if self.status[item] else '' for item in self.items ]
    status_line = ''.join(f'{word:<6}' for word in to_print)
    print(status_line, end='\r')
