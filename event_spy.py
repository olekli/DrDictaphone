# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from events import Events
from event_loop import makeSlotName

class EventSpy:
  def __init__(self, events):
    self.events = Events(tuple(events))
    for event in events:
      setattr(self, event, list())
      setattr(
        self, makeSlotName(event),
        lambda item, event = event: setattr(self, event, getattr(self, event) + [item])
      )
