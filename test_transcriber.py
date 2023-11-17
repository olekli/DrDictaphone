# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from transcriber import Transcriber
from pydub import AudioSegment

@pytest.mark.integration
def test_transcription():
  transcriber = Transcriber('en')
  result = transcriber('', AudioSegment.from_mp3('test/speech.mp3'))
  assert result == 'This is a test. One, two, three. This is a test.'

@pytest.mark.integration
def test_weird_context_behaviour():
  transcriber = Transcriber('en')
  result = transcriber('Some context', AudioSegment.from_mp3('test/speech.mp3'))
  assert result == 'This is a test 123. This is a test.'
