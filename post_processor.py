# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from chat_gpt import ChatGpt
from events import Events
import yaml
import logger

logger = logger.get(__name__)

class PostProcessor:
  def __init__(self, chat_gpt):
    self.events = Events(('result', 'fence'))
    self.chat_gpt = chat_gpt

    self.text_buffer = ''

  def onResult(self, text):
    self.text_buffer = text
    self.events.result(text)

  def onFence(self):
    if len(self.text_buffer) > 0:
      response = self.chat_gpt.ask(self.text_buffer)
      if 'ok' in response:
        logger.debug(f'post replied ok: {response["ok"]}')
        logger.debug(f'input was: {self.text_buffer}')
        self.text_buffer = ''
        self.events.result(response['ok'])
      else:
        logger.warning(f'post replied with error: {response["err"]}')
        logger.warning(f'input was: {self.text_buffer}')
      self.events.fence()
