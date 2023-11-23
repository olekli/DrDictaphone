# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from events import Events
import logger

logger = logger.get(__name__)

class PostProcessor:
  def __init__(self, chat_gpt):
    self.events = Events(('result', 'fence'))
    self.chat_gpt = chat_gpt

    self.text_buffer = [None]
    self.attempts = 0
    self.max_attempts = 3

  def makeText(self):
    return ' '.join([line for line in self.text_buffer if line is not None])

  def onResult(self, text):
    self.text_buffer[-1] = text
    self.events.result(self.makeText())

  def onFence(self):
    text = self.makeText()
    if len(text) > 0:
      self.text_buffer.append(None)
      response = self.chat_gpt.ask(text)
      if 'ok' in response:
        logger.debug(f'post replied: {response}')
        logger.debug(f'input was: {text}')
        self.events.result(response['ok'])
        if ('coherent' in response and response['coherent']) or self.attempts >= self.max_attempts:
          if self.attempts >= self.max_attempts:
            logger.warning(f'accepting incoherent unit of text: {response["ok"]}')
          self.text_buffer = [None]
          self.attempts = 0
          self.events.fence()
        else:
          self.attempts += 1
      else:
        logger.warning(f'post replied with error: {response["err"]}')
        logger.warning(f'input was: {self.text_buffer}')
