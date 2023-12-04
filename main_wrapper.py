# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from main import Main
from pipeline_events import PipelineEvents
from event_loop import EventLoop, connect,forwardEvents
import logger

logger = logger.get(__name__)

class MainWrapper:
  def __init__(self):
    self.events = PipelineEvents()
    self.__event_loop__ = EventLoop()
    forwardEvents(self, [ 'start_rec', 'stop_rec' ])
    self.main = None
    self.result = ''

  def setProfile(self, profile_name):
    if self.main:
      self.main.__exit__(None, None, None)
    self.main = Main(profile_name)
    connect(self, [ 'start_rec', 'stop_rec', 'clear_buffer' ], self.main.pipeline, None)
    connect(self.main.aggregator, 'result', self.onResult)
    connect(self.main.aggregator, 'fence', self.onFence)
    self.main.__enter__()

  def onResult(self, result):
    self.result = result

  def onFence(self):
    self.events.result(self.result)
    self.events.clear_buffer()

  def __enter__(self):
    self.__event_loop__.__enter__()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    return self.__event_loop__.__exit__(exc_type, exc_value, traceback)
