# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from pydub import AudioSegment
import tempfile
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
from events import Events
import logger
logger = logger.get(__name__)

class Transcriber:
  def __init__(self, language):
    self.language = language
    self.events = Events(('final_result', 'temporary_result', 'fence'))
    self.context = []
    self.buffer = AudioSegment.empty()

  def transcribeBuffer(self):
    with tempfile.NamedTemporaryFile(
      prefix = "recorded_audio_",
      suffix = ".mp3",
      delete = True
    ) as temp_file:
      self.buffer.export(temp_file.name, format = 'mp3')
      audio_file = open(temp_file.name, 'rb')
      client = OpenAI(api_key = os.environ.get('API_KEY', ''))
      transcript = client.audio.transcriptions.create(
        model = "whisper-1",
        file = audio_file,
        language = self.language,
        prompt = ' '.join(self.context)
      )
      logger.debug(f'whisper replied: {transcript.text}')
      logger.debug(f'context was: {self.context}')
      return transcript.text

  def onFinalResult(self, audio_segment):
    self.buffer += audio_segment
    text = self.transcribeBuffer()
    self.events.temporary_result(text)

  def onFence(self):
    if len(self.buffer) > 0:
      text = self.transcribeBuffer()
      self.context.append(text)
      self.buffer = AudioSegment.empty()
      self.events.final_result(text)
      self.events.fence()

  def onTemporaryResult(self, audio_segment):
    assert False
