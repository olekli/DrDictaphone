# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import  Thread
from queue import Queue

class Dispatcher:
  def __init__(self, collector):
    self.collector = collector
    self.queue = Queue()
    self.worker_thread = Thread(target = self.worker)

  def __enter__(self):
    self.worker_thread.start()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.queue.put(None)
    self.worker_thread.join()
    return True

  def worker(self):
    while True:
      item = self.queue.get()
      if item != None:
        self.collector(item)
      else:
        return

  def __call__(self, audio_segment):
    self.queue.put(audio_segment)
