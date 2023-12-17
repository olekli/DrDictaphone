# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

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
    self.last_final_pos = 0
    with open(self.filename, 'a'):
      pass
    with open(self.filename, 'rt') as file:
      file.seek(0, os.SEEK_END)
      self.last_final_pos = file.tell()

  @slot
  async def onResult(self, result):
    if self.filename:
      async with aiofiles.open(self.filename, 'r+t') as file:
        await file.seek(self.last_final_pos)
        await file.truncate()
        await file.write(f'\n{result}\n')
    self.events.result(result)

  @slot
  async def onFence(self):
    async with aiofiles.open(self.filename, 'rt') as file:
      await file.seek(0, os.SEEK_END)
      self.last_final_pos = await file.tell()
    self.events.fence()
