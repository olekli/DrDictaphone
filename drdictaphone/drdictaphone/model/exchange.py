# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from pydantic import BaseModel, ConfigDict

class Exchange(BaseModel):
  model_config = ConfigDict(extra = 'forbid')

  user_message: str
  assistant_message: str

  def __str__(self):
    return f'Q: {self.user_message}\nR: {self.assistant_message}'
