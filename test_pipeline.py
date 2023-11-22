# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pipeline import Pipeline
from events import Events
from queue import Queue
from model.PipelineResult import PipelineResult, PipelineResultType

class DummyTranscriber:
  def __init__(self):
    self.events = Events(('final_result', 'temporary_result'))

  def onFinalResult(self, audio_segment):
    self.events.final_result(f't{audio_segment}')

class DummyPostProcessor:
  def __init__(self):
    self.events = Events(('final_result', 'temporary_result'))

  def onFinalResult(self, text):
    self.events.final_result(f'p{text}')

class DummyOutput:
  def __init__(self):
    self.events = Events(('final_result', 'temporary_result'))
    self.content = []

  def onFinalResult(self, text):
    self.content.append(text)

def test_dispatches_correctly():
  output = DummyOutput()
  queue = Queue()
  with Pipeline([DummyTranscriber(), DummyPostProcessor(), output]) as pipeline:
    pipeline('1')
    pipeline('2')
    pipeline('3')
  assert output.content == [ 'pt1', 'pt2', 'pt3' ]
