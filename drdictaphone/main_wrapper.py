# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from mreventloop import emits, slot, supports_event_loop, forwards, EventLoop
from drdictaphone.main import Main
from drdictaphone.pipeline_events import PipelineEvents
from drdictaphone import logger

logger = logger.get(__name__)

@supports_event_loop('event_loop')
@forwards( [ 'onStartRec', 'onStopRec' ] )
@emits('events', PipelineEvents)
class MainWrapper:
  def __init__(self):
    self.event_loop = EventLoop()
    self.main = None
    self.result = ''

  def setProfile(self, profile_name):
    if self.main:
      self.main.__exit__(None, None, None)
    self.main = Main(profile_name)
    connect(self, [ 'start_rec', 'stop_rec', 'clear_buffer' ], self.main.pipeline, None)
    connect(self.main.aggregator, 'result', self, 'onResult')
    connect(self.main.aggregator, 'fence', self, 'onFence')
    self.main.__enter__()

  @slot
  def onResult(self, result):
    self.result = result

  @slot
  def onFence(self):
    self.events.result(self.result)
    self.events.clear_buffer()

  def __enter__(self):
    self.event_loop.__enter__()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    return self.event_loop.__exit__(exc_type, exc_value, traceback)
