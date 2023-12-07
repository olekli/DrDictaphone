# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from drdictaphone.config import readProfile, makeOutputFilename, getProfilePath
from drdictaphone.microphone import Microphone
from drdictaphone.transcriber import Transcriber
from drdictaphone.chat_gpt import ChatGpt
from drdictaphone.post_processor import PostProcessor
from drdictaphone.output import Output
from drdictaphone.aggregator import Aggregator
from drdictaphone.output_command import OutputCommand
from drdictaphone.cost_counter import CostCounter
from drdictaphone.pipeline import Pipeline
from drdictaphone import logger

logger = logger.get(__name__)

class Main:
  def __init__(self, profile_name):
    profile_path = getProfilePath(profile_name)
    os.utime(profile_path, None)
    self.profile = readProfile(profile_path)

    self.microphone = Microphone()
    self.vad = None
    if self.profile.enable_vad:
      from drdictaphone.static_vad import StaticVad
      self.vad = StaticVad()
    self.transcriber = Transcriber(self.profile.language)
    self.chat_gpt = ChatGpt(self.profile.post_processor)
    self.post_processor = PostProcessor(self.chat_gpt)
    self.output = Output(makeOutputFilename(self.profile.output))
    self.aggregator = Aggregator()
    self.output_command = None
    if self.profile.output_command:
      self.output_command = OutputCommand(self.profile.output_command)
    self.cost_counter = CostCounter()
    self.pipeline = Pipeline(
      [
        self.microphone,
        self.vad,
        self.transcriber,
        self.post_processor,
        self.output,
        self.aggregator,
        self.output_command,
        self.cost_counter
      ]
    )

  async def __aenter__(self):
    await self.pipeline.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    return await self.pipeline.__aexit__(exc_type, exc_value, traceback)
