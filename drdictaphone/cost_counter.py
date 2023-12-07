# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from mreventloop import emits, slot, supports_event_loop
from drdictaphone.pipeline_events import PipelineEvents

@supports_event_loop('event_loop')
@emits('events', PipelineEvents)
class CostCounter:
  def __init__(self):
    self.total_costs = 0

  @slot
  def onCosts(self, costs):
    self.total_costs += costs
    self.events.costs(self.total_costs)
