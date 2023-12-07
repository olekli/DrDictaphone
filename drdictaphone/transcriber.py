# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from pydub import AudioSegment
import tempfile
from openai import OpenAI
from mreventloop import emits, slot, supports_event_loop
from drdictaphone.pipeline_events import PipelineEvents
from drdictaphone.config import config
from drdictaphone import logger
logger = logger.get(__name__)

@supports_event_loop('event_loop')
@emits('events', PipelineEvents)
class Transcriber:
  cost_second = (0.6 / 60)

  def __init__(self, language):
    self.language = language
    self.context = []
    self.buffer = AudioSegment.empty()
    self.text_buffer = ''
    self.mark = 0

  def transcribeBuffer(self):
    with tempfile.NamedTemporaryFile(
      prefix = "recorded_audio_",
      suffix = ".mp3",
      delete = True
    ) as temp_file:
      self.buffer.export(temp_file.name, format = 'mp3')
      audio_file = open(temp_file.name, 'rb')
      client = OpenAI(api_key = config['openai_api_key'])
      transcript = client.audio.transcriptions.create(
        model = "whisper-1",
        file = audio_file,
        language = self.language,
        prompt = ' '.join(self.context)
      )
      length_seconds = len(self.buffer) / 1000
      costs = length_seconds * Transcriber.cost_second
      self.events.costs(costs)
      logger.debug(f'costs: {costs}')
      logger.debug(f'whisper replied: {transcript.text}')
      logger.debug(f'context was: {self.context}')
      self.text_buffer = transcript.text
      self.mark = len(self.buffer)
      return transcript.text

  @slot
  def onResult(self, audio_segment):
    logger.debug(f'received audio of length: {len(audio_segment)}')
    self.buffer += audio_segment
    text = self.transcribeBuffer()
    self.events.result(text)

  @slot
  def onFence(self):
    if len(self.buffer) > 0:
      if len(self.buffer) > self.mark:
        text = self.transcribeBuffer()
      else:
        text = self.text_buffer
      self.context.append(text)
      self.buffer = AudioSegment.empty()
      self.text_buffer = ''
      self.mark = 0
      self.events.result(text)
    self.events.fence()

  @slot
  def onClearBuffer(self):
    self.text_buffer = ''
    self.mark = 0
    self.events.clear_buffer()
