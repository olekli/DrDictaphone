# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Thread
from queue import SimpleQueue
import logger
from model.PipelineResult import PipelineResult, PipelineResultType

logger = logger.get(__name__)

class ConcurrentOperation:
  def __init__(self, operation):
    self.operation = operation
    self.thread = Thread(target = self.run)
    self.queue = SimpleQueue()

  def queueFinalResult(self, item):
    self.queue.put(PipelineResult(type = PipelineResultType.Final, value = item))

  def queueTemporaryResult(self, item):
    self.queue.put(PipelineResult(type = PipelineResultType.Temporary, value = item))

  def queueFence(self):
    self.queue.put(PipelineResult(type = PipelineResultType.Fence, value = None))

  def run(self):
    while True:
      next_result = self.queue.get()
      cached_temporary_result = None
      if next_result.type == PipelineResultType.Final:
        self.operation.onFinalResult(next_result.value)
      elif next_result.type == PipelineResultType.Fence:
        self.operation.onFence()
      elif (next_result.type == PipelineResultType.Temporary) and self.queue.empty():
        self.operation.onTemporaryResult(next_result.value)
      elif (next_result.type == PipelineResultType.Temporary) and not self.queue.empty():
        cached_temporary_result = next_result
      elif next_result.type == PipelineResultType.Shutdown:
        if cached_temporary_result:
          self.operation.onFinalResult(cached_temporary_result.value)
          self.operation.onFence()
        return

  def __enter__(self):
    self.thread.start()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.queue.put(PipelineResult(type = PipelineResultType.Shutdown, value = None))
    self.thread.join()
