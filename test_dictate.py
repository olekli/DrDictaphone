# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import difflib
from pydub import AudioSegment
from transcriber import Transcriber
from post_processor import PostProcessor
from pipeline import Pipeline
from dispatcher import Dispatcher
from audio_tools import normaliseFormat
from output import Output
from read_context import readContext
from file_stream import FileStream
from vad import Vad
import logger_config

class Output:
  def __init__(self):
    self.content = []

  def __call__(self, content):
    self.content.append(content)

def dictate(audio_filename):
  context = readContext('context/transcribe-en.yaml')
  vad = Vad()
  post_processor = PostProcessor(context, 'Dictate')
  transcriber = Transcriber(context.language)
  output = Output()
  with Pipeline([vad, transcriber, post_processor, output]) as pipeline:
    with FileStream(audio_filename, 1000) as file_stream:
      with Dispatcher(file_stream.queue, pipeline) as dispatcher:
        pass
  return ' '.join(output.content)

expected = 'This is an example text to test the dictate functionality. This text will be spoken. There will be multiple audio files containing the voice data. Some will have additional silence added to them, especially in the middle of sentences. Some might have background noise. This is specifically designed to test the voice activity detection and the different patterns of segmenting the audio for transcription.'

@pytest.mark.integration
def test_dictate_no_disruption():
  result = dictate('test/speech-2.mp3')
  matcher = difflib.SequenceMatcher(None, result, expected)
  print(f'ratio: {matcher.ratio()}')
  assert matcher.ratio() > 0.95

@pytest.mark.integration
def test_dictate_some_disruption():
  result = dictate('test/speech-2-gaps.mp3')
  matcher = difflib.SequenceMatcher(None, result, expected)
  print(f'ratio: {matcher.ratio()}')
  assert matcher.ratio() > 0.95
