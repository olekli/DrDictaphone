# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from dispatcher import Dispatcher
from collector import Collector
from pipeline import Pipeline

class DummyTranscriber:
  def __call__(self, textual_context, audio_segment):
    return f't{"".join(textual_context)}{audio_segment}'

class DummyPostProcessor:
  def __call__(self, textual_context, text):
    return f'p{"".join(textual_context)}{text}'

class DummyOutput:
  def __init__(self):
    self.content = []

  def __call__(self, text):
    self.content.append(text)

def test_dispatches_correctly():
  output = DummyOutput()
  collector = Collector(Pipeline(DummyTranscriber(), DummyPostProcessor()), output)
  with Dispatcher(collector) as dispatcher:
    dispatcher('1')
    dispatcher('2')
    dispatcher('3')
  assert collector.content == [ 'pt1', 'ppt1tpt12', 'ppt1ppt1tpt12tpt1ppt1tpt123' ]
  assert output.content == collector.content
