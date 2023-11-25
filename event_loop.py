# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from queue import SimpleQueue
from threading import Thread
from events import Events

def connect_(emitter, event_name, receiver, slot_name):
  listeners = getattr(emitter.events, event_name)
  listeners += lambda payload = None: receiver.__event_loop__.enqueue(receiver, slot_name, payload)
  setattr(emitter.events, event_name, listeners)

def connect(emitter, event_name, receiver, slot_name):
  if event_name == None and slot_name == None:
    for event_name in emitter.events.__events__:
      slot_name = f'on{event_name.capitalize()}'
      if callable(getattr(receiver, slot_name, None)):
        connect_(emitter, event_name, receiver, f'on{event_name.capitalize()}')
  elif event_name == None or slot_name == None:
    assert False
  else:
    connect_(emitter, event_name, receiver, slot_name)

def associateWithEventLoop(receiver, event_loop):
  receiver.__event_loop__ = event_loop

class EventLoop:
  def __init__(self):
    self.queue = SimpleQueue()
    self.thread = Thread(target = self.run)

  def enqueue(self, receiver, slot_name, payload):
    self.queue.put( (receiver, slot_name, payload) )

  def __enter__(self):
    self.thread.start()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.queue.put(None)
    self.thread.join()

  def run(self):
    item = self.queue.get()
    while item != None:
      receiver, slot_name, payload = item
      if payload == None:
        getattr(receiver, slot_name)()
      else:
        getattr(receiver, slot_name)(payload)
      item = self.queue.get()
