# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from queue import SimpleQueue
from threading import Thread
from events import Events
import logger

logger = logger.get(__name__)

def makeSlotName(event_name):
  segments = event_name.split('_')
  return 'on' + ''.join([ segment.capitalize() for segment in segments ])

def connect_(emitter, event_name, receiver, slot_name):
  listeners = getattr(emitter.events, event_name)
  listeners += lambda payload = None: receiver.__event_loop__.enqueue(receiver, slot_name, payload)
  setattr(emitter.events, event_name, listeners)
  logger.debug(f'connecting {emitter.__class__.__name__} {event_name} -> {receiver.__class__.__name__} {slot_name}')

def connect(emitter, event_name, receiver, slot_name):
  if event_name == None and slot_name == None:
    for event_name in emitter.events.__events__:
      slot_name = makeSlotName(event_name)
      if not getattr(receiver, slot_name, None) and event_name in receiver.events.__events__:
        forwardEvents(receiver, [event_name])
      if callable(getattr(receiver, slot_name, None)):
        connect_(emitter, event_name, receiver, slot_name)
  elif event_name == None or slot_name == None:
    assert False
  else:
    connect_(emitter, event_name, receiver, slot_name)

def forwardEvents(self, event_names):
  for event_name in event_names:
    setattr(
      self,
      makeSlotName(event_name),
      getattr(self.events, event_name)
    )

def associateWithEventLoop(receiver, event_loop):
  receiver.__event_loop__ = event_loop

class EventLoop:
  def __init__(self):
    self.events = Events(('active', 'idle'))
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
    self.events.idle()
    item = self.queue.get()
    while item != None:
      self.events.active()
      receiver, slot_name, payload = item
      if payload == None:
        getattr(receiver, slot_name)()
      else:
        getattr(receiver, slot_name)(payload)
      self.events.idle()
      item = self.queue.get()
