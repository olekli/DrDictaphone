# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drdictaphone.config import makeOutputFilename
from drdictaphone.audio_feedback import AudioFeedback
from drdictaphone.file_input import FileInput
from drdictaphone.microphone import Microphone
from drdictaphone.transcriber import Transcriber
from drdictaphone.chat_gpt import ChatGpt
from drdictaphone.post_processor import PostProcessor
from drdictaphone.output import Output
from drdictaphone.cost_counter import CostCounter
from drdictaphone.outlet import Outlet
from drdictaphone.pipeline import Pipeline
from drdictaphone import logger

logger = logger.get(__name__)

class ServerPipeline:
  def __init__(self, profile):
    self.profile = profile
    self.audio_feedback = AudioFeedback()
    self.file_input = FileInput()
    self.microphone = Microphone()
    self.vad = None
    if self.profile.enable_vad:
      from drdictaphone.static_vad import StaticVad
      self.vad = StaticVad()
    self.transcriber = Transcriber(self.profile.language)
    self.chat_gpt = ChatGpt(self.profile.post_processor)
    self.post_processor = PostProcessor(self.chat_gpt)
    self.output = None
    if self.profile.output:
      self.output = Output(makeOutputFilename(self.profile.output))
    self.cost_counter = CostCounter()
    self.outlet = Outlet()
    modules = [
      self.audio_feedback,
      self.file_input,
      self.microphone,
      self.vad,
      self.transcriber,
      self.post_processor,
      self.output,
      self.cost_counter,
      self.outlet,
    ]
    self.pipeline = Pipeline(modules)

  async def __aenter__(self):
    await self.pipeline.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    return await self.pipeline.__aexit__(exc_type, exc_value, traceback)
