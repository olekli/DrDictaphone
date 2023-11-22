# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Any
from enum import Enum

class PipelineResultType(Enum):
  Temporary = 'temporary'
  Final = 'final'
  Shutdown = 'shutdown'

class PipelineResult(BaseModel):
  model_config = ConfigDict(extra = 'forbid')

  type: PipelineResultType
  value: Any
