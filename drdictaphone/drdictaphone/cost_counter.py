# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from mreventloop import emits, slot, has_event_loop, forwards
from drdictaphone.pipeline_events import PipelineEvents, PipelineSlots
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
@forwards(PipelineSlots)
@emits('events', PipelineEvents)
class CostCounter:
  def __init__(self):
    self.total_costs = 0

  @slot
  def onCostsIncurred(self, costs):
    logger.debug(f'recording costs: {costs}')
    self.total_costs += costs
    self.events.costs_incurred(self.total_costs)
