# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Thread
from queue import Queue
from events import Events
import logger

logger = logger.get(__name__)

class Display:
  def __init__(self, status_line):
    self.status_line = status_line
    self.total_cost = 0
    self.thread = Thread(target = self.run)
    self.queue = Queue()

  def onStatusUpdate(self, operation_name, new_status):
    self.queue.put((operation_name, new_status))

  def run(self):
    while True:
      item = self.queue.get()
      if item != None:
        operation_name, new_status = item
        self.status_line.update(operation_name, new_status)
      else:
        break

  def __enter__(self):
    self.thread.start()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.queue.put(None)
    self.thread.join()
