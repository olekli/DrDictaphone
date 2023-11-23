# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Thread
from queue import Queue
from events import Events
import logger
from model.PipelineResult import PipelineResult, PipelineResultType

logger = logger.get(__name__)

class ConcurrentOperation:
  def __init__(self, operation_factory):
    self.events = Events(('result', 'fence'))
    self.operation_factory = operation_factory
    self.thread = Thread(target = self.run)
    self.queue = Queue()

  def queueResult(self, item):
    self.queue.put(PipelineResult(type = PipelineResultType.Result, value = item))
    #logger.debug(f'{self.operation.__class__.__name__} queue: {self.queue.qsize()}')

  def queueFence(self):
    self.queue.put(PipelineResult(type = PipelineResultType.Fence, value = None))
    #logger.debug(f'{self.operation.__class__.__name__} queue: {self.queue.qsize()}')

  def run(self):
    operation = self.operation_factory()
    operation.events.result += self.events.result
    operation.events.fence += self.events.fence
    if callable(getattr(operation, '__enter__', None)):
      operation.__enter__()
    while True:
      next_result = self.queue.get()
      cached_temporary_result = None
      if next_result.type == PipelineResultType.Result:
        operation.onResult(next_result.value)
      elif next_result.type == PipelineResultType.Fence:
        operation.onFence()
      elif next_result.type == PipelineResultType.Shutdown:
        operation.onFence()
        break
    if callable(getattr(operation, '__exit__', None)):
      operation.__exit__(None, None, None)

  def __enter__(self):
    self.thread.start()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.queue.put(PipelineResult(type = PipelineResultType.Shutdown, value = None))
    self.thread.join()
