# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import asyncio
from mreventloop import emits, slot, has_event_loop, forwards
from drdictaphone.pipeline_events import PipelineEvents, PipelineSlots
from drdictaphone.model.exchange import Exchange
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
@forwards(PipelineSlots)
@emits('events', PipelineEvents)
class PostProcessor:
  def __init__(self, chat_gpt):
    self.chat_gpt = chat_gpt

    self.text_buffer = []
    self.attempts = 0
    self.max_attempts = 5

  def makeText(self):
    return '\n'.join(self.text_buffer)

  async def tryGpt(self):
    text = self.makeText()
    response = await self.chat_gpt.ask(text)
    self.events.costs_incurred(self.chat_gpt.last_cost)
    self.attempts += 1
    if 'result' in response:
      logger.debug(f'post replied: {response}')
      logger.debug(f'input was: {text}')
      if ('coherent' in response and response['coherent']) or self.attempts >= self.max_attempts:
        if self.attempts >= self.max_attempts:
          logger.warning(f'accepting incoherent unit of text: {response["result"]}')
        self.events.result(response['result'].split('\n'))
        self.text_buffer = []
        self.attempts = 0
      else:
        self.events.error()
    else:
      logger.warning(f'post replied with error: {response["err"]}')
      logger.warning(f'input was: {text}')
      self.events.error()

  @slot
  async def onResult(self, text):
    if not text:
      self.events.result(None)
    else:
      self.text_buffer.append(text)
      await self.tryGpt()

  @slot
  def onClearBuffer(self):
    self.text_buffer = []
    self.attempts = 0
    self.events.clear_buffer()
