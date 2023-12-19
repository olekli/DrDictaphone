# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from .context import Context
from .gpt_model import GptModel
from .options import Options
from .instructions import Instructions

class Profile(BaseModel):
  model_config = ConfigDict(extra = 'forbid')

  post_processor: Context
  topic: Instructions
  gpt_model: Optional[GptModel]
  options: Optional[Options]
  language: str
  output: str
  output_command: Optional[str]
  enable_vad: bool = False
  raw: dict

  def __str__(self):
    return f'{self.post_processor}, {self.topic}, {self.gpt_model}, {self.options}, {self.language}, {self.output}, {self.output_command}, {self.enable_vad}'
