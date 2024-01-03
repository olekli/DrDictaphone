# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from mreventloop import connect, has_event_loop, emits, slot
from drdictaphone import logger

logger = logger.get(__name__)

@emits('events', [ 'active', 'idle' ])
@has_event_loop('event_loop')
class StatusAggregator:
  def __init__(self, emitters):
    self.statuses = { emitter: False for emitter in emitters }
    for emitter in [ e for e in emitters if e ]:
      connect(emitter, 'active', self, lambda emitter=emitter: self.onActive(emitter))
      connect(emitter, 'idle', self, lambda emitter=emitter: self.onIdle(emitter))

  @slot
  def onActive(self, emitter):
    self.statuses[emitter] = True
    self.events.active()

  @slot
  def onIdle(self, emitter):
    self.statuses[emitter] = False
    if not any(self.statuses.values()):
      self.events.idle()
