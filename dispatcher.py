# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import  Thread
from queue import Queue

class Dispatcher:
  def __init__(self, input_queue, pipeline):
    self.pipeline = pipeline
    self.queue = input_queue
    self.worker_thread = Thread(target = self.worker)

  def __enter__(self):
    print('entering dispatcher')
    self.worker_thread.start()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.queue.put(None)
    self.worker_thread.join()
    print('exiting dispatcher')
    return True

  def worker(self):
    while True:
      item = self.queue.get()
      if item != None:
        self.pipeline(item)
      else:
        return

  def __call__(self, audio_segment):
    self.queue.put(audio_segment)
