# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from events import Events

class CostCounter:
  def __init__(self):
    self.events = Events(('updated'))
    self.total_costs = 0

  def addCosts(self, costs):
    self.total_costs += costs
    self.events.updated(self.total_costs)
