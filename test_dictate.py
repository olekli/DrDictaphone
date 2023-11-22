# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import difflib
from pydub import AudioSegment
from transcriber import Transcriber
from post_processor import PostProcessor
from pipeline import Pipeline
from audio_tools import normaliseFormat
from output import Output
from read_context import readContext
from file_stream import FileStream
from vad import Vad
import logger_config

class Output:
  def __init__(self):
    self.content = []

  def onFinalResult(self, content):
    self.content.append(content)

def dictate(context, audio_filename):
  context = readContext(context)
  vad = Vad()
  post_processor = PostProcessor(context, 'Dictate')
  transcriber = Transcriber(context.language)
  output = Output()
  with Pipeline([vad, transcriber, post_processor, output]) as pipeline:
    with FileStream(audio_filename, 1000, pipeline) as file_stream:
      pass
  return ' '.join(output.content)

expected = 'This is an example text to test the dictate functionality. This text will be spoken. There will be multiple audio files containing the voice data. Some will have additional silence added to them, especially in the middle of sentences. Some might have background noise. This is specifically designed to test the voice activity detection and the different patterns of segmenting the audio for transcription.'

expected_de = 'Dies ist ein Beispieltext, um die Diktierfunktion zu testen. Dieser Text wird gesprochen. Es wird mehrere Audiodateien geben, die die Sprachdaten enthalten. Einige werden zusätzliche Stille enthalten, besonders in der Mitte von Sätzen. Einige könnten Hintergrundgeräusche haben. Dies ist speziell dafür konzipiert, die Sprachaktivitätserkennung und die verschiedenen Muster der Audiosegmentierung für die Transkription zu testen.'

@pytest.mark.integration
def test_dictate_no_disruption():
  result = dictate('context/transcribe-en.yaml', 'test/speech-2.mp3')
  matcher = difflib.SequenceMatcher(None, result, expected)
  print(f'ratio: {matcher.ratio()}')
  assert matcher.ratio() > 0.95

@pytest.mark.integration
def test_dictate_some_disruption():
  result = dictate('context/transcribe-en.yaml', 'test/speech-2-gaps.mp3')
  matcher = difflib.SequenceMatcher(None, result, expected)
  print(f'ratio: {matcher.ratio()}')
  print(f'**** RESULT: {result}')
  assert matcher.ratio() > 0.95

@pytest.mark.integration
def test_dictate_no_disruption_non_english():
  result = dictate('context/transcribe-de.yaml', 'test/speech-2-de.mp3')
  matcher = difflib.SequenceMatcher(None, result, expected_de)
  print(f'ratio: {matcher.ratio()}')
  assert matcher.ratio() > 0.95
