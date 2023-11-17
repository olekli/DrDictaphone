# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
from typing import List
from pydantic import BaseModel, ConfigDict

from .Options import Options

class Context(BaseModel):
  model_config = ConfigDict(extra = 'forbid')

  system: List[str]
  options: Options
  language: str

  def __str__(self):
    result = str(self.options)
    for m in self.system:
      result += f'\nS: {m}'
    return result
