# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from .gpt_model import GptModel
from .options import Options
from .instructions import Instructions
from .tools import Tools

class Context(BaseModel):
  model_config = ConfigDict(extra = 'forbid')

  gpt_model: GptModel
  options: Options
  instructions: Instructions
  topic: Instructions
  language: str
  tools: Optional[Tools]

  def __str__(self):
    return f'{self.gpt_model}, {self.options}, {self.instructions}, {self.language}, {self.tools}'
