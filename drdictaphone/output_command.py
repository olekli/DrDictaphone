# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
from mreventloop import emits, slot, has_event_loop_thread
from drdictaphone.pipeline_events import PipelineEvents
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop_thread('event_loop')
@emits('events', PipelineEvents)
class OutputCommand:
  def __init__(self, command):
    self.command = command

  @slot
  def onResult(self, result):
    process = subprocess.Popen(
      self.command,
      stdin = subprocess.PIPE,
      stdout = subprocess.PIPE,
      stderr = subprocess.PIPE,
      text = True
    )
    output, error = process.communicate(input = result)
    if process.returncode != 0:
      logger.error(f'Output command reports error: {error}')
    self.events.result(result)

  @slot
  def onFence(self):
    self.events.fence()
