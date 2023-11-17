# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

class Options(BaseModel):
  model_config = ConfigDict(extra = 'forbid')

  model: str
  temperature: float
  max_tokens: int

  def __str__(self):
    return f'{self.model}, {self.temperature}, {self.max_tokens}'
