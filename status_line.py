# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from events import Events
import logger

logger = logger.get(__name__)

class StatusLine:
  mapping = {
    'Vad': 'VAD',
    'Transcriber': 'TRANS',
    'PostProcessor': 'POST',
    'Output': 'OUT'
  }

  def makeClosure(self, item, status):
    return lambda: self.onUpdate(item, status)

  def __init__(self):
    self.events = Events(('status_update'))
    self.items = [ 'VAD', 'TRANS', 'POST', 'OUT' ]
    self.status = {
      'VAD': False,
      'TRANS': False,
      'POST': False,
      'OUT': False
    }
    for item in self.items:
      setattr(self, f'on{item}active', self.makeClosure(item, True))
      setattr(self, f'on{item}idle', self.makeClosure(item, False))
    logger.debug(f'__init__: {dir(self)}')

  def onUpdate(self, op, status):
    logger.debug(f'onUpdate: {op} {status}')
    self.status[op] = status
    self.events.status_update(self.getStatusLine())

  def getStatusLine(self):
    to_print = [ item if self.status[item] else '' for item in self.items ]
    status_line = ''.join(f'{word:<6}' for word in to_print)
    return status_line
