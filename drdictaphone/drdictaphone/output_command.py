# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import asyncio
from mreventloop import emits, slot, has_event_loop, forwards
from drdictaphone.pipeline_events import PipelineEvents, PipelineSlots
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
@forwards(PipelineSlots)
@emits('events', PipelineEvents)
class OutputCommand:
  def __init__(self, command):
    self.command = command

  @slot
  async def onResult(self, result):
    process = await asyncio.create_subprocess_exec(
      self.command,
      stdin = asyncio.subprocess.PIPE,
      stdout = asyncio.subprocess.PIPE,
      stderr = asyncio.subprocess.PIPE,
    )
    output, error = await process.communicate(input = result.encode())
    if process.returncode != 0:
      logger.error(f'Output command reports error: {error}')
    self.events.result(result)
