# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from dispatcher import Dispatcher
from pipeline import Pipeline
from events import Events
from queue import Queue

class DummyTranscriber:
  def __init__(self):
    self.events = Events(('result'))

  def __call__(self, audio_segment):
    self.events.result(f't{audio_segment}')

class DummyPostProcessor:
  def __init__(self):
    self.events = Events(('result'))

  def __call__(self, text):
    self.events.result(f'p{text}')

class DummyOutput:
  def __init__(self):
    self.events = Events(('result'))
    self.content = []

  def __call__(self, text):
    self.content.append(text)

def test_dispatches_correctly():
  output = DummyOutput()
  queue = Queue()
  pipeline = Pipeline([DummyTranscriber(), DummyPostProcessor(), output])
  with Dispatcher(queue, pipeline) as dispatcher:
    queue.put('1')
    queue.put('2')
    queue.put('3')
  assert output.content == [ 'pt1', 'pt2', 'pt3' ]
