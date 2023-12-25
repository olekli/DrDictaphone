# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from mreventloop import emits, slot, has_event_loop
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
@emits('events', [ 'status_update' ])
class ServerStatusLine:
  def __init__(self):
    self.profile_name = ''
    self.items = [ 'MIC', 'PROCESSING' ]
    self.status = {
      'MIC': False,
      'PROCESSING': False,
    }
    self.costs = 0

  @slot
  def onProfileChange(self, profile):
    self.profile_name = profile.id
    self.update()

  @slot
  def onRecording(self, status):
    self.status['MIC'] = status
    self.update()

  @slot
  def onProcessing(self, status):
    self.status['PROCESSING'] = status
    self.update()

  @slot
  def onCostsUpdate(self, costs):
    self.costs = costs
    self.update()

  def update(self):
    to_print = [ item if self.status[item] else '' for item in self.items ]
    left = '  ' + ''.join(f'{word:<6}' for word in to_print)
    right = f'{self.profile_name}      costs: {(self.costs / 100):.2f}$  '
    self.events.status_update({ 'left': left, 'right': right  })
