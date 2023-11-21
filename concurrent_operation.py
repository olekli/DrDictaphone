# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Thread
from queue import SimpleQueue
import logger

logger = logger.get(__name__)

class ConcurrentOperation:
  def __init__(self, operation):
    self.operation = operation
    self.thread = Thread(target = self.run)
    self.queue = SimpleQueue()

  def __call__(self, item):
    self.queue.put(item)

  def run(self):
    while True:
      item = self.queue.get()
      if item != None:
        self.operation(item)
      else:
        return

  def __enter__(self):
    self.thread.start()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.queue.put(None)
    self.thread.join()
    return True
