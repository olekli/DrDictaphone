# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from .context import Context
from .gpt_model import GptModel
from .options import Options
from .instructions import Instructions

class Profile(BaseModel):
  model_config = ConfigDict(extra = 'forbid')

  id: str
  post_processor: Context
  topic: Instructions
  gpt_model: Optional[GptModel]
  options: Optional[Options]
  language: str
  output: Optional[str]
  output_command: Optional[str]
  enable_vad: bool = False

  def __str__(self):
    return f'{self.id}: {self.post_processor}, {self.topic}, {self.gpt_model}, {self.options}, {self.language}, {self.output}, {self.output_command}, {self.enable_vad}'
