# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
from pipeline_events import PipelineEvents
import logger

logger = logger.get(__name__)

class OutputCommand:
  def __init__(self, command):
    self.events = PipelineEvents()
    self.command = command

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

  def onFence(self):
    self.events.fence()
