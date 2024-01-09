
# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from mreventloop import emits, has_event_loop, slot

@has_event_loop('event_loop')
@emits('events', [ 'updated' ])
class StatusManager:
  def __init__(self):
    self.status = {
      'profile_name': 'no profile selected',
      'mic': False,
      'processing': False,
      'error': False,
      'costs': 0.0,
    }

  @slot
  def onStartRec(self):
    self.status['mic'] = True
    self.events.updated(self.status)

  @slot
  def onStopRec(self):
    self.status['mic'] = False
    self.events.updated(self.status)

  @slot
  def onStartProcessing(self):
    self.status['processing'] = True
    self.events.updated(self.status)

  @slot
  def onStopProcessing(self):
    self.status['processing'] = False
    self.events.updated(self.status)

  @slot
  def onErrorSet(self):
    self.status['error'] = True
    self.events.updated(self.status)

  @slot
  def onErrorUnset(self):
    self.status['error'] = False
    self.events.updated(self.status)

  @slot
  def onProfileChange(self, profile):
    self.status['profile_name'] = profile.id
    self.events.updated(self.status)

  @slot
  def onCostsIncurred(self, costs):
    self.status['costs'] = costs
    self.events.updated(self.status)

  @slot
  def onQueryStatus(self):
    self.events.updated(self.status)
