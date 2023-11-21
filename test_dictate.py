# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
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
    self.content = ''

  def __call__(self, content):
    self.content += f'{content} '

def dictate(audio_filename):
  context = readContext('context/transcribe-en.yaml')
  vad = Vad()
  post_processor = PostProcessor(context, 'Dictate')
  transcriber = Transcriber(context.language)
  output = Output()
  pipeline = Pipeline([vad, transcriber, post_processor])
  with FileStream(audio_filename, 1000) as file_stream:
    with Dispatcher(file_stream.queue, pipeline) as dispatcher:
      pass
  print(f'RESULT: {output.content}')
  return ' '.join(pipeline.content)

@pytest.mark.integration
def test_dictate_no_disruption():
  result = dictate('test/speech-2.mp3')
  assert result == 'This is an example text to test the dictate functionality. This text will be spoken. There will be multiple audio files containing the voice data. Some will have additional silence added to them, especially in the middle of sentences. Some might have background noise. This is specifically designed to test the voice activity detection and the different patterns of segmenting the audio for transcription.'

@pytest.mark.integration
def test_dictate_some_disruption():
  result = dictate('test/speech-2-gaps.mp3')
  assert result == 'This is an example text to test the dictation functionality. This text will be spoken. There will be multiple audio files containing the voice data. Some will have additional silence added to them, especially in the middle of sentences. Some might have background noise. This is specifically designed to test the voice activity detection and the different patterns of segmenting the audio for transcription.'
