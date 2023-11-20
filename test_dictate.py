# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydub import AudioSegment
from transcriber import Transcriber
from post_processor import PostProcessor
from pipeline import Pipeline
from collector import Collector
from dispatcher import Dispatcher
from recorder import Recorder
from audio_tools import normaliseFormat
from output import Output
from read_context import readContext
from file_stream import FileStream

class Output:
  def __init__(self):
    self.content = ''

  def __call__(self, content):
    self.content += f'{content} '

def dictate(audio_filename):
  context = readContext('context/transcribe-en.yaml')
  transcriber = Transcriber(context.language)
  post_processor = PostProcessor(context, 'Dictate')
  output = Output()
  collector = Collector(Pipeline(transcriber, post_processor), output)
  with FileStream(audio_filename, 1000) as file_stream:
    with Dispatcher(collector) as dispatcher:
      with Recorder(file_stream.queue, dispatcher):
        pass
  print(f'RESULT: {output.content}')
  return output.content

@pytest.mark.integration
def test_dictate_no_disruption():
  result = dictate('test/speech-2.mp3')
  assert result == 'This is an example text to test the dictate functionality. This text will be spoken. There will be multiple audio files containing the voice data. Some will have additional silence added to them, especially in the middle of sentences. Some might have background noise. This is specifically designed to test the voice activity detection and the different patterns of segmenting the audio for transcription. '

@pytest.mark.integration
def test_dictate_some_disruption():
  result = dictate('test/speech-2-gaps.mp3')
  assert result == 'This is an example text to test the dictation functionality. This text will be spoken. There will be multiple audio files containing the voice data. Some will have additional silence added to them, especially in the middle of sentences. Some might have background noise. This is specifically designed to test the voice activity detection and the different patterns of segmenting the audio for transcription. '
