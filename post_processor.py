# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from pipeline_events import PipelineEvents
from model.exchange import Exchange
import logger

logger = logger.get(__name__)

class PostProcessor:
  def __init__(self, chat_gpt):
    self.events = PipelineEvents()
    self.chat_gpt = chat_gpt

    self.text_buffer = [None]
    self.attempts = 0
    self.max_attempts = 5

    self.history = []

  def makeText(self):
    return ' '.join([line for line in self.text_buffer if line is not None])

  def tryGpt(self, text):
    response = self.chat_gpt.ask(text)
    self.events.costs(self.chat_gpt.last_cost)
    self.attempts += 1
    if 'result' in response:
      logger.debug(f'post replied: {response}')
      logger.debug(f'input was: {text}')
      self.events.result(response['result'])
      if ('coherent' in response and response['coherent']) or self.attempts >= self.max_attempts:
        if self.attempts >= self.max_attempts:
          logger.warning(f'accepting incoherent unit of text: {response["result"]}')
        self.text_buffer = [None]
        self.history.append(Exchange(user_message = text, assistant_message = response['result']))
        self.attempts = 0
        self.events.fence()
        return True
    else:
      logger.warning(f'post replied with error: {response["err"]}')
      logger.warning(f'input was: {text}')
    return False

  def onResult(self, text):
    self.text_buffer[-1] = text
    self.events.result(self.makeText())

  def onFence(self):
    text = self.makeText()
    if len(text) > 0:
      self.text_buffer.append(None)
      self.tryGpt(text)
