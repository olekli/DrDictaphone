# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
from typing import List
from pydantic import BaseModel, ConfigDict

from .Context import Context
from .Exchange import Exchange

class Conversation(BaseModel):
  model_config = ConfigDict(extra = 'forbid')

  context: Context
  topic: str
  history: List[Exchange]

  def __str__(self):
    result = f'{self.context}\n'
    result += f'T: {self.topic}'
    for e in self.history:
      result += f'\n{e}'
    return result
