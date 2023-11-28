# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from .context import Context

class Profile(BaseModel):
  model_config = ConfigDict(extra = 'forbid')

  context: Context
  output: str
  enable_vad: bool = False

  def __str__(self):
    return f'{self.context}, {self.output}, {self.enable_vad}'
