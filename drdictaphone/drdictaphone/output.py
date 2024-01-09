# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import os
import asyncio
import aiofiles
from mreventloop import emits, slot, has_event_loop, forwards
from drdictaphone.pipeline_events import PipelineEvents, PipelineSlots

@has_event_loop('event_loop')
@forwards(PipelineSlots)
@emits('events', PipelineEvents)
class Output:
  def __init__(self, filename = None):
    self.filename = filename
    with open(self.filename, 'a'):
      pass

  @slot
  async def onResult(self, result):
    if self.filename and result:
      async with aiofiles.open(self.filename, 'at') as file:
        await file.write(f'\n\n{result}')
    self.events.result(result)
