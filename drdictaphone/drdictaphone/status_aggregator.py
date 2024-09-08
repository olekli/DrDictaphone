# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from mreventloop import connect, has_event_loop, emits, slot
from drdictaphone import logger

logger = logger.get(__name__)

@emits('events', [ 'active', 'idle' ])
@has_event_loop('event_loop')
class StatusAggregator:
  def __init__(self, emitters):
    self.statuses = { emitter: False for emitter in emitters if emitter }
    for emitter in [ e for e in emitters if e ]:
      connect(emitter, 'active', lambda emitter=emitter: self.onActive(emitter))
      connect(emitter, 'idle', lambda emitter=emitter: self.onIdle(emitter))

  @slot
  def onActive(self, emitter):
    self.statuses[emitter] = True
    self.events.active()

  @slot
  def onIdle(self, emitter):
    self.statuses[emitter] = False
    if not any(self.statuses.values()):
      self.events.idle()
