# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from events import Events
import logger

logger = logger.get(__name__)

class StatusLine:
  mapping = {
    'Mic': 'MIC',
    'Vad': 'VAD',
    'Transcriber': 'TRANS',
    'PostProcessor': 'POST',
    'Output': 'OUT'
  }

  def makeClosure(self, item, status):
    return lambda: self.onUpdateActivity(item, status)

  def __init__(self):
    self.events = Events(('status_update_left', 'status_update_center', 'status_update_right'))
    self.items = [ 'MIC', 'VAD', 'TRANS', 'POST', 'OUT' ]
    self.status = {
      'MIC': False,
      'VAD': False,
      'TRANS': False,
      'POST': False,
      'OUT': False
    }
    self.costs = 0
    self.time_recorded = 0
    for item in self.items:
      setattr(self, f'on{item}active', self.makeClosure(item, True))
      setattr(self, f'on{item}idle', self.makeClosure(item, False))

  def update(self):
    self.events.status_update_left(self.getStatusLineLeft())
    self.events.status_update_right(self.getStatusLineRight())

  def onUpdateActivity(self, op, status):
    self.status[op] = status
    self.events.status_update_left(self.getStatusLineLeft())

  def onUpdateCosts(self, new_costs):
    self.costs = new_costs
    self.events.status_update_right(self.getStatusLineRight())

  def onUpdateTimeRecorded(self, new_time):
    self.time_recorded = new_time
    self.events.status_update_center(self.getStatusLineCenter())

  def getStatusLineLeft(self):
    to_print = [ item if self.status[item] else '' for item in self.items ]
    status_line = '  ' + ''.join(f'{word:<6}' for word in to_print)
    return status_line

  def getStatusLineCenter(self):
    status_line = f'{int(self.time_recorded/60):02d}:{self.time_recorded%60:02d}'
    return status_line

  def getStatusLineRight(self):
    status_line = f'costs: {(self.costs / 100):.2f}$  '
    return status_line
