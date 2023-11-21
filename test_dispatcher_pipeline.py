# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from dispatcher import Dispatcher
from pipeline import Pipeline
from events import Events

class DummyTranscriber:
  def __init__(self):
    self.events = Events(('result'))

  def __call__(self, context, audio_segment):
    self.events.result(f't{"".join(context)}{audio_segment}')

class DummyPostProcessor:
  def __init__(self):
    self.events = Events(('result'))

  def __call__(self, context, text):
    self.events.result(f'p{"".join(context)}{text}')

class DummyOutput:
  def __init__(self):
    self.events = Events(('result'))
    self.content = []

  def __call__(self, context, text):
    self.content.append(text)
    self.events.result(text)

def test_dispatches_correctly():
  output = DummyOutput()
  pipeline = Pipeline([DummyTranscriber(), DummyPostProcessor(), output])
  with Dispatcher(pipeline) as dispatcher:
    dispatcher('1')
    dispatcher('2')
    dispatcher('3')
  assert pipeline.content == [ 'pt1', 'ppt1tpt12', 'ppt1ppt1tpt12tpt1ppt1tpt123' ]
  assert output.content == pipeline.content
