# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from mreventloop import emits, slot
from drdictaphone.pipeline import Pipeline

@emits('events', [ 'result', 'fence' ])
class DummyTranscriber:
  def __init__(self):
    pass

  @slot
  def onResult(self, audio_segment):
    self.events.result(f't{audio_segment}')

  @slot
  def onFence(self):
    pass

@emits('events', [ 'result', 'fence' ])
class DummyPostProcessor:
  def __init__(self):
    pass

  @slot
  def onResult(self, text):
    self.events.result(f'p{text}')

  @slot
  def onFence(self):
    pass

@emits('events', [ 'result', 'fence' ])
class DummyOutput:
  content = []

  def __init__(self):
    pass

  @slot
  def onResult(self, text):
    DummyOutput.content.append(text)

  @slot
  def onFence(self):
    pass

def test_dispatches_correctly():
  with Pipeline([DummyTranscriber(), DummyPostProcessor(), DummyOutput()]) as pipeline:
    pipeline.events.result('1')
    pipeline.events.result('2')
    pipeline.events.result('3')
  assert DummyOutput.content == [ 'pt1', 'pt2', 'pt3' ]
