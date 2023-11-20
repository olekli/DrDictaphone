# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from pydub import AudioSegment
import tempfile
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os

class Transcriber:
  def __init__(self, language):
    self.language = language

  def saveToTempFile(self, audio_segment):
    temp_file = tempfile.NamedTemporaryFile(
      prefix = "recorded_audio_",
      suffix = ".mp3",
      delete = False
    )
    audio_segment.export(temp_file.name, format = 'mp3')
    return temp_file.name

  def transcribeAudio(self, textual_context, temp_file):
    client = OpenAI(api_key = os.environ.get('API_KEY', ''))
    audio_file = open(temp_file, 'rb')
    transcript = client.audio.transcriptions.create(
      model = "whisper-1",
      file = audio_file,
      language = self.language,
      prompt = '\n'.join(textual_context)
    )
    #print(f'WHISPER: {transcript.text} {temp_file} {textual_context}')
    return transcript.text

  def __call__(self, textual_context, audio_segment):
    return self.transcribeAudio(textual_context, self.saveToTempFile(audio_segment))
