# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from transcriber import Transcriber
from pydub import AudioSegment

class Result:
  def __init__(self):
    self.result = ''

  def onResult(self, result):
    self.result = result

@pytest.mark.integration
def test_transcription():
  transcriber = Transcriber('en')
  result = Result()
  transcriber.events.result += result.onResult
  transcriber('', AudioSegment.from_mp3('test/speech.mp3'))
  assert result.result == 'This is a test. One, two, three. This is a test.'

@pytest.mark.integration
def test_weird_context_behaviour():
  transcriber = Transcriber('en')
  result = Result()
  transcriber.events.result += result.onResult
  transcriber('Some context', AudioSegment.from_mp3('test/speech.mp3'))
  assert result.result == 'This is a test 123. This is a test.'
