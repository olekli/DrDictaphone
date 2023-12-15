# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from mreventloop import emits, slot, has_event_loop
from drdictaphone.pipeline_events import PipelineEvents
from drdictaphone.model.exchange import Exchange
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
@emits('events', PipelineEvents)
class PostProcessor:
  def __init__(self, chat_gpt):
    self.chat_gpt = chat_gpt

    self.text_buffer = [None]
    self.attempts = 0
    self.max_attempts = 5

  def makeText(self):
    return ' '.join([line for line in self.text_buffer if line is not None])

  async def tryGpt(self, text):
    response = await self.chat_gpt.ask(text)
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
        self.attempts = 0
        self.events.fence()
        return True
    else:
      logger.warning(f'post replied with error: {response["err"]}')
      logger.warning(f'input was: {text}')
    return False

  @slot
  def onResult(self, text):
    self.text_buffer[-1] = text
    self.events.result(self.makeText())

  @slot
  async def onFence(self):
    text = self.makeText()
    if len(text) > 0:
      self.text_buffer.append(None)
      await self.tryGpt(text)

  @slot
  def onClearBuffer(self):
    self.text_buffer = [None]
    self.attempts = 0
    self.events.clear_buffer()