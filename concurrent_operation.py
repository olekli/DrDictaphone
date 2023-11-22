# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Thread
from queue import Queue
import logger
from model.PipelineResult import PipelineResult, PipelineResultType

logger = logger.get(__name__)

class ConcurrentOperation:
  def __init__(self, operation):
    self.operation = operation
    self.thread = Thread(target = self.run)
    self.queue = Queue()

  def queueResult(self, item):
    self.queue.put(PipelineResult(type = PipelineResultType.Result, value = item))
    logger.debug(f'{self.operation.__class__.__name__} queue: {self.queue.qsize()}')

  def queueFence(self):
    self.queue.put(PipelineResult(type = PipelineResultType.Fence, value = None))
    logger.debug(f'{self.operation.__class__.__name__} queue: {self.queue.qsize()}')

  def run(self):
    while True:
      next_result = self.queue.get()
      cached_temporary_result = None
      if next_result.type == PipelineResultType.Result:
        self.operation.onResult(next_result.value)
      elif next_result.type == PipelineResultType.Fence:
        self.operation.onFence()
      elif next_result.type == PipelineResultType.Shutdown:
        self.operation.onFence()
        return

  def __enter__(self):
    self.thread.start()
    if callable(getattr(self.operation, '__enter__', None)):
      self.operation.__enter__()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.queue.put(PipelineResult(type = PipelineResultType.Shutdown, value = None))
    self.thread.join()
    if callable(getattr(self.operation, '__exit__', None)):
      return self.operation.__exit__(exc_type, exc_value, traceback)
