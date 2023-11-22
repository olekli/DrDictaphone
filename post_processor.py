# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from chat_gpt import ChatGpt
from model.Conversation import Conversation
from events import Events
import yaml
import logger

logger = logger.get(__name__)

class PostProcessor:
  def __init__(self, context, topic = '', more_pp = False):
    self.context = context
    self.topic = topic
    self.more_pp = more_pp
    self.events = Events(('final_result', 'temporary_result', 'fence'))
    self.text_buffer = []
    self.conversation = Conversation(context = self.context, topic = self.topic, history = [])

    with open('instructions/post_process.yaml', 'rt') as file:
      instructions = yaml.safe_load(file)
    self.context.system = instructions + self.context.system
    self.chat_gpt = ChatGpt()

  def onFinalResult(self, text):
    self.text_buffer.append(text)
    input = ' '.join(self.text_buffer)

    self.events.temporary_result(input)

    if self.more_pp:
      response = self.chat_gpt.ask(self.conversation, input)
      if 'ok' in response:
        logger.debug(f'post replied ok: {response["ok"]}')
        logger.debug(f'input was: {input}')
        self.events.temporary_result(response['ok'])
      else:
        logger.warning(f'post replied with error: {response["err"]}')
        logger.warning(f'input was: {input}')

  def onFence(self):
    if len(self.text_buffer) > 0:
      input = ' '.join(self.text_buffer)
      response = self.chat_gpt.ask(self.conversation, input)
      if 'ok' in response:
        logger.debug(f'post replied ok: {response["ok"]}')
        logger.debug(f'input was: {input}')
        self.text_buffer = []
        self.events.final_result(response['ok'])
      else:
        logger.warning(f'post replied with error: {response["err"]}')
        logger.warning(f'input was: {input}')
      self.events.fence()

  def onTemporaryResult(self, audio_segment):
    assert False
