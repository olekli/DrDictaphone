# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from drdictaphone.pipeline_events import PipelineEvents

class CostCounter:
  def __init__(self):
    self.events = PipelineEvents()
    self.total_costs = 0

  def onCosts(self, costs):
    self.total_costs += costs
    self.events.costs(self.total_costs)
