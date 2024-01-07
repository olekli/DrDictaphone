# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

class GptModel(BaseModel):
  model_config = ConfigDict(extra = 'forbid')

  name: str
  input_cost: float
  output_cost: float

  def __str__(self):
    return f'{self.name}, {self.input_cost}, {self.output_cost}'
