# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from mreventloop import emits, slot, has_event_loop_thread
from drdictaphone.pipeline_events import PipelineEvents

@has_event_loop_thread('event_loop')
@emits('events', PipelineEvents)
class CostCounter:
  def __init__(self):
    self.total_costs = 0

  @slot
  def onCosts(self, costs):
    self.total_costs += costs
    self.events.costs(self.total_costs)
