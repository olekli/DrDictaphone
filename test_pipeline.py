# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pipeline import Pipeline
from events import Events
from queue import Queue
from model.PipelineResult import PipelineResult, PipelineResultType

class DummyTranscriber:
  def __init__(self):
    self.events = Events(('result', 'fence'))

  def onResult(self, audio_segment):
    self.events.result(f't{audio_segment}')

  def onFence(self):
    pass

class DummyPostProcessor:
  def __init__(self):
    self.events = Events(('result', 'fence'))

  def onResult(self, text):
    self.events.result(f'p{text}')

  def onFence(self):
    pass

class DummyOutput:
  content = []

  def __init__(self):
    self.events = Events(('result', 'fence'))

  def onResult(self, text):
    DummyOutput.content.append(text)

  def onFence(self):
    pass

def test_dispatches_correctly():
  queue = Queue()
  with Pipeline([DummyTranscriber, DummyPostProcessor, DummyOutput]) as pipeline:
    pipeline('1')
    pipeline('2')
    pipeline('3')
  assert DummyOutput.content == [ 'pt1', 'pt2', 'pt3' ]
