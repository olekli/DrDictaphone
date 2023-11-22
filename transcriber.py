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
  cost_second = (0.6 / 60)

  def __init__(self, language):
    self.language = language
    self.events = Events(('result', 'fence'))
    self.context = []
    self.buffer = AudioSegment.empty()
    self.total_length = 0
    self.total_cost = 0

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
      self.total_length += round(len(self.buffer) / 1000)
      self.total_cost = round(self.total_length * Transcriber.cost_second)
      logger.debug(f'total cost: {self.total_cost}')
      logger.debug(f'whisper replied: {transcript.text}')
      logger.debug(f'context was: {self.context}')
      return transcript.text

  def onResult(self, audio_segment):
    self.buffer += audio_segment
    text = self.transcribeBuffer()
    self.events.result(text)

  def onFence(self):
    if len(self.buffer) > 0:
      text = self.transcribeBuffer()
      self.context.append(text)
      self.buffer = AudioSegment.empty()
      self.events.result(text)
      self.events.fence()
